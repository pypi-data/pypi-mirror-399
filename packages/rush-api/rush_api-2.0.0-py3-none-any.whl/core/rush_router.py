import json
import os
import inspect
from core.rush_server import Response

class RushRouter:
    def __init__(self):
        self.routes = {}
        self.static_dirs = {}
        self.middlewares = []

    def add_middleware(self, middleware_func):
        """Adds a middleware function to the chain."""
        self.middlewares.append(middleware_func)

    def get(self, path):
        def decorator(func):
            self.routes[("GET", path)] = func
            return func
        return decorator

    def post(self, path):
        def decorator(func):
            self.routes[("POST", path)] = func
            return func
        return decorator

    def mount(self, path, directory, name=None):
        self.static_dirs[path] = directory

    def handle_request(self, request):
        # 1. Run Middlewares (Pre-Process)
        for middleware in self.middlewares:
            response = middleware(request)
            if response: # Middleware intercepted request
                return response

        # 2. Check Static Files
        for prefix, directory in self.static_dirs.items():
            if request.path.startswith(prefix):
                file_path = request.path[len(prefix):]
                full_path = os.path.join(directory, file_path.lstrip("/"))
                
                if os.path.isdir(full_path):
                    full_path = os.path.join(full_path, "index.html")

                if os.path.exists(full_path) and os.path.isfile(full_path):
                    with open(full_path, "rb") as f:
                        content = f.read()
                    
                    content_type = "text/plain"
                    if full_path.endswith(".html"): content_type = "text/html"
                    if full_path.endswith(".css"): content_type = "text/css"
                    if full_path.endswith(".js"): content_type = "application/javascript"
                    if full_path.endswith(".json"): content_type = "application/json"
                    
                    return Response(content, 200, content_type)

        # 3. Check Routes
        # Normalize path: remove trailing slash for consistency
        normalized_path = request.path.rstrip("/")
        if normalized_path == "": normalized_path = "/"
        
        handler = self.routes.get((request.method, normalized_path))
        if not handler:
             # Try exact match if normalization failed (e.g. root /)
             handler = self.routes.get((request.method, request.path))
             
        if handler:
            try:
                # SAFE MODE: Type Validation
                sig = inspect.signature(handler)
                # Basic check: if handler expects arguments but none provided, or type mismatch
                # For now, we just call it. In a full Pydantic implementation, we'd validate here.
                
                result = handler()
                
                if isinstance(result, dict) or isinstance(result, list):
                    return Response(json.dumps(result), 200, "application/json")
                if hasattr(result, "body"): # It's already a Response object
                    return result
                return Response(str(result), 200, "text/plain")
            except Exception as e:
                # HEAVY MODE: Standardized Error Response
                error_resp = {
                    "error": "Internal Server Error",
                    "detail": str(e),
                    "status": 500
                }
                return Response(json.dumps(error_resp), 500, "application/json")

        return Response(json.dumps({"error": "Not Found"}), 404, "application/json")

class FileResponse(Response):
    def __init__(self, path):
        with open(path, "rb") as f:
            content = f.read()
        super().__init__(content, 200, "text/html")
