"""Fetch pinned public strategy sources for inspection; never execute upstream code."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent / "sources"
REPOS = {
    "freqtrade/freqtrade": ["README.md", "LICENSE"],
    "freqtrade/freqtrade-strategies": ["README.md", "LICENSE"],
    "iterativv/NostalgiaForInfinity": ["README.md", "LICENSE", "NostalgiaForInfinityX8.py"],
    "nautechsystems/nautilus_trader": ["README.md", "LICENSE"],
    "je-suis-tm/quant-trading": ["README.md", "LICENSE", "London Breakout backtest.py"],
    "pst-group/pysystemtrade": ["README.md", "LICENSE", "systems/provided/rules/ewmac.py", "systems/provided/rules/breakout.py"],
}


def fetch(url):
    request = Request(url, headers={"User-Agent": "trading-platform-source-review", "Accept": "application/vnd.github+json"})
    with urlopen(request, timeout=30) as response:
        return response.read()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", choices=REPOS)
    args = parser.parse_args()
    ROOT.mkdir(parents=True, exist_ok=True)
    manifest_path = ROOT / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if args.only and manifest_path.exists() else {"retrieved_at": datetime.now(timezone.utc).isoformat(), "repositories": []}
    for repo, paths in REPOS.items():
        if args.only and repo != args.only:
            continue
        record = {"repository": repo, "retrieved_at": datetime.now(timezone.utc).isoformat(), "files": []}
        try:
            metadata = json.loads(fetch(f"https://api.github.com/repos/{repo}"))
            branch = metadata["default_branch"]
            commit = json.loads(fetch(f"https://api.github.com/repos/{repo}/commits/{branch}"))["sha"]
            record.update(commit=commit, default_branch=branch, license=(metadata.get("license") or {}).get("spdx_id"), stars=metadata["stargazers_count"], pushed_at=metadata["pushed_at"])
            destination = ROOT / repo.replace("/", "__")
            destination.mkdir(exist_ok=True)
            for path in paths:
                url = f"https://raw.githubusercontent.com/{repo}/{commit}/{path.replace(' ', '%20')}"
                item = {"path": path, "url": url}
                try:
                    data = fetch(url)
                    output = destination / path
                    output.parent.mkdir(parents=True, exist_ok=True)
                    output.write_bytes(data)
                    item.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
                except Exception as exc:
                    item["error"] = str(exc)
                record["files"].append(item)
        except Exception as exc:
            record["error"] = str(exc)
        manifest["repositories"] = [item for item in manifest["repositories"] if item["repository"] != repo]
        manifest["repositories"].append(record)
        print(repo, record.get("commit", record.get("error")), flush=True)
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
