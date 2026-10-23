#!/usr/bin/env python3
"""Rend les SVG du logo en PNG transparents, via un canevas de navigateur.

Pourquoi pas une bibliotheque : ni Pillow ni cairosvg ne sont installables sur
le Mac de developpement (Python 3.9 systeme, sans gestionnaire de paquets), et
`qlmanage` aplatit le SVG sur un fond blanc opaque — verifie en decodant
l'alpha des coins, qui ressortait a 255 au lieu de 0.

Un SVG dessine dans un canevas conserve sa transparence. Ce script lance le
recepteur qui ecrit les fichiers ; le rendu lui-meme a lieu dans
`tools/brand/rendu.html`, ouvert dans un navigateur.
"""

from __future__ import annotations

import base64
import http.server
import pathlib
import textwrap
import urllib.parse

RACINE = pathlib.Path(__file__).resolve().parent.parent.parent
DEST = RACINE / "custom_components" / "rhizome" / "brand"
PORT = 8778


class Recepteur(http.server.BaseHTTPRequestHandler):
    """Ecrit chaque PNG poste par la page de rendu."""

    def _cors(self) -> None:
        # La page est servie depuis un autre port que ce recepteur.
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")

    def do_OPTIONS(self) -> None:
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_POST(self) -> None:
        nom = urllib.parse.unquote(urllib.parse.urlparse(self.path).query)
        brut = self.rfile.read(int(self.headers["Content-Length"])).decode()
        cible = DEST / f"{nom}.png"
        cible.write_bytes(base64.b64decode(brut.split(",", 1)[1]))
        print(f"  {cible.name} — {cible.stat().st_size} octets", flush=True)
        self.send_response(200)
        self._cors()
        self.end_headers()

    def log_message(self, *a: object) -> None:
        pass


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    print(
        textwrap.dedent(
            f"""
            Recepteur en ecoute sur 127.0.0.1:{PORT}
            Les PNG atterrissent dans {DEST.relative_to(RACINE)}

            Dans un autre terminal :

                python3 -m http.server 8777

            puis ouvrir http://localhost:8777/tools/brand/rendu.html

            La page rend les quatre logos d'elle-meme. Les icones n'ont pas de
            texte et ne bougent pas avec le nom du produit : pour les refaire,
            appeler produire() sans argument dans la console.

            Ctrl-C pour arreter.
            """
        ).strip()
    )
    try:
        http.server.HTTPServer(("127.0.0.1", PORT), Recepteur).serve_forever()
    except KeyboardInterrupt:
        print("\nArrete.")


if __name__ == "__main__":
    main()
