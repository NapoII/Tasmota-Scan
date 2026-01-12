import json
from datetime import datetime
from pathlib import Path


def _safe_float(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        value = value.strip()
        if not value or value.upper() == "N/A":
            return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_iso_ts(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None


def generate_cost_plot_per_device(data_dir: Path, output_png: Path):
    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
    except ImportError:
        print("matplotlib is missing. Install with: pip install -r requirements.txt")
        return None

    if not data_dir.exists():
        print(f"data folder not found: {data_dir}")
        return None

    series_by_device = []  # list of (label, times[], eur[])

    for path in sorted(data_dir.glob("*.json")):
        try:
            device_log = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        dev = device_log.get("device") or {}
        label = dev.get("hostname") or dev.get("name") or path.stem
        baseline_kwh = _safe_float(dev.get("baseline_total_kwh"))
        points = []

        for e in device_log.get("entries") or []:
            ts = _parse_iso_ts(e.get("ts"))
            if ts is None:
                continue
            cost_since = _safe_float(e.get("cost_since_first_seen_eur"))
            if cost_since is None:
                total_kwh = _safe_float(e.get("total_kwh"))
                price = _safe_float(e.get("price_eur_per_kwh"))
                if baseline_kwh is not None and total_kwh is not None and price is not None:
                    cost_since = max(total_kwh - baseline_kwh, 0.0) * price

            if cost_since is None:
                continue

            points.append((ts, cost_since))

        if not points:
            continue

        points.sort(key=lambda x: x[0])
        times = [p[0] for p in points]
        eur = [p[1] for p in points]
        series_by_device.append((str(label), times, eur))

    if not series_by_device:
        print(f"No plottable cost data in: {data_dir}")
        return None

    fig, ax = plt.subplots(figsize=(12, 6))
    for label, times, eur in series_by_device:
        ax.plot(times, eur, linewidth=2, label=label)

    ax.set_ylabel("EUR")
    ax.set_title("Tasmota: Cost (EUR) over time")
    ax.grid(True, alpha=0.25)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
    fig.autofmt_xdate(rotation=30, ha="right")
    ax.legend(loc="upper left")

    output_png.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_png, dpi=150)
    print(f"Plot saved: {output_png}")

    try:
        plt.show()
    except Exception:
        pass

    return output_png


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    data_dir = root / "data"
    out = root / "tasmota_cost_plot.png"
    generate_cost_plot_per_device(data_dir, out)
