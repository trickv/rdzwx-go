# TTGO Simulator

A Python-based simulator for testing the rdzwx-go app without physical TTGO ESP32 hardware.

## Features

- ✅ **mDNS/Bonjour advertising** as `_jsonrdz._tcp.` service for auto-discovery
- ✅ **TCP server** on configurable port (default: 12345)
- ✅ **Bidirectional JSON protocol** - accepts GPS updates from app
- ✅ **Realistic balloon flight playback** with configurable speed
- ✅ **Multiple data sources**: built-in sample, JSON files, or CSV files
- ✅ **Multi-client support** - broadcast to multiple connected apps
- ✅ **Looping mode** for continuous testing

## Installation

Install Python dependencies:

```bash
pip install zeroconf
```

Or use the requirements file:

```bash
pip install -r simulator-requirements.txt
```

## Quick Start

Run with built-in sample flight:

```bash
./ttgo_simulator.py
```

The simulator will:
1. Advertise itself via mDNS as "TTGO Simulator"
2. Listen for connections on port 12345
3. Start streaming balloon telemetry data

## Usage Examples

### Use custom flight data

```bash
# From CSV file
./ttgo_simulator.py --flight my_flight.csv

# From JSON file
./ttgo_simulator.py --flight my_flight.json
```

### Adjust playback speed

```bash
# 2x speed (twice as fast)
./ttgo_simulator.py --speed 2.0

# 0.5x speed (half speed, slow motion)
./ttgo_simulator.py --speed 0.5
```

### Loop flight indefinitely

```bash
./ttgo_simulator.py --loop
```

### Custom port and service name

```bash
./ttgo_simulator.py --port 9999 --name "Test Balloon"
```

### Change sonde ID and type

```bash
./ttgo_simulator.py --id "S1234567" --type "DFM09"
```

### Combined example

```bash
./ttgo_simulator.py --flight real_flight.csv --speed 5.0 --loop --name "High Altitude Test"
```

## Data Formats

### CSV Format

CSV files must have these columns:

- **Required**: `time`, `lat`, `lon`, `alt`
- **Optional**: `temp`, `humidity`, `pressure`, `climb`

Example `sample_flight.csv`:

```csv
time,lat,lon,alt,temp,humidity,pressure,climb
0,48.5024,11.9271,500,15.2,65,954.3,5.2
10,48.5028,11.9275,552,14.8,64,948.1,5.3
20,48.5032,11.9280,605,14.3,63,941.8,5.1
```

### JSON Format

JSON files can be either:

**Array format:**
```json
[
  {"time": 0, "lat": 48.5024, "lon": 11.9271, "alt": 500, "temp": 15.2},
  {"time": 10, "lat": 48.5028, "lon": 11.9275, "alt": 552, "temp": 14.8}
]
```

**Object format:**
```json
{
  "sonde_id": "S2260991",
  "sonde_type": "RS41",
  "points": [
    {"time": 0, "lat": 48.5024, "lon": 11.9271, "alt": 500},
    {"time": 10, "lat": 48.5028, "lon": 11.9275, "alt": 552}
  ]
}
```

## Protocol Details

The simulator implements the **JSON-RDZ protocol** used by TTGO devices.

### Messages from simulator → app

Sonde telemetry (sent every update interval):

```json
{
  "id": "S2260991",
  "type": "RS41",
  "lat": 48.5024,
  "lon": 11.9271,
  "alt": 500,
  "validPos": 3,
  "validId": 1,
  "res": 0,
  "temperature": 15.2,
  "relativeHumidity": 65,
  "pressure": 954.3,
  "climbRate": 5.2,
  "batteryVoltage": 3.1,
  "rssi": -95,
  "frameNumber": 1
}
```

### Messages from app → simulator

GPS position (received and logged):

```json
{"lat": 48.1234, "lon": 11.5678, "alt": 520, "course": 90, "hdop": 2.5}
```

Keepalive:

```json
{"status": 1}
```

## Testing with rdzwx-go App

1. **Start the simulator:**
   ```bash
   ./ttgo_simulator.py --loop
   ```

2. **Open rdzwx-go app** on your device (or simulator)

3. **Auto-discovery (preferred):**
   - App should automatically discover "TTGO Simulator" via mDNS
   - Tap to connect

4. **Manual connection (fallback):**
   - Get simulator's IP address from console output
   - In app, enter: `192.168.x.x:12345`

5. **Verify:**
   - Map should show balloon position
   - Position should update every ~1 second
   - Check console for GPS updates from app

## Troubleshooting

### Simulator not discovered by app

- Ensure device and simulator are on same network
- Check firewall isn't blocking port 12345
- Try manual connection with IP:port
- Verify mDNS is working: `dns-sd -B _jsonrdz._tcp` (macOS) or `avahi-browse -r _jsonrdz._tcp` (Linux)

### No data showing in app

- Check simulator console for "Connected" message
- Verify JSON format matches expected protocol
- Enable app debug logging if available

### Connection drops

- Check for network instability
- Verify simulator is still running
- Look for error messages in simulator output

## Development

### Creating Custom Flights

Convert real balloon tracking data:

```python
import csv

# From radiosondy.info or similar source
# Parse telemetry and create CSV with required columns

with open('real_flight.csv', 'w') as f:
    writer = csv.DictWriter(f, fieldnames=['time', 'lat', 'lon', 'alt', 'temp', 'humidity', 'pressure', 'climb'])
    writer.writeheader()
    # ... write rows
```

### Extending the Simulator

The `FlightSimulator` class can be extended to:

- Add realistic GPS noise
- Simulate signal dropouts (validPos flags)
- Model different sonde types (DFM, M10, etc.)
- Include burst/descent phases
- Add wind drift calculations

## License

Same as rdzwx-go project (Apache 2.0)
