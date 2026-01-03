import socket
import threading
import json
from concurrent.futures import ThreadPoolExecutor
from core.rush_protocols import RushProtocol

class RushServer:
    def __init__(self, app, host="0.0.0.0", port=8000, max_workers=50):
        self.app = app
        self.host = host
        self.port = port
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.clients = [] # Keep track of connected clients for broadcast
        self.lock = threading.Lock()

    def run(self):
        self.running = True
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((self.host, self.port))
        server_sock.listen(100)
        
        print(f"🚀 RushServer (Custom Protocol) running at tcp://{self.host}:{self.port}")

        try:
            while self.running:
                client_sock, addr = server_sock.accept()
                with self.lock:
                    self.clients.append(client_sock)
                
                # Handle client in a separate thread
                self.executor.submit(self.handle_client, client_sock)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping RushServer...")
            self.executor.shutdown(wait=False)
        finally:
            server_sock.close()

    def handle_client(self, client_sock):
        try:
            while True:
                # Read message using Custom Protocol
                message = RushProtocol.read_message(client_sock)
                if message is None:
                    break # Connection closed
                
                # Process Message
                response = self.app.handle_message(message, client_sock)
                
                # Send Response if any
                if response:
                    RushProtocol.send_message(client_sock, response)
                    
        except Exception as e:
            print(f"❌ Connection Error: {e}")
        finally:
            with self.lock:
                if client_sock in self.clients:
                    self.clients.remove(client_sock)
            client_sock.close()

    def broadcast(self, message):
        """Broadcasts a message to all connected clients."""
        with self.lock:
            dead_clients = []
            for client in self.clients:
                try:
                    RushProtocol.send_message(client, message)
                except:
                    dead_clients.append(client)
            
            for dead in dead_clients:
                self.clients.remove(dead)

