"""Local fallback: same API/worker with SQLite; no Docker required."""
import os
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent
os.environ['PYTHONPATH'] = os.pathsep.join([str(root/'src'), str(root/'.local-deps')])
sys.path[:0] = [str(root/'src'), str(root/'.local-deps')]

if __name__ == '__main__':
    from tradinglab.store import Store
    Store().migrate()
    # Same-origin static hosting for this loopback-only fallback.
    import uvicorn
    from fastapi.staticfiles import StaticFiles
    from tradinglab.api import app
    app.mount('/', StaticFiles(directory=root/'prototype/dist', html=True), name='web')
    worker = subprocess.Popen([sys.executable, '-m', 'tradinglab.worker'], cwd=root)
    try: uvicorn.run(app, host='127.0.0.1', port=int(os.environ.get('PORT', '4173')))
    finally:
        worker.terminate()
        worker.wait(timeout=10)
