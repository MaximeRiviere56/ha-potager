# Sources du logo

Les quatre SVG d'où sortent les huit PNG de `custom_components/rhizome/brand/`.
Le wordmark porte le nom du produit : il a dit « Mon Potager » jusqu'à la
v0.7.0, et « Rhizome » depuis.

Le dessin est un semis qui sort de terre, calibré pour tenir à 48 px dans la
barre latérale : peu de formes, des masses pleines, aucun détail qui disparaisse
à petite taille. Les deux cotylédons sont volontairement dissymétriques — l'un
plus bas et large, l'autre plus haut — ce qui évite l'effet « trèfle » et fait
lire un vrai semis plutôt qu'une plante générique.

## Regénérer les PNG

`qlmanage` (macOS) ne convient pas : il aplatit le SVG sur un fond blanc opaque,
alors que Home Assistant attend de la transparence. Le rendu passe donc par un
canevas de navigateur, qui la conserve.

```bash
python3 tools/brand/rendre.py          # recepteur, port 8778
python3 -m http.server 8777            # dans un autre terminal
# puis http://localhost:8777/tools/brand/rendu.html
```

La page rend les quatre logos d'elle-même. Les icônes ne portent pas de
texte : `produire()` sans argument, dans la console, les refait aussi.

| Fichier | Dimensions | Rôle |
|---|---|---|
| `icon.png` / `icon@2x.png` | 256² / 512² | icône carrée, thème clair |
| `dark_icon.png` / `dark_icon@2x.png` | 256² / 512² | idem, thème sombre |
| `logo.png` / `logo@2x.png` | 640×160 / 1280×320 | logo paysage, thème clair |
| `dark_logo.png` / `dark_logo@2x.png` | 640×160 / 1280×320 | idem, thème sombre |

Depuis Home Assistant 2026.3, un composant personnalisé sert ses propres images
de marque depuis `brand/`, qui **prime** sur le dépôt central
[home-assistant/brands](https://github.com/home-assistant/brands). Aucune pull
request n'est nécessaire.
