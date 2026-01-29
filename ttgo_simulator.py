#!/usr/bin/env python3
"""
TTGO JSONRDZ Protocol Simulator

Simulates a TTGO ESP32 radiosonde tracker device for testing rdzwx-go app.
Advertises via mDNS and streams simulated balloon flight data over TCP.

Usage:
    ./ttgo_simulator.py                          # Use built-in sample flight
    ./ttgo_simulator.py --flight flight.json     # Load flight from JSON
    ./ttgo_simulator.py --flight flight.csv      # Load flight from CSV
    ./ttgo_simulator.py --speed 2.0              # 2x playback speed
    ./ttgo_simulator.py --port 12345             # Custom TCP port
"""

import socket
import json
import time
import threading
import argparse
import csv
import sys
from datetime import datetime
from typing import List, Dict, Optional
from zeroconf import ServiceInfo, Zeroconf
import ipaddress


# Sample balloon flight data (ascending phase)
SAMPLE_FLIGHT = [
    {"time": 0, "lat": 48.5024, "lon": 11.9271, "alt": 500, "temp": 15.2, "humidity": 65, "pressure": 954.3, "climb": 5.2},
    {"time": 10, "lat": 48.5028, "lon": 11.9275, "alt": 552, "temp": 14.8, "humidity": 64, "pressure": 948.1, "climb": 5.3},
    {"time": 20, "lat": 48.5032, "lon": 11.9280, "alt": 605, "temp": 14.3, "humidity": 63, "pressure": 941.8, "climb": 5.1},
    {"time": 30, "lat": 48.5036, "lon": 11.9285, "alt": 656, "temp": 13.9, "humidity": 62, "pressure": 935.7, "climb": 5.4},
    {"time": 40, "lat": 48.5041, "lon": 11.9291, "alt": 710, "temp": 13.4, "humidity": 61, "pressure": 929.3, "climb": 5.2},
    {"time": 50, "lat": 48.5045, "lon": 11.9297, "alt": 762, "temp": 12.9, "humidity": 60, "pressure": 923.2, "climb": 5.3},
    {"time": 60, "lat": 48.5050, "lon": 11.9303, "alt": 815, "temp": 12.4, "humidity": 59, "pressure": 916.9, "climb": 5.1},
    {"time": 70, "lat": 48.5054, "lon": 11.9310, "alt": 866, "temp": 11.9, "humidity": 58, "pressure": 910.8, "climb": 5.4},
    {"time": 80, "lat": 48.5059, "lon": 11.9316, "alt": 920, "temp": 11.3, "humidity": 57, "pressure": 904.4, "climb": 5.2},
    {"time": 90, "lat": 48.5064, "lon": 11.9323, "alt": 972, "temp": 10.8, "humidity": 56, "pressure": 898.3, "climb": 5.3},
    {"time": 100, "lat": 48.5068, "lon": 11.9330, "alt": 1025, "temp": 10.2, "humidity": 55, "pressure": 891.9, "climb": 5.1},
    {"time": 110, "lat": 48.5073, "lon": 11.9337, "alt": 1076, "temp": 9.7, "humidity": 54, "pressure": 885.8, "climb": 5.4},
    {"time": 120, "lat": 48.5078, "lon": 11.9345, "alt": 1130, "temp": 9.1, "humidity": 53, "pressure": 879.4, "climb": 5.2},
    {"time": 130, "lat": 48.5083, "lon": 11.9352, "alt": 1182, "temp": 8.5, "humidity": 52, "pressure": 873.3, "climb": 5.3},
    {"time": 140, "lat": 48.5088, "lon": 11.9360, "alt": 1235, "temp": 7.9, "humidity": 51, "pressure": 866.9, "climb": 5.1},
]


class FlightSimulator:
    """Manages flight data playback"""

    def __init__(self, flight_data: List[Dict], speed: float = 1.0, loop: bool = True):
        self.flight_data = flight_data
        self.speed = speed
        self.loop = loop
        self.current_index = 0
        self.sonde_id = "S2260991"
        self.sonde_type = "RS41"
        self.freq = "402.300"

    def get_next_point(self) -> Optional[Dict]:
        """Get next flight data point with proper JSON-RDZ formatting"""
        if self.current_index >= len(self.flight_data):
            if self.loop:
                self.current_index = 0
            else:
                return None

        point = self.flight_data[self.current_index]
        self.current_index += 1

        # Build JSON-RDZ message matching the protocol
        msg = {
            "id": self.sonde_id,
            "type": self.sonde_type,
            "lat": point["lat"],
            "lon": point["lon"],
            "alt": point["alt"],
            "validPos": 3,  # lat and lon valid (bits 0,1)
            "validId": 1,
            "res": 0,  # success
            "freq": self.freq,
            "temperature": point.get("temp"),
            "relativeHumidity": point.get("humidity"),
            "pressure": point.get("pressure"),
            "climbRate": point.get("climb", 0),
            "batteryVoltage": 3.1,
            "rssi": -95,
            "frameNumber": self.current_index,
        }

        # Remove None values
        return {k: v for k, v in msg.items() if v is not None}

    def get_update_interval(self) -> float:
        """Calculate sleep time between updates based on speed multiplier"""
        if self.current_index >= len(self.flight_data):
            return 1.0 / self.speed

        if self.current_index == 0:
            return 0.1  # First point immediately

        curr = self.flight_data[self.current_index]
        prev = self.flight_data[self.current_index - 1]
        time_delta = curr.get("time", self.current_index) - prev.get("time", self.current_index - 1)

        return max(0.1, time_delta / self.speed)


class TTGOSimulator:
    """Main simulator server"""

    def __init__(self, port: int = 12345, host: str = "0.0.0.0", service_name: str = "TTGO Simulator"):
        self.port = port
        self.host = host
        self.service_name = service_name
        self.running = False
        self.clients = []
        self.lock = threading.Lock()
        self.zeroconf = None
        self.service_info = None

    def start_mdns(self):
        """Advertise service via mDNS"""
        self.zeroconf = Zeroconf()

        # Get local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        except:
            local_ip = "127.0.0.1"
        finally:
            s.close()

        # Convert IP to bytes
        ip_bytes = socket.inet_aton(local_ip)

        self.service_info = ServiceInfo(
            "_jsonrdz._tcp.local.",
            f"{self.service_name}._jsonrdz._tcp.local.",
            addresses=[ip_bytes],
            port=self.port,
            properties={},
            server=f"{self.service_name.replace(' ', '-').lower()}.local."
        )

        print(f"[mDNS] Advertising service: {self.service_name}")
        print(f"[mDNS] Type: _jsonrdz._tcp.local.")
        print(f"[mDNS] Address: {local_ip}:{self.port}")

        self.zeroconf.register_service(self.service_info)

    def stop_mdns(self):
        """Stop mDNS advertisement"""
        if self.zeroconf and self.service_info:
            print("[mDNS] Unregistering service...")
            self.zeroconf.unregister_service(self.service_info)
            self.zeroconf.close()

    def handle_client(self, client_socket: socket.socket, address):
        """Handle individual client connection"""
        print(f"[Client] Connected: {address}")

        with self.lock:
            self.clients.append(client_socket)

        try:
            # Read incoming data (GPS positions from app)
            client_socket.settimeout(1.0)
            buffer = b""

            while self.running:
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        break

                    buffer += data
                    while b'\n' in buffer:
                        line, buffer = buffer.split(b'\n', 1)
                        try:
                            msg = json.loads(line.decode('iso-8859-1'))
                            if "lat" in msg and "lon" in msg:
                                print(f"[Client] Received GPS: lat={msg['lat']:.4f}, lon={msg['lon']:.4f}, alt={msg.get('alt', 0):.1f}m")
                            elif "status" in msg:
                                print(f"[Client] Keepalive received")
                        except json.JSONDecodeError:
                            pass

                except socket.timeout:
                    continue
                except Exception as e:
                    break

        finally:
            with self.lock:
                if client_socket in self.clients:
                    self.clients.remove(client_socket)

            client_socket.close()
            print(f"[Client] Disconnected: {address}")

    def broadcast_data(self, data: Dict):
        """Send data to all connected clients"""
        json_str = json.dumps(data, separators=(',', ':'))
        message = json_str.encode('iso-8859-1') + b'}\n'

        with self.lock:
            dead_clients = []
            for client in self.clients:
                try:
                    client.send(message)
                except:
                    dead_clients.append(client)

            for client in dead_clients:
                self.clients.remove(client)
                client.close()

    def run(self, flight_sim: FlightSimulator):
        """Main server loop"""
        self.running = True

        # Start mDNS advertisement
        self.start_mdns()

        # Start TCP server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        server_socket.settimeout(1.0)

        print(f"[Server] Listening on {self.host}:{self.port}")
        print(f"[Server] Sonde ID: {flight_sim.sonde_id}, Type: {flight_sim.sonde_type}")
        print(f"[Server] Flight data points: {len(flight_sim.flight_data)}")
        print(f"[Server] Playback speed: {flight_sim.speed}x")
        print(f"[Server] Press Ctrl+C to stop\n")

        # Accept connections in background thread
        def accept_connections():
            while self.running:
                try:
                    client_socket, address = server_socket.accept()
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"[Error] Accept failed: {e}")

        accept_thread = threading.Thread(target=accept_connections, daemon=True)
        accept_thread.start()

        # Main data broadcast loop
        try:
            while self.running:
                point = flight_sim.get_next_point()
                if point is None:
                    print("[Simulation] Flight complete, stopping...")
                    break

                # Broadcast to all clients
                if self.clients:
                    self.broadcast_data(point)
                    print(f"[Data] alt={point['alt']:5.0f}m, lat={point['lat']:.4f}, lon={point['lon']:.4f}, "
                          f"climb={point.get('climbRate', 0):+.1f}m/s → {len(self.clients)} client(s)")

                # Wait before next update
                time.sleep(flight_sim.get_update_interval())

        except KeyboardInterrupt:
            print("\n[Server] Shutting down...")

        finally:
            self.running = False
            server_socket.close()
            self.stop_mdns()

            with self.lock:
                for client in self.clients:
                    client.close()
                self.clients.clear()


def load_flight_from_json(filepath: str) -> List[Dict]:
    """Load flight data from JSON file"""
    with open(filepath, 'r') as f:
        data = json.load(f)

    # Handle both array of points or object with 'points' key
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and 'points' in data:
        return data['points']
    else:
        raise ValueError("JSON must be array of points or object with 'points' key")


def load_flight_from_csv(filepath: str) -> List[Dict]:
    """Load flight data from CSV file

    Expected columns: time,lat,lon,alt[,temp,humidity,pressure,climb]
    """
    flight_data = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            point = {
                "time": float(row["time"]),
                "lat": float(row["lat"]),
                "lon": float(row["lon"]),
                "alt": float(row["alt"]),
            }

            # Optional fields
            if "temp" in row:
                point["temp"] = float(row["temp"])
            if "humidity" in row:
                point["humidity"] = float(row["humidity"])
            if "pressure" in row:
                point["pressure"] = float(row["pressure"])
            if "climb" in row:
                point["climb"] = float(row["climb"])

            flight_data.append(point)

    return flight_data


def main():
    parser = argparse.ArgumentParser(
        description="TTGO JSONRDZ Protocol Simulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              Use built-in sample flight
  %(prog)s --flight my_flight.json      Load flight from JSON
  %(prog)s --flight my_flight.csv       Load flight from CSV
  %(prog)s --speed 2.0 --loop           2x speed, loop forever
  %(prog)s --port 9999 --name "Test"    Custom port and service name
        """
    )

    parser.add_argument('--flight', '-f', type=str, help='Flight data file (JSON or CSV)')
    parser.add_argument('--port', '-p', type=int, default=12345, help='TCP port (default: 12345)')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Bind address (default: 0.0.0.0)')
    parser.add_argument('--speed', '-s', type=float, default=1.0, help='Playback speed multiplier (default: 1.0)')
    parser.add_argument('--loop', '-l', action='store_true', help='Loop flight data indefinitely')
    parser.add_argument('--name', '-n', type=str, default='TTGO Simulator', help='mDNS service name')
    parser.add_argument('--id', type=str, default='S2260991', help='Sonde ID (default: S2260991)')
    parser.add_argument('--type', '-t', type=str, default='RS41', help='Sonde type (default: RS41)')

    args = parser.parse_args()

    # Load flight data
    if args.flight:
        print(f"[Init] Loading flight from: {args.flight}")
        try:
            if args.flight.endswith('.json'):
                flight_data = load_flight_from_json(args.flight)
            elif args.flight.endswith('.csv'):
                flight_data = load_flight_from_csv(args.flight)
            else:
                print("Error: Flight file must be .json or .csv")
                return 1
        except Exception as e:
            print(f"Error loading flight data: {e}")
            return 1
    else:
        print("[Init] Using built-in sample flight")
        flight_data = SAMPLE_FLIGHT

    # Create simulator
    flight_sim = FlightSimulator(flight_data, speed=args.speed, loop=args.loop)
    flight_sim.sonde_id = args.id
    flight_sim.sonde_type = args.type

    server = TTGOSimulator(port=args.port, host=args.host, service_name=args.name)

    # Run
    server.run(flight_sim)

    return 0


if __name__ == "__main__":
    sys.exit(main())
