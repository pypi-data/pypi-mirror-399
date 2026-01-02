-webenginepy

Mini moteur Python pour créer des sites web ultra simples.

-Installation

pip install webenginepy

Exemple d'utilisation

engine.py:
# Déclarer des pages
app("/", "index.html")
app("/contact", "pages/contact.html")

# Activer un outil si besoin
tool("seo")

# Lancer le serveur
run(port=8080)

webenginepy/
│── engine.py
│──index.html
├── pages/
│   └── autrepage.html
│
├── server/
│   └── css/style.css (autres script possibles)
│
├── tools/
    ├── exemple.py
