from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from typing import Dict, List

ROUTES: Dict[str, str] = {}
TOOLS: List[str] = []
BASE_DIR = os.getcwd()


def app(url: str, file: str) -> None:
    """Déclare une route vers un fichier HTML"""
    ROUTES[url] = file


def tool(name: str) -> None:
    """Active un outil (plugin)"""
    if name not in TOOLS:
        TOOLS.append(name)


def _load_tool(name: str, html: str) -> str:
    """Charge et applique un outil si disponible"""
    tool_path = os.path.join(BASE_DIR, "tools", f"{name}.py")

    if not os.path.exists(tool_path):
        print(f"[WARN] Outil '{name}' introuvable")
        return html

    tool_code = {}
    try:
        with open(tool_path, "r", encoding="utf-8") as f:
            exec(f.read(), tool_code)

        if "apply" in tool_code:
            return tool_code["apply"](html)
        else:
            print(f"[WARN] Outil '{name}' sans fonction apply()")

    except Exception as e:
        print(f"[ERROR] Outil '{name}' : {e}")

    return html


def run(host: str = "localhost", port: int = 8000) -> None:
    """Lance le serveur web"""

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            # ROUTES HTML
            if self.path in ROUTES:
                file_path = os.path.join(BASE_DIR, ROUTES[self.path])

                if not os.path.exists(file_path):
                    self.send_error(404, "Fichier introuvable")
                    return

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        html = f.read()

                    # Appliquer les outils
                    for t in TOOLS:
                        html = _load_tool(t, html)

                    self.send_response(200)
                    self.send_header("Content-type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(html.encode("utf-8"))

                except Exception as e:
                    self.send_error(500, str(e))

            # FICHIERS STATIQUES
            elif self.path.startswith("/server/"):
                file_path = os.path.join(BASE_DIR, self.path[1:])

                if not os.path.exists(file_path):
                    self.send_error(404)
                    return

                self.send_response(200)
                if file_path.endswith(".css"):
                    self.send_header("Content-type", "text/css")
                elif file_path.endswith(".js"):
                    self.send_header("Content-type", "application/javascript")
                else:
                    self.send_header("Content-type", "application/octet-stream")

                self.end_headers()

                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())

            else:
                self.send_error(404, "Route inconnue")

        def log_message(self, format, *args):
            # Logs plus propres
            print(f"[REQ] {self.command} {self.path}")

    print("WebEnginePy démarré")
    print(f"→ http://{host}:{port}")
    print(f"→ Routes : {list(ROUTES.keys())}")
    print(f"→ Outils : {TOOLS}")

    HTTPServer((host, port), Handler).serve_forever()
