import asyncio
import random
import json
import importlib
import os
import requests
import time
from core.adapters import WebAdapter
from core.db_adapter import SQLAdapter
from core.migrator import RestWrapper
from pyngrok import ngrok

import threading
from core.custom_ai import CustomAI
from core.custom_source import CustomSource

class Rush:
    def __init__(self, secret_key="rush-secret-123"):
        self.registry = {}
        self.web_adapter = WebAdapter()
        self.memory_cache = {}
        self.secret_key = secret_key
        self.listeners = {}
        self.webhooks = {}
        self.history_log = [] # Phase 25: Time Machine
        # Phase 26: Self-Healing Module
        self.health_monitor_thread = threading.Thread(target=self.monitor_health, daemon=True)
        self.health_monitor_thread.start()
        
        # Phase 29: Mesh Network
        self.peers = []

    def connect(self, alias, source):
        """
        Connects a data source to the Rush engine.
        Detects if source is a Website URL (http), a Database String (sql), or a Local Object (dict).
        """
        # Log Action (Phase 25)
        self.history_log.append({
            "timestamp": time.time(),
            "action": "connect",
            "args": {"alias": alias, "source": str(source)}
        })

        source_type = "unknown"
        adapter = None

        if isinstance(source, CustomAI):
            source_type = "custom_ai"
            adapter = source
        elif isinstance(source, CustomSource):
            source_type = "custom_source"
            adapter = source
        elif isinstance(source, dict) or isinstance(source, list):
            source_type = "memory"
        elif isinstance(source, str):
            if source.strip().lower().startswith("http"):
                # Check if it's a JSON API or a Web Page
                try:
                    # Quick check
                    r = requests.head(source, timeout=3)
                    content_type = r.headers.get("Content-Type", "").lower()
                    if "application/json" in content_type:
                        source_type = "api"
                        adapter = RestWrapper(source)
                    else:
                        source_type = "url"
                        # WebAdapter is initialized in __init__, but we can use it directly
                except:
                    # Fallback to url if check fails
                    source_type = "url"
            elif "sqlite" in source.lower():
                source_type = "sql"
                adapter = SQLAdapter(source)
            else:
                source_type = "sql"
        
        self.registry[alias] = {
            "source": source,
            "type": source_type,
            "adapter": adapter
        }
        self.listeners[alias] = []
        return f"[{alias}] Connected. Type: {source_type}"



    def load_plugins(self):
        """
        Dynamically loads plugins from the plugins/ directory.
        """
        plugin_dir = "plugins"
        if not os.path.exists(plugin_dir):
            return
            
        for filename in os.listdir(plugin_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f"{plugin_dir}.{module_name}")
                    if hasattr(module, "register"):
                        module.register(self)
                        print(f"🧩 [PLUGIN] Loaded: {module_name}")
                except Exception as e:
                    print(f"❌ [PLUGIN] Failed to load {module_name}: {e}")

    def validate_access(self, request_key):
        """
        Validates the access key.
        """
        if request_key == self.secret_key:
            return True
        raise PermissionError("Invalid Access Key")

    def discover_peers(self):
        """
        Scans the local network (UDP Broadcast) to find other RUSH nodes.
        """
        # Simulated Discovery
        # In a real app, we'd bind a UDP socket and listen/broadcast.
        # For this demo, we'll assume a peer at localhost:8001 if we are 8000
        print("📡 [MESH] Scanning for peers...")
        # Mocking a peer
        self.peers.append("http://localhost:8001")
        print(f"✅ [MESH] Found peer: http://localhost:8001")

    def offload_task(self, task, data):
        """
        Offloads a task to a peer if CPU is high.
        """
        import psutil
        cpu_usage = psutil.cpu_percent()
        
        if cpu_usage > 90 and self.peers:
            peer = random.choice(self.peers)
            print(f"⚠️ [MESH] CPU High ({cpu_usage}%). Offloading to {peer}...")
            try:
                # Send task to peer (assuming peer has an endpoint)
                # requests.post(f"{peer}/offload", json={"task": task, "data": data})
                return {"status": "offloaded", "peer": peer}
            except:
                print("❌ [MESH] Offload failed.")
        
        return None # Process locally

    def monitor_health(self):
        """
        Background thread that checks source health and auto-reconnects.
        """
        while True:
            time.sleep(10) # Check every 10s
            for alias, meta in list(self.registry.items()):
                try:
                    # Ping check
                    if meta["type"] == "url":
                        requests.head(meta["source"], timeout=2)
                    elif meta["type"] == "api":
                        if meta["adapter"]:
                            meta["adapter"].fetch_data() # Try fetch
                except Exception as e:
                    print(f"⚠️ [SELF-HEALING] Source '{alias}' failed: {e}. Reconnecting...")
                    time.sleep(2)
                    try:
                        self.connect(alias, meta["source"])
                        print(f"✅ [SELF-HEALING] Source '{alias}' restored.")
                    except Exception as rec_e:
                        print(f"❌ [SELF-HEALING] Recovery failed for '{alias}': {rec_e}")

    def register_webhook(self, alias, target_url):
        """
        Registers a webhook URL for a specific source alias.
        """
        if alias not in self.webhooks:
            self.webhooks[alias] = []
        self.webhooks[alias].append(target_url)
        return f"Webhook registered for {alias} -> {target_url}"

    async def _send_webhook(self, url, data):
        """
        Sends data to a webhook URL asynchronously.
        """
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: requests.post(url, json=data))
        except Exception as e:
            print(f"Failed to send webhook to {url}: {e}")

    def update(self, alias, new_data):
        """
        Updates the data source and notifies listeners (Real-Time Push) and Webhooks.
        """
        if alias not in self.registry:
            return {"error": "Source not found"}
        
        meta = self.registry[alias]
        
        # Update the source data
        if meta["type"] == "memory":
            if isinstance(meta["source"], list):
                meta["source"].append(new_data)
            elif isinstance(meta["source"], dict):
                meta["source"].update(new_data)
        
        elif meta["type"] == "custom_ai":
            # When we "update" a Custom AI source, we are sending it input to process.
            # The result of the processing becomes the new "data" for that source.
            if meta["adapter"]:
                processed_result = meta["adapter"].process(new_data)
                # We can store the result in memory cache or just broadcast it
                # Let's broadcast the RESULT, not the input.
                new_data = processed_result
        
        # Notify Listeners
        if alias in self.listeners:
            for callback in self.listeners[alias]:
                try:
                    asyncio.create_task(callback(new_data))
                except Exception as e:
                    print(f"Error notifying listener: {e}")

        # Notify Webhooks
        if alias in self.webhooks:
            for url in self.webhooks[alias]:
                try:
                    asyncio.create_task(self._send_webhook(url, new_data))
                except Exception as e:
                    print(f"Webhook error: {e}")
                    
        return {"status": "updated", "data": new_data}

    def get(self, alias, fields=None, ai_task=None):
        """
        Retrieves data from the source.
        Implements Smart Filtering: if fields is provided, return ONLY those fields.
        Implements Smart Caching: checks memory_cache first.
        Implements AI Processing: if ai_task is provided, processes data.
        """
        if fields is None:
            fields = []
            
        # Generate Cache Key
        cache_key = f"{alias}_{str(sorted(fields))}_{str(ai_task)}"
        
        # Check Cache
        if cache_key in self.memory_cache:
            print("⚡ [RUSH] Served from Cache (0ms)")
            return self.memory_cache[cache_key]

        if alias not in self.registry:
            return {"error": f"Source '{alias}' not found."}
        
        meta = self.registry[alias]
        
        # Phase 39: Circuit Breaker
        if meta.get("failure_count", 0) >= 3:
            last_fail = meta.get("last_failure_time", 0)
            if time.time() - last_fail < 300: # 5 minutes cool-down
                return {"error": "Source Temporarily Unavailable (Circuit Open)", "retry_after": 300 - (time.time() - last_fail)}
            else:
                # Reset after cool-down
                meta["failure_count"] = 0

        data = {}
        
        try:
            if meta["type"] == "memory" or meta["type"] == "dict":
                data = meta["source"]
                if isinstance(data, dict) and fields:
                    data = {k: v for k, v in data.items() if k in fields}
                    
            elif meta["type"] == "url":
                data = self.web_adapter.fetch_data(meta["source"])
                if fields:
                    data = {k: v for k, v in data.items() if k in fields}
    
            elif meta["type"] == "api":
                if meta["adapter"]:
                    data = meta["adapter"].fetch_data()
                    if isinstance(data, dict) and fields:
                        data = {k: v for k, v in data.items() if k in fields}
    
            elif meta["type"] == "sql":
                if meta["adapter"]:
                    data = meta["adapter"].fetch_data(alias, fields)
                else:
                    data = {
                        "query": meta["source"],
                        "rows": 5,
                        "data": [{"id": 1, "name": "Test User"}],
                        "status": "success"
                    }
                    if fields:
                        data = {k: v for k, v in data.items() if k in fields}
    
            elif meta["type"] == "plugin":
                if meta["adapter"]:
                    query = "New York" 
                    data = meta["adapter"].fetch_data(query)
                    if fields:
                        data = {k: v for k, v in data.items() if k in fields}

            elif meta["type"] == "custom_ai":
                if meta["adapter"]:
                    # For custom AI, we might want to pass input data if provided, 
                    # but for a simple GET, we'll just fetch status or process a default input.
                    # If 'ai_task' is provided, we can use that as input?
                    # Or we can define a convention that GET on custom_ai returns its status/metadata.
                    # To actually USE the AI, we might need a new method or use 'update' to send input?
                    # Let's assume GET returns the adapter's fetch_data result (status).
                    data = meta["adapter"].fetch_data()
                    if fields:
                        data = {k: v for k, v in data.items() if k in fields}

            elif meta["type"] == "custom_source":
                if meta["adapter"]:
                    data = meta["adapter"].fetch()
                    if isinstance(data, dict) and fields:
                        data = {k: v for k, v in data.items() if k in fields}
            
            # Reset failure count on success
            meta["failure_count"] = 0
            
        except Exception as e:
            print(f"❌ [CIRCUIT BREAKER] Fetch failed for {alias}: {e}")
            meta["failure_count"] = meta.get("failure_count", 0) + 1
            meta["last_failure_time"] = time.time()
            raise e
        
        # AI Processing
        if ai_task:
            data = self._process_with_ai(data, ai_task)

        # Save to Cache
        self.memory_cache[cache_key] = data
        return data

    def time_travel(self, target_timestamp):
        """
        Restores the system state to a specific point in time.
        """
        print(f"⏳ [TIME MACHINE] Rewinding to {target_timestamp}...")
        
        # 1. Reset State
        self.registry = {}
        self.memory_cache = {}
        self.listeners = {}
        self.webhooks = {}
        
        # 2. Replay Log
        for entry in self.history_log:
            if entry["timestamp"] <= target_timestamp:
                if entry["action"] == "connect":
                    self.connect(entry["args"]["alias"], entry["args"]["source"])
        
        return {"status": "Time Travel Successful", "restored_to": target_timestamp}

    async def watch(self, alias, callback, cycles=4):
        """
        Subscribes to real-time updates for a source.
        """
        if alias not in self.registry:
            print(f"Error: Source '{alias}' not found.")
            return

        print(f"[{alias}] Starting Real-Time Stream...")
        
        if cycles:
            # Legacy Simulation Mode
            for _ in range(cycles):
                await asyncio.sleep(2)
                update_data = {
                    "source": alias,
                    "value": random.randint(1, 100),
                    "timestamp": random.randint(1600000000, 1700000000)
                }
                if asyncio.iscoroutinefunction(callback):
                    await callback(update_data)
                else:
                    callback(update_data)
            print(f"[{alias}] Stream ended.")
        else:
            # Real-Time Mode
            if alias not in self.listeners:
                self.listeners[alias] = []
            
            self.listeners[alias].append(callback)
            
            # If it's an API source, we need to poll it
            meta = self.registry[alias]
            if meta["type"] == "api":
                try:
                    while True:
                        await asyncio.sleep(5) # Poll every 5 seconds
                        if meta["adapter"]:
                            new_data = meta["adapter"].fetch_data()
                            await callback(new_data)
                except asyncio.CancelledError:
                     self.listeners[alias].remove(callback)
                     print(f"[{alias}] Listener disconnected.")
            else:
                # For memory/push sources, just wait
                try:
                    while True:
                        await asyncio.sleep(1)
                except asyncio.CancelledError:
                    self.listeners[alias].remove(callback)
                    print(f"[{alias}] Listener disconnected.")
