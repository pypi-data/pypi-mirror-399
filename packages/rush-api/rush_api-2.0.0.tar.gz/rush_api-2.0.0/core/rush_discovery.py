import socket
import threading
import time
import json

DISCOVERY_PORT = 54321
DISCOVERY_MSG = "RUSH_AGENT_BEACON"

class RushDiscovery:
    def __init__(self, agent_id, port):
        self.agent_id = agent_id
        self.port = port # The HTTP port this agent is listening on
        self.known_agents = {} # {id: {ip, port, last_seen}}
        self.running = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind(("", 0))

    def start(self):
        """Starts Beacon and Listener threads."""
        self.running = True
        
        # 1. Beacon Thread (I am here!)
        threading.Thread(target=self._beacon_loop, daemon=True).start()
        
        # 2. Listener Thread (Who is there?)
        threading.Thread(target=self._listen_loop, daemon=True).start()

    def _beacon_loop(self):
        while self.running:
            msg = json.dumps({
                "magic": DISCOVERY_MSG,
                "id": self.agent_id,
                "port": self.port
            })
            try:
                self.sock.sendto(msg.encode(), ('<broadcast>', DISCOVERY_PORT))
            except Exception as e:
                print(f"⚠️ Discovery Beacon Error: {e}")
            time.sleep(2) # Pulse every 2 seconds

    def _listen_loop(self):
        listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            listen_sock.bind(("", DISCOVERY_PORT))
        except:
            print("⚠️ Discovery Port Busy. Discovery Disabled.")
            return

        while self.running:
            try:
                data, addr = listen_sock.recvfrom(1024)
                msg = json.loads(data.decode())
                
                if msg.get("magic") == DISCOVERY_MSG:
                    remote_id = msg["id"]
                    if remote_id != self.agent_id: # Ignore self
                        self.known_agents[remote_id] = {
                            "ip": addr[0],
                            "port": msg["port"],
                            "last_seen": time.time()
                        }
                        # print(f"📡 Discovered Agent: {remote_id} at {addr[0]}:{msg['port']}")
            except Exception:
                pass
