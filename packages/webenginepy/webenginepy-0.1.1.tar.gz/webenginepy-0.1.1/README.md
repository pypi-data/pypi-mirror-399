webenginepy

Mini moteur web ultra simple en Python pour :

les débutants

créer des sites ultra légers

sans framework ni API complexe

Installation
pip install webenginepy

Exemple d’utilisation
engine.py (fichier principal)
import webenginepy

# Déclarer la page principale
webenginepy.app("/", "index.html")

# Déclarer des pages secondaires
webenginepy.app("/about", "pages/about.html")
# /about = nom de la page
# pages/about.html = chemin du fichier

# Déclarer des outils
webenginepy.tool("seo")  # 'seo' = nom de l'outil placé dans tools/seo.py

# Démarrer le serveur
webenginepy.run(host="0.0.0.0", port=8000)

Exemple d’outil (plugin)

tools/seo.py

def apply(html: str) -> str:
    """Ajoute une meta description pour le SEO"""
    return html.replace(
        "</head>",
        "<meta name='description' content='Mon site'>\n</head>"
    )

Structure de base du projet
project/
├── engine.py           # fichier principal
├── index.html          # page principale
├── pages/              # pages secondaires
│   └── about.html
├── server/             # fichiers statiques (CSS, JS, images…)
│   └── style.css
└── tools/              # outils / plugins
    └── seo.py