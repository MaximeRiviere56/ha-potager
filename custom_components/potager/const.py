"""Constantes de l'integration Mon Potager."""

from __future__ import annotations

DOMAIN = "potager"

STORAGE_KEY = "potager.jardin"
STORAGE_VERSION = 1

PANEL_URL = "/potager-frontend"
PANEL_PATH = "potager"
PANEL_TITLE = "Mon Potager"
PANEL_ICON = "mdi:sprout"

# --- Options de configuration -------------------------------------------------

CONF_GELEES_DERNIERE = "gelees_derniere"
CONF_GELEES_PREMIERE = "gelees_premiere"
CONF_ZONES = "zones"
CONF_NOTIFY_TARGETS = "notify_targets"
CONF_NOTIFY_HOUR = "notify_hour"
CONF_RAPPEL_JOURS = "rappel_jours"

# Bouguenais (44), zone USDA 9a, climat oceanique.
DEFAUT_GELEES_DERNIERE = "04-15"
DEFAUT_GELEES_PREMIERE = "11-15"
DEFAUT_NOTIFY_HOUR = 8
DEFAUT_RAPPEL_JOURS = 3

ZONE_PLEINE_TERRE = "pleine-terre"

ZONES_DEFAUT: list[dict] = [
    {"id": ZONE_PLEINE_TERRE, "nom": "Pleine terre", "decalage_jours": 0},
    {"id": "serre", "nom": "Serre", "decalage_jours": -21},
    {"id": "chassis", "nom": "Chassis / tunnel", "decalage_jours": -10},
    {"id": "balcon", "nom": "Balcon / pots", "decalage_jours": 0},
]

# --- Services -----------------------------------------------------------------

SERVICE_AJOUTER_PLANTE = "ajouter_plante"
SERVICE_RETIRER_PLANTE = "retirer_plante"
SERVICE_MARQUER_SEME = "marquer_seme"
SERVICE_MARQUER_REPIQUE = "marquer_repique"
SERVICE_MARQUER_RECOLTE = "marquer_recolte"
SERVICE_MARQUER_PERDU = "marquer_perdu"
SERVICE_MARQUER_TERMINE = "marquer_termine"
SERVICE_ANNULER = "annuler_dernier_evenement"
SERVICE_RAFRAICHIR = "rafraichir"

# --- Evenements du bus -------------------------------------------------------

EVENT_JARDIN_MAJ = f"{DOMAIN}_jardin_maj"
