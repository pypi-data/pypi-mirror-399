import time
from cryptography.fernet import Fernet

class SecurityEngine:
    def __init__(self, encryption_key=None):
        self.request_counts = {} # IP -> [timestamps]
        # Generate a key if none provided (in real app, load from env)
        self.key = encryption_key or Fernet.generate_key()
        self.cipher = Fernet(self.key)
        print(f"🔒 [VAULT] Encryption Key: {self.key.decode()}")

    def encrypt_payload(self, data: dict) -> str:
        """
        Encrypts a dictionary payload into a string.
        """
        import json
        json_str = json.dumps(data)
        return self.cipher.encrypt(json_str.encode()).decode()

    def decrypt_payload(self, token: str) -> dict:
        """
        Decrypts a token string back into a dictionary.
        """
        import json
        decrypted_data = self.cipher.decrypt(token.encode())
        return json.loads(decrypted_data.decode())

    def check_limit(self, ip_address):
        """
        Enforces a rate limit of 60 requests per minute per IP.
        """
        current_time = time.time()
        
        if ip_address not in self.request_counts:
            self.request_counts[ip_address] = []
            
        # Clean up old timestamps (older than 60s)
        self.request_counts[ip_address] = [t for t in self.request_counts[ip_address] if current_time - t < 60]
        
        # Check count
        if len(self.request_counts[ip_address]) >= 60:
            raise Exception("429 Too Many Requests")
            
        # Add current request
        self.request_counts[ip_address].append(current_time)
        return True
