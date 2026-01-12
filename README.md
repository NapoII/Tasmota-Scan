# ⚡ Tasmota Network Scanner + Cost Logger

Tiny scripts to scan your LAN for **Tasmota** devices, log energy stats, and (optionally) plot **cost over time**.

## ✨ What it does

- 🔎 Scans your local network for Tasmota devices
- 📡 Fetches telemetry: `Status 8` (ENERGY) + `State` (POWER/WiFi/Hostname)
- 🗂️ Writes **one JSON file per device** into `data/`
- 📈 Optional: generates a cost plot (one line per device)

## ✅ Requirements

- Python 3.10+ recommended

Install dependencies:

```bash
pip install -r requirements.txt
```

## 🚀 Quick start

### 1) One-time scan

Runs a single scan, stores/updates JSON logs in `data/`, and (by default) creates a PNG plot.

```bash
python tasmota_scan.py
```

Output:

- Per-device JSON logs: `data/<hostname>__<mac>.json`
- Cost plot: `tasmota_cost_plot.png`

### 2) Continuous logging (every 10 minutes)

Runs `scan_network()` every 10 minutes and prints a one-line countdown.

```bash
python tasmota_logger_loop.py
```

Note: the loop does **not** create plots (it only scans + stores values).

### 3) Plot from existing data

Generate a single plot: **X = time**, **Y = EUR**, **one line per device**.

```bash
python plot_tasmota_logs.py
```

## 🧾 Data format

Each device is stored in its own file:

- `data/<hostname>__<mac>.json`

The file contains:

- `device`: metadata (hostname, mac, first_seen, baseline_total_kwh, ...)
- `entries`: snapshots with timestamps and computed costs (`cost_since_first_seen_eur`)

## 🔧 Tasmota console / HTTP commands (kept for reference)

### Reset energy values (console)

Reset today's energy:

```text
EnergyToday 0
```

Reset yesterday:

```text
EnergyYesterday 0
```

Reset total energy (warning: resets the main counter):

```text
EnergyTotal 0
Restart 1
```

### Device settings

Set hostname:

```text
Hostname MeinSmartSwitch
```

Set Friendly Name:

```text
FriendlyName1 Wohnzimmer Lampe
```

### Configure toggle button

Enable toggle button (physical button toggles relay):

```text
SwitchMode1 0
```

Disable toggle button:

```text
SwitchMode1 1
FriendlyName1 MeinSmartSwitch
```

### HTTP URLs (web requests)

Switch ON:

```text
http://<IP-Adresse>/cm?cmnd=Power%20On
```

Switch OFF:

```text
http://<IP-Adresse>/cm?cmnd=Power%20Off
```

Switch TOGGLE:

```text
http://<IP-Adresse>/cm?cmnd=Power%20Toggle
```

---

## 🖥️ Web UI (Switch Control)

Open the file in your browser:

- `Tasmota_switch_control.html`

Edit the IP list inside the file (search for `DEVICES`). The UI will automatically fetch each device hostname via `cm?cmnd=State` and use it as the button label.
