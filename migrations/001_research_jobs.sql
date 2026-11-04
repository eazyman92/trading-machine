-- Development research queue only; no user/account authorization yet.
CREATE TABLE IF NOT EXISTS research_jobs (
    id TEXT PRIMARY KEY,
    request_key TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK (status IN ('queued','running','completed','failed','cancelled')),
    config TEXT NOT NULL,
    result TEXT,
    error TEXT,
    created_at DOUBLE PRECISION NOT NULL,
    updated_at DOUBLE PRECISION NOT NULL,
    lease_until DOUBLE PRECISION
);
CREATE INDEX IF NOT EXISTS research_jobs_queue ON research_jobs (created_at, id) WHERE status = 'queued';
