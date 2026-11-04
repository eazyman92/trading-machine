"""Run deterministic synthetic replay without broker access."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT/"src"), str(ROOT/".local-deps")]
import json
from dataclasses import asdict
from tradinglab.replay import fixture, replay

if __name__ == "__main__":
    folder = ROOT/"output"/"replay"
    folder.mkdir(parents=True, exist_ok=True)
    bars = fixture()
    report = replay(bars)
    (folder/"synthetic-bars.json").write_text(json.dumps([asdict(b) for b in bars], default=str, indent=2), encoding="utf-8")
    (folder/"report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"data_kind": report["data_kind"], "trades": len(report["trades"]), "report": str(folder/"report.json")}, indent=2))
