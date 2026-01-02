import socket
import ssl
import json

class RushHTTP:
    def __init__(self):
        self.timeout = 10

    def _parse_url(self, url):
        """Splits URL into scheme, host, port, path."""
        scheme, rest = url.split("://", 1)
        if "/" in rest:
            host_port, path = rest.split("/", 1)
            path = "/" + path
        else:
            host_port = rest
            path = "/"

        if ":" in host_port:
            host, port = host_port.split(":")
            port = int(port)
        else:
            host = host_port
            port = 443 if scheme == "https" else 80

        return scheme, host, port, path

    def _validate_header_value(self, value):
        """Security: Prevent Header Injection by checking for newlines."""
        if "\r" in value or "\n" in value:
            raise ValueError(f"Security Error: Header value contains newline characters: {value}")
        return value

    def request(self, method, url, headers=None, json_data=None, data=None):
        """Generic HTTP Request Method (The Core)."""
        scheme, host, port, path = self._parse_url(url)
        
        # Security: Sanitize inputs
        host = self._validate_header_value(host)
        path = self._validate_header_value(path)
        method = self._validate_header_value(method.upper())

        # Prepare Headers
        if headers is None:
            headers = {}
        
        # Add Default Headers
        if "Host" not in headers:
            headers["Host"] = host
        if "User-Agent" not in headers:
            headers["User-Agent"] = "RUSH-RawHTTP/1.0"
        if "Connection" not in headers:
            headers["Connection"] = "close"

        # Prepare Body
        body_bytes = b""
        if json_data is not None:
            body_bytes = json.dumps(json_data).encode("utf-8")
            headers["Content-Type"] = "application/json"
        elif data is not None:
            if isinstance(data, str):
                body_bytes = data.encode("utf-8")
            elif isinstance(data, bytes):
                body_bytes = data
            
        if body_bytes:
            headers["Content-Length"] = str(len(body_bytes))

        # Build Request String
        header_str = f"{method} {path} HTTP/1.1\r\n"
        for k, v in headers.items():
            header_str += f"{k}: {self._validate_header_value(str(v))}\r\n"
        header_str += "\r\n"
        
        request_bytes = header_str.encode("utf-8") + body_bytes

        # 1. Create Socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)

        try:
            # 2. Connect
            sock.connect((host, port))

            # 3. SSL Wrap (if HTTPS)
            if scheme == "https":
                context = ssl.create_default_context()
                sock = context.wrap_socket(sock, server_hostname=host)

            # 4. Send Request
            sock.sendall(request_bytes)

            # 5. Receive Response
            response_bytes = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response_bytes += chunk

            return self._parse_response(response_bytes)

        finally:
            sock.close()

    # --- Wrapper Methods for Convenience ---
    def get(self, url, headers=None):
        return self.request("GET", url, headers=headers)

    def post(self, url, json=None, data=None, headers=None):
        return self.request("POST", url, headers=headers, json_data=json, data=data)

    def put(self, url, json=None, data=None, headers=None):
        return self.request("PUT", url, headers=headers, json_data=json, data=data)

    def delete(self, url, headers=None):
        return self.request("DELETE", url, headers=headers)
        
    def patch(self, url, json=None, data=None, headers=None):
        return self.request("PATCH", url, headers=headers, json_data=json, data=data)

    def _parse_response(self, response_bytes):
        """Parses raw HTTP response bytes."""
        try:
            header_part, body_part = response_bytes.split(b"\r\n\r\n", 1)
        except ValueError:
            # Handle case where no body or malformed response
            header_part = response_bytes
            body_part = b""

        headers_str = header_part.decode("utf-8", errors="ignore")
        lines = headers_str.split("\r\n")
        
        # Parse Status Line
        status_line = lines[0]
        try:
            status_code = int(status_line.split(" ")[1])
        except IndexError:
            status_code = 0

        # Parse Body (JSON support)
        text = body_part.decode("utf-8", errors="ignore")
        
        try:
            json_data = json.loads(text)
        except json.JSONDecodeError:
            json_data = text  # Return raw text if not JSON

        # Mimic requests response object structure
        class Response:
            def __init__(self, status, data, text_content):
                self.status_code = status
                self._json = data
                self.text = text_content

            def json(self):
                return self._json

            def raise_for_status(self):
                if 400 <= self.status_code < 600:
                    raise Exception(f"HTTP Error: {self.status_code}")

        return Response(status_code, json_data, text)
