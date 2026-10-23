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
CONF_NOTIFY_HEURE = "notify_heure"
CONF_PRESET_CLIMAT = "preset_climat"
CONF_RAPPEL_JOURS = "rappel_jours"

# --- Granularite des rappels --------------------------------------------------

# Quelles etapes meritent un rappel. Tout le monde ne veut pas etre prevenu
# d'un semis a l'abri, mais presque personne ne veut rater une recolte.
CONF_NOTIFY_ETAPES = "notify_etapes"

# Un seul message groupe, plutot qu'une notification par plante : au printemps,
# cinq rappels le meme matin, c'est cinq rappels qu'on balaie sans lire.
CONF_NOTIFY_RESUME = "notify_resume"

# Relance pendant la fenetre de recolte, en jours (0 = une seule fois). Une
# courgette se cueille tous les deux jours : prevenir une fois ne sert a rien.
CONF_NOTIFY_RECOLTE_RECURRENCE = "notify_recolte_recurrence"

# Masquer les plantes terminees ou perdues dans « Mon potager ».
CONF_MASQUER_TERMINEES = "masquer_terminees"

# --- Arrosage -----------------------------------------------------------------

# Le suivi d'arrosage s'active globalement. Un potager entierement en pleine
# terre, sous climat humide, n'en a pas forcement l'usage.
CONF_ARROSAGE_ACTIF = "arrosage_actif"

# Bouguenais (44), zone USDA 9a, climat oceanique.
DEFAUT_GELEES_DERNIERE = "04-15"
DEFAUT_GELEES_PREMIERE = "11-15"
DEFAUT_NOTIFY_HEURE = "08:00:00"
DEFAUT_RAPPEL_JOURS = 3
DEFAUT_NOTIFY_RECOLTE_RECURRENCE = 0
DEFAUT_NOTIFY_RESUME = False
DEFAUT_MASQUER_TERMINEES = False
DEFAUT_ARROSAGE_ACTIF = True

# Par defaut on notifie tout : mieux vaut desactiver ce qui derange que
# decouvrir en juillet qu'un rappel n'est jamais parti.
ETAPES_NOTIFIABLES = (
    "semis_interieur",
    "semis_direct",
    "repiquage",
    "plantation",
    "recolte",
)

ZONE_PLEINE_TERRE = "pleine-terre"

# `abritee` : serre, chassis, pots. Ces zones sechent toute l'annee, donc
# l'arrosage y est rappele meme en hiver. En pleine terre, aucun rappel entre
# la premiere et la derniere gelee : personne n'arrose son jardin en decembre.
ZONES_DEFAUT: list[dict] = [
    {"id": ZONE_PLEINE_TERRE, "nom": "Pleine terre", "decalage_jours": 0},
    {"id": "serre", "nom": "Serre", "decalage_jours": -21, "abritee": True},
    {"id": "chassis", "nom": "Chassis / tunnel", "decalage_jours": -10,
     "abritee": True},
    {"id": "balcon", "nom": "Balcon / pots", "decalage_jours": 0, "abritee": True},
]

# Caracteristique deduite pour les zones d'origine, quand un stockage anterieur
# a l'arrosage ne la porte pas encore.
TRAITS_ZONES_CONNUES = {
    "serre": {"abritee": True},
    "chassis": {"abritee": True},
    "balcon": {"abritee": True},
}

# --- Services -----------------------------------------------------------------

SERVICE_AJOUTER_PLANTE = "ajouter_plante"
SERVICE_RETIRER_PLANTE = "retirer_plante"
SERVICE_MARQUER_SEME = "marquer_seme"
SERVICE_MARQUER_REPIQUE = "marquer_repique"
SERVICE_MARQUER_RECOLTE = "marquer_recolte"
SERVICE_MARQUER_PERDU = "marquer_perdu"
SERVICE_MARQUER_TERMINE = "marquer_termine"
SERVICE_ARROSER = "marquer_arrose"
SERVICE_RESSEMER = "ressemer"
SERVICE_ANNULER = "annuler_dernier_evenement"
SERVICE_RAFRAICHIR = "rafraichir"

# --- Evenements du bus -------------------------------------------------------

EVENT_JARDIN_MAJ = f"{DOMAIN}_jardin_maj"

# --- Catalogue personnel ------------------------------------------------------

# Prefixe des fiches ajoutees par l'utilisateur, pour ne jamais les confondre
# avec les 108 fiches livrees ni risquer d'ecraser l'une d'elles.
PREFIXE_PERSO = "perso-"

# Preselections climatiques : eviter de demander a froid une date de gelee.
PRESETS_CLIMAT: dict[str, dict[str, str]] = {
    "oceanique": {"derniere": "04-15", "premiere": "11-15"},
    "nord_est": {"derniere": "05-05", "premiere": "10-20"},
    "midi": {"derniere": "03-20", "premiere": "12-05"},
    "montagne": {"derniere": "05-25", "premiere": "10-01"},
}
PRESET_PERSONNALISE = "personnalise"
