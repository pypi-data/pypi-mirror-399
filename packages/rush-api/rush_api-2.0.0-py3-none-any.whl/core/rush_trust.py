import hmac
import hashlib
import base64
import os

class RushTrust:
    def __init__(self, secret_key=None):
        # In a real app, this would come from ENV or a Key Vault
        # For now, we generate a random one if not provided
        self.secret_key = secret_key.encode() if secret_key else os.urandom(32)

    def sign_message(self, message_dict):
        """Signs a message dictionary (excluding signature field)."""
        # Create a canonical string representation for signing
        # We sort keys to ensure consistency
        payload_str = ""
        for key in sorted(message_dict.keys()):
            if key == "signature": continue
            payload_str += f"{key}={message_dict[key]}&"
        
        # HMAC-SHA256
        signature = hmac.new(
            self.secret_key, 
            payload_str.encode(), 
            hashlib.sha256
        ).digest()
        
        return base64.b64encode(signature).decode()

    def verify_message(self, message_dict):
        """Verifies that the message signature is valid."""
        if "signature" not in message_dict or not message_dict["signature"]:
            return False
            
        expected_sig = self.sign_message(message_dict)
        # Constant time comparison to prevent timing attacks
        return hmac.compare_digest(expected_sig, message_dict["signature"])
