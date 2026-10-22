#!/usr/bin/env python3
"""Rend les SVG du logo en PNG transparents, via un canevas de navigateur.

Pourquoi pas une bibliotheque : ni Pillow ni cairosvg ne sont installables sur
le Mac de developpement (Python 3.9 systeme, sans gestionnaire de paquets), et
`qlmanage` aplatit le SVG sur un fond blanc opaque — verifie en decodant
l'alpha des coins, qui ressortait a 255 au lieu de 0.

Un SVG dessine dans un canevas conserve sa transparence. Ce script prepare les
deux pages et le recepteur ; il reste a ouvrir la page dans un navigateur.
"""

from __future__ import annotations

import pathlib
import textwrap

RACINE = pathlib.Path(__file__).resolve().parent.parent.parent
DEST = RACINE / "custom_components" / "potager" / "brand"

print(
    textwrap.dedent(
        f"""
        Marche a suivre
        ---------------
        1. Lancer un recepteur qui ecrit dans {DEST.relative_to(RACINE)} :

           python3 - <<'EOF'
           import base64, http.server, pathlib, urllib.parse
           DEST = pathlib.Path("{DEST}")
           DEST.mkdir(parents=True, exist_ok=True)
           class H(http.server.BaseHTTPRequestHandler):
               def do_OPTIONS(self):
                   self.send_response(200); self._c(); self.end_headers()
               def do_POST(self):
                   nom = urllib.parse.urlparse(self.path).query
                   brut = self.rfile.read(int(self.headers["Content-Length"])).decode()
                   (DEST / f"{{nom}}.png").write_bytes(
                       base64.b64decode(brut.split(",", 1)[1]))
                   self.send_response(200); self._c(); self.end_headers()
               def _c(self):
                   self.send_header("Access-Control-Allow-Origin", "*")
               def log_message(self, *a): pass
           http.server.HTTPServer(("127.0.0.1", 8778), H).serve_forever()
           EOF

        2. Servir ce dossier :   python3 -m http.server 8777 --directory tools/brand
        3. Ouvrir http://localhost:8777/ et, dans la console, appeler produire().

        Les tailles attendues sont rappelees dans tools/brand/README.md.
        """
    ).strip()
)
