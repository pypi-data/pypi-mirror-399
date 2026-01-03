import socket
import json
import time
from core.rush_protocols import RushProtocol
from core.custom_source import CustomSource

class RushClient(CustomSource):
    def __init__(self, host="localhost", port=8000, stealth=False):
        super().__init__(name="rush_client")
        self.host = host
        self.port = port
        self.sock = None
        self.connected = False
        self.stealth = stealth # Kept for API compatibility, though less relevant for raw TCP

    def connect(self):
        """Establishes a TCP connection to the Rush Server."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.connected = True
            print(f"✅ Connected to Rush Server at {self.host}:{self.port}")
        except Exception as e:
            print(f"❌ Connection Failed: {e}")
            self.connected = False

    def send(self, action, data=None):
        """Sends a message and waits for a response."""
        if not self.connected:
            self.connect()
            if not self.connected:
                return {"status": "error", "message": "Not connected"}

        message = {
            "action": action,
            "data": data or {}
        }
        
        try:
            RushProtocol.send_message(self.sock, message)
            
            # Loop until we get a response (ignore broadcasts)
            while True:
                response = RushProtocol.read_message(self.sock)
                if response is None:
                    return None # Connection closed
                
                if response.get("event") == "broadcast":
                    print(f"📢 Broadcast Received: {response}")
                    continue
                    
                return response
        except Exception as e:
            print(f"❌ Send Error: {e}")
            self.close()
            return {"status": "error", "message": str(e)}

    def close(self):
        if self.sock:
            self.sock.close()
        self.connected = False

    # --- Compatibility Methods (Mapping HTTP verbs to Actions) ---
    def get(self, endpoint, **kwargs):
        """Maps GET to an action."""
        return self.send("get", {"endpoint": endpoint, **kwargs})

    def post(self, endpoint, json=None, **kwargs):
        """Maps POST to an action."""
        return self.send("post", {"endpoint": endpoint, "payload": json, **kwargs})

    def put(self, endpoint, json=None, **kwargs):
        return self.send("put", {"endpoint": endpoint, "payload": json, **kwargs})

    def delete(self, endpoint, **kwargs):
        return self.send("delete", {"endpoint": endpoint, **kwargs})

    def fetch(self):
        return self.get("root")

