# Trading research platform

Early development: a sample-data web workspace and backend-connected synthetic research lab. Python API and worker, PostgreSQL in Docker Compose, and a paper-only Rust validator under development. No broker or LLM is connected; no real orders are enabled.

## Start development

See [DEVELOPMENT.md](DEVELOPMENT.md) for Docker Compose and local Python setup, verification results and limitations.

For Git Bash push commands, EC2 startup, the HTTP smoke test and private SSH-tunnel access, follow [EC2-TEST.md](EC2-TEST.md). GitHub Actions checks are defined for Python, Rust and Compose; remote results remain pending until the repository is pushed.

With Docker/Compose available, copy `.env.example` to `.env`, set a random URL-safe `POSTGRES_PASSWORD`, then run:

```sh
docker compose config --quiet
docker compose up --build
```

Open `http://127.0.0.1:4173/#research`. The published port binds only to loopback. For an EC2 development test, keep it private and access it through an SSH tunnel; do not expose the unauthenticated API publicly.

```sh
ssh -i /path/to/key.pem -L 4173:127.0.0.1:4173 EC2_USER@EC2_HOST
```

Run that SSH command on your own computer, substituting your key, instance user and host. Then open the local address above. This is a development test, not a production deployment. Docker images and the PostgreSQL runtime path have not yet been verified on the development machine.

## Project references

- [Roadmap](ROADMAP.md): milestones and acceptance gates.
- [Work queue](WORK-QUEUE.md): next tasks and known blockers.
- [Architecture](SYSTEM-BLUEPRINT.md): responsibilities and build/reuse decisions.
- [Engineering requirements](ENGINEERING-REQUIREMENTS.md): execution, data and account controls.
- [Gold research import](GOLD-RESEARCH.md): XAU/USD CSV format, contract assumptions, test sample and deployment steps.
- [Actual market-data adapter](MARKET-DATA-ADAPTER.md): acquired provider sample, offline reproduction and qualification limits.
- [Upstream strategy reproduction and EC2 acceptance](UPSTREAM-REPRODUCTION.md): exact reference parity, license, commands, inputs and expected results.

Generated output, local dependencies, environment files and downloaded third-party research source snapshots are excluded from Git. Research notes and the source manifest remain included. No project-wide open-source license has been selected; third-party components retain their own licenses.
