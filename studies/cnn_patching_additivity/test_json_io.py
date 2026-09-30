import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import evaluate as ev

payload = {
    "study": "bom-smoke",
    "unicode": "áéíóú",
    "nested": {"ok": True, "n": 3},
}

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    plain = root / "plain.json"
    bom = root / "bom.json"

    plain.write_text(json.dumps(payload), encoding="utf-8")
    bom.write_text(json.dumps(payload), encoding="utf-8-sig")

    assert ev.read_json(plain) == payload
    assert ev.read_json(bom) == payload

print("BOM-safe JSON reader test PASS")
