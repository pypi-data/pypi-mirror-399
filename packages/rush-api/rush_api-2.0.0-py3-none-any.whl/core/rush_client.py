# import requests  <-- REMOVED
from core.rush_http import RushHTTP
import time
from core.custom_source import CustomSource

import random

class RushClient(CustomSource):
    def __init__(self, base_url, stealth=False):
        super().__init__(name="rush_client")
        self.base_url = base_url.rstrip("/")
        self.cache = {}
        self.retry_count = 5
        self.http_client = RushHTTP()
        self.stealth = stealth
        
        # STEALTH MODE: Browser Agents
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
        ]

    def _apply_stealth(self, headers):
        """Applies Stealth Headers and Jitter."""
        if not self.stealth:
            return headers or {}
            
        if headers is None:
            headers = {}
            
        # 1. Rotate User-Agent
        if "User-Agent" not in headers:
            headers["User-Agent"] = random.choice(self.user_agents)
            
        # 2. Add Real Browser Headers
        headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
        headers["Accept-Language"] = "en-US,en;q=0.5"
        headers["Connection"] = "keep-alive"
        headers["Upgrade-Insecure-Requests"] = "1"
        
        # 3. Add Jitter (Random Delay to look human)
        time.sleep(random.uniform(0.1, 0.5))
        
        return headers

    def get(self, endpoint, use_cache=True, ai_task=None, headers=None):
        """
        A 'Better' GET request with:
        - Auto-Caching
        - Auto-Retries
        - AI Processing Hook
        - Stealth Mode (Anti-Blocking)
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # 1. Cache Check
        if use_cache and url in self.cache:
            print(f"⚡ [RUSH_CLIENT] Cache Hit: {url}")
            return self.cache[url]

        # 2. Network Request with Retry
        for attempt in range(self.retry_count):
            try:
                # STEALTH: Apply Browser Headers
                headers = self._apply_stealth(headers)
                
                print(f"🌍 [RUSH_CLIENT] Fetching: {url} (Attempt {attempt+1})")
                resp = self.http_client.get(url, headers=headers)
                
                # STEALTH: Handle Rate Limits (429)
                if resp.status_code == 429:
                    wait_time = random.uniform(5, 10)
                    print(f"🛑 [STEALTH] Rate Limited (429). Sleeping {wait_time:.1f}s...")
                    time.sleep(wait_time)
                    continue

                # Simulate 500 error handling
                if resp.status_code >= 500:
                    print(f"⚠️ [RUSH_CLIENT] Server Error {resp.status_code}. Retrying...")
                    time.sleep(1)
                    continue
                
                resp.raise_for_status()
                data = resp.json()
                
                # 3. AI Processing (Simulation)
                if ai_task:
                    print(f"🤖 [RUSH_CLIENT] AI Processing ({ai_task})...")
                    data = self._simulate_ai(data, ai_task)

                # Save to Cache
                if use_cache:
                    self.cache[url] = data
                
                return data
            except Exception as e:
                print(f"❌ [RUSH_CLIENT] Request Failed: {e}")
                if attempt == self.retry_count - 1:
                    return {"error": str(e)}
                time.sleep(1)

    # --- Full Control Passthrough Methods ---
    def _build_url(self, endpoint):
        if endpoint.startswith("http"):
            return endpoint
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def post(self, endpoint, json=None, data=None, headers=None):
        url = self._build_url(endpoint)
        return self.http_client.post(url, json=json, data=data, headers=headers)

    def put(self, endpoint, json=None, data=None, headers=None):
        url = self._build_url(endpoint)
        return self.http_client.put(url, json=json, data=data, headers=headers)

    def delete(self, endpoint, headers=None):
        url = self._build_url(endpoint)
        return self.http_client.delete(url, headers=headers)

    def patch(self, endpoint, json=None, data=None, headers=None):
        url = self._build_url(endpoint)
        return self.http_client.patch(url, json=json, data=data, headers=headers)

    def fetch(self):
        """
        Implementation for RUSH CustomSource compatibility.
        Fetches the root or a default endpoint.
        """
        return self.get("")

    def _simulate_ai(self, data, task):
        """
        Simulates the Neural Gateway processing.
        """
        if task == "summarize":
            return {
                "summary": "AI Summarized this content for you.",
                "original_keys": list(data.keys()) if isinstance(data, dict) else "list",
                "original_data": data
            }
        return data
