# WebEnginePy

WebEnginePy est un mini moteur web en Python permettant de créer des sites web très simples sans framework externe.

Le module fournit :
- un serveur HTTP intégré
- un système de routes HTML
- le service de fichiers statiques
- un système d’outils (plugins) appliqués aux pages

Aucune dépendance externe n’est requise.

## Installation

pip install webenginepy

## Principe
Chaque URL est associée à un fichier HTML

Les fichiers statiques sont servis depuis le dossier server/

Les outils sont des scripts Python appliqués au HTML avant envoi

## Structure minimale d’un projet

project/
├── main.py
├── index.html
├── pages/
│   └── page2.html
├── server/
│   └── style.css
└── tools/
    └── exemple.py

## Exemple de site

### Exemple : moteur (engine.py)

import webenginepy as web

with web.app("/", "index.html"):
    web.app("/page2", "pages/page2.html")
    web.app("server/style.css)

with web.app("page2", "page2.html")
    web.app("server/style.css")

web.run(host=0.0.0.0 port=5000)

### index.html

<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="/server/style.css">
</head>
<body>
    <h1>Accueil</h1>
    <a href="/page2">Aller à la page 2</a>
</body>
</html>


### server/style.css

body {
    font-family: Arial;
}

### tools/exemple.py

def apply(html: str) -> str:
    return html.replace("</body>", "<!-- outil appliqué --></body>")

