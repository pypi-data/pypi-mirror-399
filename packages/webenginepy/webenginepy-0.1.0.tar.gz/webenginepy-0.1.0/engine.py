from http.server import BaseHTTPRequestHandler, HTTPServer
import os

ROUTES = {}
TOOLS = []
BASE_DIR = os.getcwd()

def app(url, file):
    """Déclare une page"""
    ROUTES[url] = file

def tool(name):
    """Active un outil"""
    TOOLS.append(name)

def run(host="localhost", port=8000):
    """Lance le serveur"""
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            # ROUTES
            if self.path in ROUTES:
                file_path = os.path.join(BASE_DIR, ROUTES[self.path])
                if not os.path.exists(file_path):
                    self.send_error(404)
                    return

                html = open(file_path, "r", encoding="utf-8").read()

                # Appliquer les outils
                for t in TOOLS:
                    tool_path = os.path.join(BASE_DIR, "tools", f"{t}.py")
                    if os.path.exists(tool_path):
                        tool_code = {}
                        exec(open(tool_path).read(), tool_code)
                        if "apply" in tool_code:
                            html = tool_code["apply"](html)

                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(html.encode())

            # SERVER (static)
            elif self.path.startswith("/server/"):
                file_path = os.path.join(BASE_DIR, self.path[1:])
                if os.path.exists(file_path):
                    self.send_response(200)
                    if file_path.endswith(".css"):
                        self.send_header("Content-type", "text/css")
                    elif file_path.endswith(".js"):
                        self.send_header("Content-type", "application/javascript")
                    self.end_headers()
                    with open(file_path, "rb") as f:
                        self.wfile.write(f.read())
                else:
                    self.send_error(404)
            else:
                self.send_error(404)

    print(f"Site lancé sur http://{host}:{port}")
    HTTPServer((host, port), Handler).serve_forever()
