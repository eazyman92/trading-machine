"""Durable development queue. PostgreSQL in Compose; SQLite for local checks."""
import json
import os
from pathlib import Path
import sqlite3
import time
import uuid
from contextlib import contextmanager

class Conflict(Exception):
    pass

class Store:
    def __init__(self, url=None):
        self.url = url or os.environ.get('DATABASE_URL', 'sqlite:///output/research.db')
        self.pg = self.url.startswith('postgresql://')

    @contextmanager
    def connection(self):
        if self.pg:
            import psycopg
            from psycopg.rows import dict_row
            conn = psycopg.connect(self.url, row_factory=dict_row, connect_timeout=5)
        else:
            path = self.url.removeprefix('sqlite:///')
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(path, timeout=5)
            conn.row_factory = sqlite3.Row
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def sql(self, conn, query, args=()):
        return conn.execute(query.replace('?', '%s') if self.pg else query, args)

    def migrate(self):
        script = (Path(__file__).resolve().parents[2]/'migrations/001_research_jobs.sql').read_text()
        script = '\n'.join(line for line in script.splitlines() if not line.lstrip().startswith('--'))
        with self.connection() as conn:
            for statement in script.split(';'):
                if statement.strip(): conn.execute(statement)

    def health(self):
        with self.connection() as conn:
            conn.execute('SELECT id FROM research_jobs LIMIT 1')

    def create(self, key, config):
        encoded = json.dumps(config, sort_keys=True)
        now = time.time()
        with self.connection() as conn:
            self.sql(conn, 'INSERT INTO research_jobs (id,request_key,status,config,created_at,updated_at) VALUES (?,?,?,?,?,?) ON CONFLICT(request_key) DO NOTHING',
                     (str(uuid.uuid4()), key, 'queued', encoded, now, now))
            row = dict(self.sql(conn, 'SELECT * FROM research_jobs WHERE request_key=?', (key,)).fetchone())
            if row['config'] != encoded: raise Conflict('Idempotency key already used with a different configuration')
            return self.decode(row)

    def decode(self, row):
        result = dict(row)
        for name in ('config', 'result'):
            if result[name] is not None: result[name] = json.loads(result[name])
        result.pop('request_key', None)
        result.pop('lease_until', None)
        return result

    def get(self, job_id):
        with self.connection() as conn:
            row = self.sql(conn, 'SELECT * FROM research_jobs WHERE id=?', (job_id,)).fetchone()
            return self.decode(row) if row else None

    def get_by_request(self, key):
        with self.connection() as conn:
            row=self.sql(conn,'SELECT * FROM research_jobs WHERE request_key=?',(key,)).fetchone()
            return self.decode(row) if row else None

    def list_jobs(self, limit=20, offset=0):
        with self.connection() as conn:
            rows = self.sql(conn, 'SELECT id,status,config,error,created_at,updated_at FROM research_jobs ORDER BY created_at DESC,id DESC LIMIT ? OFFSET ?', (limit+1, offset)).fetchall()
            items = [dict(row) for row in rows[:limit]]
            for item in items: item['config'] = json.loads(item['config'])
            return {'items': items, 'next_offset': offset+limit if len(rows)>limit else None}

    def cancel(self, job_id):
        with self.connection() as conn:
            self.sql(conn, "UPDATE research_jobs SET status='cancelled',updated_at=?,lease_until=NULL WHERE id=? AND status IN ('queued','running')", (time.time(), job_id))
        return self.get(job_id)

    def claim(self):
        now = time.time()
        with self.connection() as conn:
            if not self.pg: conn.execute('BEGIN IMMEDIATE')
            # Expired work is failed, not silently re-executed. Research jobs can be resubmitted with a new key.
            self.sql(conn, "UPDATE research_jobs SET status='failed',error='worker_lease_expired',updated_at=?,lease_until=NULL WHERE status='running' AND lease_until<?", (now, now))
            query = "SELECT * FROM research_jobs WHERE status='queued' ORDER BY created_at,id LIMIT 1"
            if self.pg: query += ' FOR UPDATE SKIP LOCKED'
            row = self.sql(conn, query).fetchone()
            if not row: return None
            self.sql(conn, "UPDATE research_jobs SET status='running',updated_at=?,lease_until=? WHERE id=?", (now, now+60, row['id']))
            return self.decode(row)

    def finish(self, job_id, result=None, error=None):
        with self.connection() as conn:
            self.sql(conn, "UPDATE research_jobs SET status=?,result=?,error=?,updated_at=?,lease_until=NULL WHERE id=? AND status='running' AND lease_until>=?",
                     ('failed' if error else 'completed', json.dumps(result) if result else None, error, time.time(), job_id, time.time()))

    def heartbeat(self,job_id,progress=None):
        now=time.time()
        with self.connection() as conn:
            if progress is None:
                cursor=self.sql(conn,"UPDATE research_jobs SET lease_until=? WHERE id=? AND status='running' AND lease_until>=?",(now+60,job_id,now))
            else:
                cursor=self.sql(conn,"UPDATE research_jobs SET lease_until=?,updated_at=?,result=? WHERE id=? AND status='running' AND lease_until>=?",(now+60,now,json.dumps({'progress':progress}),job_id,now))
            return cursor.rowcount==1

if __name__ == '__main__':
    Store().migrate()
    print('Research schema initialized')
