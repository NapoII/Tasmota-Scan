# 🏠 Tasmota Smart Home Control

A powerful Python-based network scanner and web interface for controlling Tasmota smart devices with beautiful liquid glass design.

## ✨ Features

- 🔍 **Automatic Network Discovery** - Scans your local network for Tasmota devices
- 💰 **Energy Cost Calculation** - Tracks power consumption and calculates costs
- 🎨 **Liquid Glass UI** - Modern, responsive web interface with glassmorphism design
- ⚙️ **Configuration System** - Persistent settings with JSON configuration
- 🔄 **Real-time Control** - Toggle devices directly from the web interface
- 📊 **Device Information** - Displays comprehensive device details (IP, MAC, version, WiFi signal)
- 🌐 **CORS-optimized** - Uses no-cors mode for reliable device communication

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- `requests` library
- Network access to Tasmota devices

### Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/tasmota-smart-home-control.git
cd tasmota-smart-home-control
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the scanner:
```bash
python tasmota_scan.py
```

### First Run Setup

On first run, the script will ask for your electricity price:
```
🔧 No configuration found. Setting up electricity price...
💡 Enter your electricity price (EUR/kWh) [default: 0.329]: 
```

This creates a `tasmota_config.json` file that will be used for future runs.

## 📁 Project Structure

```
tasmota-smart-home-control/
├── tasmota_scan.py              # Main scanner script
├── Tasmota_switch_control.html  # Generated web interface
├── tasmota_config.json          # Configuration file (auto-generated)
├── requirements.txt             # Python dependencies
├── README.md                    # This file
└── .gitignore                   # Git ignore rules
```

## 🔧 Configuration

The configuration is stored in `tasmota_config.json`:

```json
{
  "electricity_price": 0.329,
  "created_date": "2025-08-06",
  "last_updated": "2025-08-06"
}
```

To change the electricity price, either:
- Delete the config file and run the script again
- Edit the JSON file directly

## 🖥️ Web Interface

After scanning, the script generates `Tasmota_switch_control.html` with:

- **Device Cards** - Beautiful cards showing each device
- **Toggle Buttons** - Click to control devices
- **Device Information** - IP address, module type, version, WiFi signal
- **Network Statistics** - Total devices found and last update time
- **Responsive Design** - Works on desktop and mobile

### Features of the Web Interface:

- 🎨 **Liquid Glass Design** with animated background
- 📱 **Mobile Responsive** layout
- ⚡ **No-CORS Mode** for reliable device communication
- 🔄 **Iframe Fallback** for maximum compatibility

## 📊 Device Information Display

For each discovered device, the scanner shows:

```
┌────────────────────────────────────────────────────────────┐
│ 🏠 SunSwitch1                                              
├────────────────────────────────────────────────────────────┤
│ 🌐 IP Address:     192.168.2.105                          
│ 📶 MAC Address:    DC:4F:22:XX:XX:XX                       
│ 📱 Module:         0                                       
│ 🔄 Version:        13.2.0                                  
│ ⏱️  Uptime:         0T12:34:56                             
│ 📶 WiFi SSID:      MyNetwork                               
│ 📊 WiFi Signal:    -52 dBm                                 
├────────────────────────────────────────────────────────────┤
│ ⚡ Current Power:   15.2 W                                  
│ 🔌 Voltage:        230.1 V                                 
│ ⚡ Current:         0.066 A                                 
│ 📈 Today:          0.15 kWh - 0.05 EUR                     
│ 📊 Yesterday:      0.25 kWh - 0.08 EUR                     
│ 💰 Total:          125.4 kWh - 41.26 EUR                   
└────────────────────────────────────────────────────────────┘
```

## 🛠️ Technical Details

### Network Scanning
- Scans the local /24 network (254 IP addresses)
- Uses ThreadPoolExecutor for fast parallel scanning
- 1-second timeout per device for quick results

### Device Communication
- Uses Tasmota HTTP API (`/cm?cmnd=` endpoints)
- Status commands for comprehensive device information
- Toggle commands for device control

### Web Interface Technology
- HTML5 + CSS3 with modern features
- JavaScript ES6+ with async/await
- CSS Grid for responsive layout
- Backdrop-filter for glassmorphism effects

## 🔒 Security Notes

- The web interface uses `no-cors` mode to bypass CORS restrictions
- All communication is local network only
- No external dependencies in the generated HTML file

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### No devices found
- Ensure Tasmota devices are on the same network
- Check if devices respond to HTTP requests
- Verify network connectivity

### Web interface not working
- Check browser console for errors
- Ensure devices are accessible via HTTP
- Try the iframe fallback method

### Configuration issues
- Delete `tasmota_config.json` to reset configuration
- Ensure valid JSON format in config file

## 🔗 Related Projects

- [Tasmota](https://tasmota.github.io/docs/) - Open source firmware for smart devices
- [Tasmota Documentation](https://tasmota.github.io/docs/Commands/) - Command reference

## 📊 Supported Tasmota Devices

This tool works with any Tasmota-flashed device that supports:
- HTTP API access
- Status commands
- Power toggle commands

Common devices include:
- Sonoff switches and plugs
- Shelly devices (with Tasmota firmware)
- Custom ESP8266/ESP32 implementations

---

**Made with ❤️ for the smart home community**
