# RUSH 🚀

**The Zero-Dependency, AI-Native Protocol Framework for Python**

RUSH is a complete HTTP framework that replaces `requests`, `FastAPI`, and `BeautifulSoup` with **zero external dependencies**. It is designed for the future of the web: **Autonomous AI Agents**.

---

## 🌟 Features

| Feature | Description |
| :--- | :--- |
| **Zero Dependencies** | Works with pure Python. No `pip install` required. |
| **Full HTTP Control** | GET, POST, PUT, DELETE, PATCH with custom headers. |
| **Stealth Mode** | Anti-blocking: User-Agent rotation, Jitter, Auto-429 handling. |
| **Enterprise Ready** | Middleware, Scheduler, Strict Mode for production. |
| **Agent Protocol** | Semantic messaging (Intent, Context) for AI-to-AI communication. |
| **Discovery Mesh** | Agents find each other automatically via UDP Beacons. |
| **Cryptographic Trust** | HMAC-SHA256 signed messages for identity verification. |

---

## ⚡ Quick Start

### 1. Basic HTTP Client (Replace `requests`)

```python
from rush import Rush

app = Rush()

# Simple GET
data = app.get("https://jsonplaceholder.typicode.com/todos/1")
print(data)

# POST with JSON
resp = app.post("https://api.example.com/data", json={"key": "value"})
print(resp.json())
```

### 2. Stealth Mode (Anti-Blocking)

```python
from rush import Rush

# Enable Stealth: Auto User-Agent rotation, Jitter, 429 handling
app = Rush(stealth=True)

data = app.get("https://protected-api.com/data")
```

### 3. HTTP Server (Replace `FastAPI`)

```python
from rush import Rush

app = Rush()

@app.route("/api/hello")
def hello():
    return {"message": "Hello from RUSH!"}

app.start(port=8000)
```

### 4. Enterprise Features

```python
from rush import Rush

app = Rush(strict_mode=True)

# Middleware (Logging, Auth)
def log_request(request):
    print(f"[LOG] {request.method} {request.path}")

app.add_middleware(log_request)

# Scheduled Tasks (Background Jobs)
def backup():
    print("Running backup...")
    
app.schedule(backup, interval_seconds=3600)

app.start(port=8000)
```

### 5. AI Agent Mode (The Future)

```python
from rush import Rush

# Enable Agent Mode for AI-to-AI communication
agent = Rush(agent_mode=True)

@agent.route("/api/status")
def status():
    return {"agent_id": agent.agent_id, "status": "online"}

agent.start(port=9000, background=True)

# Agents discover each other automatically via UDP Beacons
# Then they communicate using signed semantic messages
```

---

## 📁 Project Structure

```
project_rush/
├── rush.py              # Main SDK Entry Point
├── core/
│   ├── rush_http.py     # Raw HTTP Client (Zero-Dep)
│   ├── rush_client.py   # High-Level Client (Caching, Retry, Stealth)
│   ├── rush_server.py   # Custom HTTP Server (Thread Pool, DDoS Protection)
│   ├── rush_router.py   # Routing & Middleware
│   ├── rush_parser.py   # HTML Parser (BeautifulSoup replacement)
│   ├── rush_protocol.py # Semantic Message Format (Intent, Context)
│   ├── rush_discovery.py# Agent Discovery (UDP Beacon)
│   └── rush_trust.py    # Cryptographic Signatures (HMAC-SHA256)
├── examples/
│   ├── magic_demo.py    # Quick Demo
│   ├── full_control_demo.py # All HTTP Methods
│   ├── stealth_demo.py  # Anti-Blocking Demo
│   ├── enterprise_demo.py # Middleware & Scheduler
│   └── ai_mesh_demo.py  # Agent-to-Agent Communication
├── static/              # Static Files for Server
├── tests/               # Unit Tests
├── README.md            # This File
├── USAGE.md             # Detailed Usage Guide
├── requirements.txt     # Empty (Zero Dependencies!)
├── setup.py             # For pip install
└── Dockerfile           # For Docker Deployment
```

---

## 🛡️ Security Features

- **Header Injection Prevention:** All header values are sanitized.
- **Anti-Slowloris:** Connection timeout (5s) prevents slow attacks.
- **Thread Pool:** Limits concurrent connections to prevent DoS.
- **Request Size Limit:** 10MB max to prevent memory exhaustion.
- **HMAC Signatures:** Agent messages are cryptographically signed.

---

## 📈 Comparison

| Feature | REST (requests + FastAPI) | RUSH |
| :--- | :---: | :---: |
| Dependencies | 50+ packages | **0** |
| Stealth/Anti-Block | ❌ | ✅ |
| Background Scheduler | External (Celery) | ✅ Built-in |
| Middleware | Complex ASGI | ✅ Simple |
| AI Agent Protocol | ❌ | ✅ |
| Discovery Mesh | ❌ | ✅ |

---

## 🚀 Deployment

### Docker

```bash
docker build -t rush-app .
docker run -p 8000:8000 rush-app
```

### Local

```bash
python rush.py
# Or run any example:
python examples/magic_demo.py
```

---

## 👤 Author

**Rushabh Mavani**  
📧 rushabhmavani01@gmail.com

---

## 📜 License

MIT License - Use it, modify it, build the future with it.

---

**Built for the Age of AI Agents.** 🤖
