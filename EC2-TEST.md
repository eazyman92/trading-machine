# First EC2 development test

Use Git Bash locally and a Linux shell on EC2. Docker Engine and the Compose v2 plugin must already be installed and running on the instance. This guide does not create billable AWS resources, install Docker or change firewall rules.

## Push from Git Bash

Create an empty private GitHub repository first, then substitute its URL below:

```bash
cd /c/Users/tijan/OneDrive/Documents/ChatGPT/trading-machine
git add .
git diff --cached --stat
git commit -m "Initialize containerized trading research platform and automated checks"
git branch -M main
git remote add origin https://github.com/YOUR_OWNER/YOUR_REPO.git
git push -u origin main
```

If origin already exists, inspect `git remote -v` before changing it. Use your normal GitHub authentication; never paste tokens into chat or put them in the remote URL. GitHub Actions will attempt the Python, Rust and Compose jobs after the push. A workflow file existing does not mean its checks have passed.

## Start on the instance

Authenticate to the private repository using your chosen GitHub access method, then:

```bash
git clone https://github.com/YOUR_OWNER/YOUR_REPO.git trading-machine
cd trading-machine
docker --version
docker compose version
python3 -c 'import secrets; from pathlib import Path; p=Path(".env"); p.open("x").write("POSTGRES_PASSWORD=" + secrets.token_hex(24) + "\n")'
chmod 600 .env
docker compose config --quiet
docker compose up --build -d --wait --wait-timeout 180
docker compose ps -a
python3 scripts/smoke_research.py
```

The environment-file command refuses to overwrite an existing `.env`. Preserve the database password when reusing its volume. The smoke test creates synthetic research records; it never submits broker orders. Successful output is a `PASS` line followed by a job ID and dataset hash.

If startup or the check fails:

```bash
docker compose ps -a
docker compose logs --tail=100 api worker migrate web
```

Read logs locally and redact secrets before sharing. Keep the EC2 security group limited to SSH from your own IP; do not open port 4173, 8000 or 5432 to the Internet. This application has no authentication yet.

## View it from your computer

Run in a separate local Git Bash window, replacing the key path, instance username and host:

```bash
ssh -i /c/path/to/key.pem -N -L 4173:127.0.0.1:4173 EC2_USER@EC2_HOST
```

Open `http://127.0.0.1:4173/#research` locally. If local port 4173 is occupied, use `-L 4174:127.0.0.1:4173` and open port 4174 instead. Leave the tunnel open while testing.

## Stop or update

```bash
docker compose down
# For a later code update:
git pull --ff-only
docker compose up --build -d --wait --wait-timeout 180
python3 scripts/smoke_research.py
```

`down` preserves database storage. Do not add `-v` unless intentionally deleting the data. Stopping containers does not stop AWS instance/storage charges; manage the instance lifecycle separately. This is a development validation path, not a production release.
