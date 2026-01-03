import struct
import json
import socket

class RushProtocol:
    """
    Custom Rush Protocol: Simple, Fast, JSON over TCP.
    Format: [Length (4 bytes big-endian)] [JSON Payload (utf-8)]
    """
    
    @staticmethod
    def send_message(sock: socket.socket, message: dict):
        """Encodes and sends a message."""
        try:
            json_data = json.dumps(message).encode("utf-8")
            length = len(json_data)
            # Pack length as 4-byte big-endian integer
            header = struct.pack("!I", length)
            sock.sendall(header + json_data)
        except Exception as e:
            print(f"Proto Send Error: {e}")
            raise e

    @staticmethod
    def read_message(sock: socket.socket) -> dict:
        """Reads and decodes a message."""
        # 1. Read Header (Length)
        header = RushProtocol._recv_all(sock, 4)
        if not header:
            return None # Connection closed
            
        length = struct.unpack("!I", header)[0]
        
        # 2. Read Body
        body_data = RushProtocol._recv_all(sock, length)
        if not body_data:
            return None # Incomplete message
            
        # 3. Decode JSON
        try:
            return json.loads(body_data.decode("utf-8"))
        except json.JSONDecodeError:
            print("Proto Error: Invalid JSON")
            return None

    @staticmethod
    def _recv_all(sock: socket.socket, n: int) -> bytes:
        """Helper to receive exactly n bytes."""
        data = b""
        while len(data) < n:
            try:
                packet = sock.recv(n - len(data))
                if not packet:
                    return None
                data += packet
            except socket.timeout:
                return None
            except Exception as e:
                print(f"Proto Recv Error: {e}")
                return None
        return data
