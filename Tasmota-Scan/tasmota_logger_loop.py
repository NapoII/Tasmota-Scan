import time
from pathlib import Path

import tasmota_scan


def _countdown(seconds: int):
    for remaining in range(seconds, 0, -1):
        mins, secs = divmod(remaining, 60)
        # One-line countdown (overwrite same line)
        print(f"⏳ Next scan in: {mins:02d}:{secs:02d}", end="\r", flush=True)
        time.sleep(1)
    print(" " * 60, end="\r", flush=True)


def main(interval_seconds: int = 10 * 60):
    tasmota_scan._ensure_utf8_stdout()

    # Ensure data folder exists (per-device JSON logs)
    Path(tasmota_scan.DATA_DIR).mkdir(parents=True, exist_ok=True)

    print("🔁 Tasmota logger loop started")
    print(f"🕒 Interval: {interval_seconds} seconds (every {interval_seconds // 60} minutes)")
    print("⛔ Stop with Ctrl+C\n")

    while True:
        started = time.time()
        try:
            tasmota_scan.scan_network(plot=False)
        except Exception as exc:
            print(f"⚠️  Scan error: {exc}")

        elapsed = int(time.time() - started)
        wait_for = max(interval_seconds - elapsed, 0)
        _countdown(wait_for)


if __name__ == "__main__":
    main()
