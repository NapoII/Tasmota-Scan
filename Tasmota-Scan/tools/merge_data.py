from __future__ import annotations

import json
from pathlib import Path

import tasmota_scan

# -----------------------------------------------------------------------------
# USER CONFIG (hard-coded paths)
# - file_1: main file (merge target)
# - file_2: source file (will be deleted AFTER successful merge/write)
# -----------------------------------------------------------------------------

file_1 = Path(r"C:\Users\space\Documents\Tasmota-Scan\Tasmota-Scan\data\PC__543204F66320.json")
file_2 = Path(r"C:\Users\space\Documents\Tasmota-Scan\Tasmota-Scan\data\PC.json")


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {
            "schema_version": 1,
            "price_eur_per_kwh_default": 0.329,
            "device": {},
            "entries": [],
        }
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json_atomic(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    tmp.replace(path)


def main() -> int:
    # Resolve relative paths against repo root (folder above this script).
    repo_root = Path(__file__).resolve().parent.parent
    p1 = (repo_root / file_1).resolve() if not file_1.is_absolute() else file_1
    p2 = (repo_root / file_2).resolve() if not file_2.is_absolute() else file_2

    if not p2.exists():
        print(f"❌ file_2 not found: {p2}")
        return 2

    if p1.resolve() == p2.resolve():
        print("❌ file_1 and file_2 are the same path")
        return 2

    try:
        main_data = _read_json(p1)
        other_data = _read_json(p2)

        tasmota_scan._merge_device_logs(main_data, other_data)
        _write_json_atomic(p1, main_data)

        # Only delete after successful write.
        p2.unlink()
        print(f"✅ Merged into: {p1}")
        print(f"🗑️  Deleted source: {p2}")
        return 0
    except Exception as exc:
        print(f"❌ Merge failed: {exc}")
        print("ℹ️  Source file was NOT deleted.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
