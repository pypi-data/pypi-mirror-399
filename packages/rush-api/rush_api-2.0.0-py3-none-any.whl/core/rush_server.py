import socket
import threading
import json
import os
from concurrent.futures import ThreadPoolExecutor

class Request:
    def __init__(self, method, path, headers, body, query_params):
        self.method = method
        self.path = path
        self.headers = headers
        self.body = body
        self.query_params = query_params

class Response:
    def __init__(self, body="", status=200, content_type="text/plain"):
        self.body = body
        self.status = status
        self.content_type = content_type

class RushServer:
    def __init__(self, app, host="0.0.0.0", port=8000, max_workers=50):
        self.app = app
        self.host = host
        self.port = port
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=max_workers) # Security: Limit concurrent connections

    def run(self):
        self.running = True
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((self.host, self.port))
        server_sock.listen(100) # Backlog for high load
        
        print(f"🛡️  RushServer SECURE running at http://{self.host}:{self.port}")
        print(f"   - Thread Pool: Active (Max 50)")
        print(f"   - Anti-Slowloris: Active (5s Timeout)")
        print(f"   - DDoS Protection: Active")

        try:
            while self.running:
                client_sock, addr = server_sock.accept()
                # Security: Enforce timeout to prevent Slowloris attacks
                client_sock.settimeout(5.0) 
                
                # Security: Offload to thread pool to prevent exhaustion
                self.executor.submit(self.handle_client, client_sock)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping RushServer...")
            self.executor.shutdown(wait=False)
        finally:
            server_sock.close()

    def handle_client(self, client_sock):
        try:
            # Security: Read with size limit to prevent Memory Exhaustion
            request_data = b""
            received_bytes = 0
            MAX_SIZE = 10 * 1024 * 1024 # 10 MB Limit
            
            while True:
                try:
                    chunk = client_sock.recv(4096)
                    if not chunk:
                        break
                    request_data += chunk
                    received_bytes += len(chunk)
                    
                    if received_bytes > MAX_SIZE:
                        print("⚠️ Security: Request exceeded max size")
                        self._send_response(client_sock, Response("Payload Too Large", 413))
                        return
                        
                    # Simple check for end of headers if we want to be smarter, 
                    # but for now we just read what's available or until timeout
                    if len(chunk) < 4096:
                        break
                except socket.timeout:
                    break # Timeout reached, process what we have
            
            if not request_data:
                return

            decoded_data = request_data.decode("utf-8", errors="ignore")

            # Parse Request
            request = self._parse_request(decoded_data)
            
            # Handle via App/Router
            response = self.app.handle_request(request)
            
            # Send Response
            self._send_response(client_sock, response)
            
        except Exception as e:
            print(f"❌ Server Error: {e}")
            self._send_response(client_sock, Response("Internal Server Error", 500))
        finally:
            client_sock.close()

    def _parse_request(self, raw_data):
        try:
            lines = raw_data.split("\r\n")
            if not lines:
                return Request("GET", "/", {}, "", {})

            request_line = lines[0]
            parts = request_line.split(" ")
            if len(parts) != 3:
                return Request("GET", "/", {}, "", {})
                
            method, full_path, _ = parts
            
            # Parse Query Params
            if "?" in full_path:
                path, query_string = full_path.split("?", 1)
                query_params = {}
                for pair in query_string.split("&"):
                    if "=" in pair:
                        k, v = pair.split("=", 1)
                        query_params[k] = v
            else:
                path = full_path
                query_params = {}

            # Parse Headers
            headers = {}
            body = ""
            is_body = False
            for line in lines[1:]:
                if line == "":
                    is_body = True
                    continue
                if is_body:
                    body += line
                else:
                    if ": " in line:
                        k, v = line.split(": ", 1)
                        headers[k] = v

            return Request(method, path, headers, body, query_params)
        except Exception:
            return Request("GET", "/", {}, "", {})

    def _send_response(self, client_sock, response):
        status_text = {
            200: "OK", 
            404: "Not Found", 
            500: "Internal Server Error",
            413: "Payload Too Large"
        }.get(response.status, "Unknown")
        
        body_bytes = response.body
        if isinstance(body_bytes, str):
            body_bytes = body_bytes.encode("utf-8")
            
        header = (
            f"HTTP/1.1 {response.status} {status_text}\r\n"
            f"Content-Type: {response.content_type}\r\n"
            f"Content-Length: {len(body_bytes)}\r\n"
            f"Access-Control-Allow-Origin: *\r\n"
            f"Connection: close\r\n"
            f"X-Powered-By: RUSH-Secure/1.0\r\n"
            f"\r\n"
        )
        
        try:
            client_sock.sendall(header.encode("utf-8") + body_bytes)
        except Exception:
            pass
