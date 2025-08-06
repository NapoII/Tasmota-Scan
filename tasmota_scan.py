import requests
import ipaddress
import socket
import json
import os
from concurrent.futures import ThreadPoolExecutor

def load_or_create_config():
    """Loads configuration from JSON file or creates new one by asking user"""
    config_file = "tasmota_config.json"
    
    # Try to load existing config
    if os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                print(f"✅ Configuration loaded: {config['electricity_price']} EUR/kWh")
                return config
        except (json.JSONDecodeError, KeyError) as e:
            print(f"⚠️ Config file corrupted, creating new one...")
    
    # Create new config by asking user
    print("🔧 No configuration found. Setting up electricity price...")
    while True:
        try:
            price_input = input("💡 Enter your electricity price (EUR/kWh) [default: 0.329]: ").strip()
            
            if not price_input:
                electricity_price = 0.329
                break
            
            electricity_price = float(price_input)
            if electricity_price <= 0:
                print("❌ Price must be greater than 0")
                continue
            break
            
        except ValueError:
            print("❌ Please enter a valid number")
    
    # Create config
    config = {
        "electricity_price": electricity_price,
        "created_date": "2025-08-06",
        "last_updated": "2025-08-06"
    }
    
    # Save config to file
    try:
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"✅ Configuration saved: {electricity_price} EUR/kWh")
    except Exception as e:
        print(f"⚠️ Could not save config: {e}")
    
    return config

def get_local_network():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    ip_parts = local_ip.split('.')
    network_prefix = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}."
    return network_prefix

def check_tasmota(ip):
    url = f"http://{ip}/"
    try:
        response = requests.get(url, timeout=1)
        if "Tasmota" in response.text:
            print(f"🔍 Tasmota device found: http://{ip}")
            return ip
    except requests.RequestException:
        pass
    return None

def get_device_info(ip):
    """Retrieves comprehensive device information"""
    info_url = f"http://{ip}/cm?cmnd=Status%200"
    status_url = f"http://{ip}/cm?cmnd=Status%205"
    wifi_url = f"http://{ip}/cm?cmnd=Status%2011"
    
    device_info = {
        'name': f"Unknown ({ip})",
        'version': 'N/A',
        'uptime': 'N/A',
        'wifi_ssid': 'N/A',
        'wifi_rssi': 'N/A',
        'ip': ip,
        'mac': 'N/A',
        'module': 'N/A'
    }
    
    try:
        # Basic information
        response = requests.get(info_url, timeout=2)
        data = response.json()
        status = data.get("Status", {})
        
        device_info['name'] = status.get("DeviceName", f"Unknown ({ip})")
        friendly_name = status.get("FriendlyName", [""])[0]
        if friendly_name:
            device_info['name'] = friendly_name
        
        device_info['version'] = status.get("Version", 'N/A')
        device_info['module'] = status.get("Module", 'N/A')
        
        # Network information
        net_response = requests.get(status_url, timeout=2)
        net_data = net_response.json()
        net_status = net_data.get("StatusNET", {})
        
        device_info['mac'] = net_status.get("Mac", 'N/A')
        
        # WiFi information
        wifi_response = requests.get(wifi_url, timeout=2)
        wifi_data = wifi_response.json()
        wifi_status = wifi_data.get("StatusSTS", {})
        
        device_info['wifi_ssid'] = wifi_status.get("Wifi", {}).get("SSId", 'N/A')
        device_info['wifi_rssi'] = wifi_status.get("Wifi", {}).get("RSSI", 'N/A')
        device_info['uptime'] = wifi_status.get("Uptime", 'N/A')
        
    except requests.RequestException:
        pass
    
    return device_info

def get_energy_data(ip):
    """Retrieves detailed energy data"""
    url = f"http://{ip}/cm?cmnd=Status%208"
    energy_data = {
        'total': 'N/A',
        'power': 'N/A',
        'voltage': 'N/A',
        'current': 'N/A',
        'today': 'N/A',
        'yesterday': 'N/A'
    }
    
    try:
        response = requests.get(url, timeout=2)
        data = response.json()
        energy = data.get("StatusSNS", {}).get("ENERGY", {})
        
        energy_data['total'] = energy.get("Total", "N/A")
        energy_data['power'] = energy.get("Power", "N/A")
        energy_data['voltage'] = energy.get("Voltage", "N/A")
        energy_data['current'] = energy.get("Current", "N/A")
        energy_data['today'] = energy.get("Today", "N/A")
        energy_data['yesterday'] = energy.get("Yesterday", "N/A")
        
    except requests.RequestException:
        pass
    
    return energy_data

def print_device_details(device_info, energy_data, price_per_kwh):
    """Prints detailed device information"""
    print(f"\n┌{'─' * 60}┐")
    print(f"│ 🏠 {device_info['name']:<56}")
    print(f"├{'─' * 60}┤")
    print(f"│ 🌐 IP Address:     {device_info['ip']:<41}")
    print(f"│ 📶 MAC Address:    {device_info['mac']:<41}")
    print(f"│ 📱 Module:         {device_info['module']:<41}")
    print(f"│ 🔄 Version:        {device_info['version']:<41}")
    print(f"│ ⏱️  Uptime:         {device_info['uptime']:<41}")
    print(f"│ 📶 WiFi SSID:      {device_info['wifi_ssid']:<41}")
    print(f"│ 📊 WiFi Signal:    {device_info['wifi_rssi']} dBm{'':<37}")
    print(f"├{'─' * 60}┤")
    
    if energy_data['total'] != 'N/A':
        cost_total = float(energy_data['total']) * price_per_kwh if energy_data['total'] != 'N/A' else 0
        cost_today = float(energy_data['today']) * price_per_kwh if energy_data['today'] != 'N/A' else 0
        cost_yesterday = float(energy_data['yesterday']) * price_per_kwh if energy_data['yesterday'] != 'N/A' else 0
        
        print(f"│ ⚡ Current Power:   {energy_data['power']} W{'':<35}")
        print(f"│ 🔌 Voltage:        {energy_data['voltage']} V{'':<35}")
        print(f"│ ⚡ Current:         {energy_data['current']} A{'':<35}")
        print(f"│ 📈 Today:          {energy_data['today']} kWh - {cost_today:.2f} EUR{'':<22}")
        print(f"│ 📊 Yesterday:      {energy_data['yesterday']} kWh - {cost_yesterday:.2f} EUR{'':<22}")
        print(f"│ 💰 Total:          {energy_data['total']} kWh - {cost_total:.2f} EUR{'':<22}")
        print(f"└{'─' * 60}┘")
        return cost_total
    else:
        print(f"│ ⚠️  Energy Data:     Not available{'':<31}")
        print(f"└{'─' * 60}┘")
        return 0

def generate_html_file(devices_data):
    """Generates a new HTML file with the found devices"""
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>🏠 Tasmota Smart Home Control</title>
  <style>
    /* Liquid Glass Design */
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      padding: 20px;
      position: relative;
      overflow-x: hidden;
    }

    /* Animated background bubbles */
    body::before {
      content: '';
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
                  radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
                  radial-gradient(circle at 40% 80%, rgba(119, 198, 255, 0.3) 0%, transparent 50%);
      animation: float 6s ease-in-out infinite;
      pointer-events: none;
      z-index: -1;
    }

    @keyframes float {
      0%, 100% { transform: translateY(0px) rotate(0deg); }
      50% { transform: translateY(-20px) rotate(180deg); }
    }

    .container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 20px;
    }

    .header {
      text-align: center;
      margin-bottom: 40px;
      background: rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(20px);
      border: 1px solid rgba(255, 255, 255, 0.2);
      border-radius: 24px;
      padding: 30px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }

    .header h1 {
      font-size: 3rem;
      font-weight: 700;
      background: linear-gradient(135deg, #fff 0%, #f0f0f0 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      margin-bottom: 10px;
    }

    .header p {
      color: rgba(255, 255, 255, 0.8);
      font-size: 1.2rem;
      font-weight: 300;
    }

    .devices-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
      gap: 20px;
      margin-bottom: 30px;
    }

    .device-card {
      background: rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(20px);
      border: 1px solid rgba(255, 255, 255, 0.2);
      border-radius: 20px;
      padding: 25px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
      position: relative;
      overflow: hidden;
    }

    .device-name {
      font-size: 1.4rem;
      font-weight: 600;
      color: white;
      margin-bottom: 15px;
      text-align: center;
    }

    .device-info {
      color: rgba(255, 255, 255, 0.8);
      font-size: 0.9rem;
      margin-bottom: 20px;
      line-height: 1.5;
    }

    .switch-button {
      width: 100%;
      padding: 15px;
      font-size: 1.1rem;
      font-weight: 600;
      border: none;
      border-radius: 15px;
      cursor: pointer;
      position: relative;
      text-transform: uppercase;
      letter-spacing: 1px;
      background: linear-gradient(135deg, #667eea, #764ba2);
      color: white;
      box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
      border: 2px solid rgba(102, 126, 234, 0.6);
      transition: all 0.3s ease;
    }

    .switch-button:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 20px rgba(102, 126, 234, 0.6);
    }

    .switch-button:active {
      transform: translateY(0px);
    }

    .stats-card {
      background: rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(20px);
      border: 1px solid rgba(255, 255, 255, 0.2);
      border-radius: 20px;
      padding: 25px;
      text-align: center;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
      margin-top: 20px;
    }

    .stats-title {
      font-size: 1.5rem;
      font-weight: 600;
      color: white;
      margin-bottom: 15px;
    }

    .stats-content {
      color: rgba(255, 255, 255, 0.8);
      font-size: 1rem;
      line-height: 1.6;
    }

    .loading {
      opacity: 0.7;
      pointer-events: none;
    }

    @media (max-width: 768px) {
      .devices-grid {
        grid-template-columns: 1fr;
      }
      
      .header h1 {
        font-size: 2rem;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🏠 Smart Home Control</h1>
      <p>Tasmota Device Control with Automatic Discovery</p>
    </div>

    <div class="devices-grid" id="devicesGrid">
'''
    
    # Generate device cards
    for i, device in enumerate(devices_data, 1):
        html_content += f'''
      <div class="device-card">
        <div class="device-name">🔌 {device['name']}</div>
        <div class="device-info">
          🌐 IP: {device['ip']}<br>
          📱 Module: {device['module']}<br>
          🔄 Version: {device['version']}<br>
          📶 WiFi: {device['wifi_rssi']} dBm
        </div>
        <button
          id="button{i}"
          class="switch-button"
          onclick="toggleSwitch('http://{device['ip']}/cm?cmnd=Power Toggle', 'button{i}');"
        >
          Toggle Switch
        </button>
      </div>'''
    
    html_content += f'''
    </div>

    <div class="stats-card">
      <div class="stats-title">📊 Network Statistics</div>
      <div class="stats-content">
        <strong>{len(devices_data)}</strong> Tasmota devices found<br>
        Last update: <span id="lastUpdate"></span>
      </div>
    </div>
  </div>

  <script>
    // Display current time
    document.getElementById('lastUpdate').textContent = new Date().toLocaleString('en-US');

    // Simple toggle function without status tracking
    async function toggleSwitch(url, buttonId) {{
      const button = document.getElementById(buttonId);
      
      console.log(`🔄 Toggle for ${{buttonId}}: ${{url}}`);
      
      try {{
        // Use No-CORS mode for toggle commands
        const response = await fetch(url, {{ mode: 'no-cors' }});
        console.log(`✅ Toggle for ${{buttonId}} sent`);
        
      }} catch (error) {{
        console.log(`❌ Toggle failed for ${{buttonId}}:`, error.message);
        
        // Fallback: Iframe method
        const iframe = document.createElement('iframe');
        iframe.style.display = 'none';
        iframe.src = url;
        iframe.onload = iframe.onerror = () => {{
          console.log(`📡 Iframe toggle for ${{buttonId}} executed`);
          document.body.removeChild(iframe);
        }};
        document.body.appendChild(iframe);
      }}
    }}
  </script>
</body>
</html>'''
    
    with open("Tasmota_switch_control.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"\n✅ HTML file 'Tasmota_switch_control.html' successfully generated!")

def scan_network():
    # Load configuration first
    config = load_or_create_config()
    electricity_price = config['electricity_price']
    
    network_prefix = get_local_network()
    print(f"🔍 Scanning network: {network_prefix}0/24")
    
    ips_to_check = [f"{network_prefix}{i}" for i in range(1, 255)]
    
    devices = []
    total_cost = 0
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(check_tasmota, ips_to_check))
    
    tasmota_devices = [ip for ip in results if ip is not None]
    
    if tasmota_devices:
        print(f"\n🎉 Found {len(tasmota_devices)} Tasmota devices!")
        
        for ip in tasmota_devices:
            device_info = get_device_info(ip)
            energy_data = get_energy_data(ip)
            cost = print_device_details(device_info, energy_data, electricity_price)
            total_cost += cost
            devices.append(device_info)
        
        print(f"\n{'═' * 62}")
        print(f"📊 SUMMARY")
        print(f"{'═' * 62}")
        print(f"│ 🏠 Total devices found:    {len(tasmota_devices):<31}")
        if total_cost > 0:
            print(f"│ 💰 Total energy costs:     {total_cost:.2f} EUR{'':<21}")
            print(f"│ ⚡ Electricity price:      {electricity_price} EUR/kWh{'':<21}")
        print(f"└{'─' * 60}┘")
        
        # Generate HTML file
        generate_html_file(devices)
    else:
        print("\n❌ No Tasmota devices found on the network.")

if __name__ == "__main__":
    scan_network()
