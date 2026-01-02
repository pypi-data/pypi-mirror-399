import json
import uuid
import time

class RushMessage:
    def __init__(self, intent, payload=None, context=None, sender_id=None):
        self.id = str(uuid.uuid4())
        self.timestamp = time.time()
        self.intent = intent
        self.payload = payload or {}
        self.context = context or {}
        self.sender_id = sender_id or "anonymous"
        self.signature = None # To be filled by Trust module

    def to_dict(self):
        """Converts message to dictionary for transmission."""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "intent": self.intent,
            "payload": self.payload,
            "context": self.context,
            "sender_id": self.sender_id,
            "signature": self.signature
        }

    def to_json(self):
        """Converts message to JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str):
        """Creates a RushMessage from JSON string."""
        data = json.loads(json_str)
        msg = cls(
            intent=data.get("intent"),
            payload=data.get("payload"),
            context=data.get("context"),
            sender_id=data.get("sender_id")
        )
        msg.id = data.get("id")
        msg.timestamp = data.get("timestamp")
        msg.signature = data.get("signature")
        return msg

    def __repr__(self):
        return f"<RushMessage intent='{self.intent}' sender='{self.sender_id}'>"
