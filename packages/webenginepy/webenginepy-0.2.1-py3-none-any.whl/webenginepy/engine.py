# webenginepy/engine.py

from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from typing import Dict, List, Optional

# ======================
# Données globales
# ======================

BASE_DIR = os.getcwd()

PAGES: Dict[str, dict] = {}
TOOLS: List[str] = []

_current_page: Optional[str] = None


# ======================
# Déclaration des pages
# ======================

class app:
    """
    Déclare une page web.

    Utilisation :
    with app("/", "index.html"):
        route("server/style.css")
        route("button:page2", "/page2")
    """

    def __init__(self, url: str, file: str):
        self.url = url
        self.file = file

    def __enter__(self):
        global _current_page

        if not self.url.startswith("/"):
            self.url = "/" + self.url

        PAGES[self.url] = {
            "file": self.file,
            "static": [],
            "buttons": {}
        }

        _current_page = self.url
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        global _current_page
        _current_page = None


# ======================
# Routes internes
# ======================

def route(value: str, target: Optional[str] = None):
    """
    Ajoute une route liée à la page courante

    - route("server/style.css")
    - route("button:page2", "/page2")
    """
    if _current_page is None:
        raise RuntimeError("route() doit être utilisé dans un bloc with app()")

    page = PAGES[_current_page]

    # Fichier statique
    if value.startswith("server/"):
        page["static"].append(value)

    # Bouton / lien
    elif value.startswith("button:") and target:
        name = value.split(":", 1)[1]
        page["buttons"][name] = target

    else:
        raise ValueError(f"Route invalide : {value}")


# ======================
# Outils (plugins)
# ======================

def tool(name: str):
    """
    Active un outil (tools/nom.py)
    """
    if name not in TOOLS:
        TOOLS.append(name)


def _apply_tools(html: str) -> str:
    """
    Applique tous les outils activés au HTML
    """
    for t in TOOLS:
        tool_path = os.path.join(BASE_DIR, "tools", f"{t}.py")

        if not os.path.exists(tool_path):
            print(f"[WARN] outil '{t}' introuvable")
            continue

        scope = {}
        try:
            with open(tool_path, encoding="utf-8") as f:
                exec(f.read(), scope)

            if "apply" in scope:
                html = scope["apply"](html)

        except Exception as e:
            print(f"[ERROR] outil '{t}': {e}")

    return html


# ======================
# Serveur HTTP
# ======================

def run(host: str = "localhost", port: int = 8000):
    """
    Lance le serveur WebEnginePy
    """

    class Handler(BaseHTTPRequestHandler):

        def do_GET(self):
            # ======================
            # Pages HTML
            # ======================
            if self.path in PAGES:
                page = PAGES[self.path]
                file_path = os.path.join(BASE_DIR, page["file"])

                if not os.path.exists(file_path):
                    self.send_error(404, "Fichier HTML introuvable")
                    return

                try:
                    with open(file_path, encoding="utf-8") as f:
                        html = f.read()

                    # Injection boutons (simple)
                    for name, link in page["buttons"].items():
                        button_html = f'<a href="{link}"><button>{name}</button></a>'
                        html = html.replace("</body>", button_html + "\n</body>")

                    # Outils
                    html = _apply_tools(html)

                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(html.encode("utf-8"))

                except Exception as e:
                    self.send_error(500, str(e))

            # ======================
            # Fichiers statiques
            # ======================
            elif self.path.startswith("/server/"):
                file_path = os.path.join(BASE_DIR, self.path[1:])

                if not os.path.exists(file_path):
                    self.send_error(404)
                    return

                self.send_response(200)

                if file_path.endswith(".css"):
                    self.send_header("Content-Type", "text/css")
                elif file_path.endswith(".js"):
                    self.send_header("Content-Type", "application/javascript")
                else:
                    self.send_header("Content-Type", "application/octet-stream")

                self.end_headers()

                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())

            # ======================
            # Inconnu
            # ======================
            else:
                self.send_error(404, "Route inconnue")

        def log_message(self, *args):
            print(f"[REQ] {self.command} {self.path}")

    # ======================
    # Infos serveur
    # ======================
    print("WebEnginePy démarré")
    print(f"→ http://{host}:{port}")
    print("→ Pages :", list(PAGES.keys()))
    print("→ Outils :", TOOLS)

    HTTPServer((host, port), Handler).serve_forever()
