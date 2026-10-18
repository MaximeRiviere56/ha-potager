"""Table compacte des cultures, compilee en data/catalog.json.

Pourquoi une table et pas du JSON ecrit a la main : 100 cultures x 25 champs
tiennent ici en une ligne chacune, les valeurs par defaut sont appliquees une
seule fois, et ajouter une culture reste une ligne a ecrire.

Les fenetres ne contiennent JAMAIS de mois en dur : chaque offset est un nombre
de jours par rapport a la derniere gelee de printemps ("derniere") ou a la
premiere gelee d'automne ("premiere"). Le calendrier devient ainsi juste partout.
Seules les perennes declarent une recolte a date fixe, puisqu'elle ne depend
plus d'un semis.

cycle = (jours_semis_a_repiquage, jours_semis_a_recolte,
         jours_plantation_a_recolte, duree_recolte_jours)
"""

from __future__ import annotations

CULTURES: list[dict] = []


def C(
    cid, nom, sci, famille, cat, emoji, *,
    expo="plein-soleil", eau="moyen", freq=4, sol="ordinaire, bien drainé",
    espacement=30, prof=None, diff=2, gel=True, tmin=None, perenne=False,
    semis_int=None, semis_dir=None, plantation=None, recolte=None,
    anchor_si="derniere", anchor_sd="derniere", anchor_pl="derniere",
    cycle=(None, None, None, 30),
    eau_notes="", aime=(), evite=(), conseils=(),
):
    ancrages = {"derniere": "gelees_derniere", "premiere": "gelees_premiere"}

    def fen(valeur, ancrage):
        offset, duree = valeur
        return {
            "ancrage": ancrages[ancrage],
            "offset_jours": offset,
            "duree_jours": duree,
        }

    fenetres: dict[str, dict] = {}
    if semis_int:
        fenetres["semis_interieur"] = fen(semis_int, anchor_si)
    if semis_dir:
        fenetres["semis_direct"] = fen(semis_dir, anchor_sd)
    if plantation:
        fenetres["plantation"] = fen(plantation, anchor_pl)
    if recolte:
        jour, duree = recolte
        fenetres["recolte"] = {
            "ancrage": "date_fixe",
            "date": jour,
            "duree_jours": duree,
        }

    repiquage, semis_recolte, plant_recolte, duree_recolte = cycle
    bloc_cycle: dict[str, int] = {"duree_recolte_jours": duree_recolte}
    if repiquage:
        bloc_cycle["jours_semis_a_repiquage"] = repiquage
    if semis_recolte:
        bloc_cycle["jours_semis_a_recolte"] = semis_recolte
    if plant_recolte:
        bloc_cycle["jours_plantation_a_recolte"] = plant_recolte

    fiche = {
        "id": cid,
        "nom": nom,
        "nom_scientifique": sci,
        "famille": famille,
        "categorie": cat,
        "emoji": emoji,
        "difficulte": diff,
        "exposition": expo,
        "arrosage": {"besoin": eau, "frequence_jours": freq, "notes": eau_notes},
        "sol": sol,
        "espacement_cm": espacement,
        "rusticite": {"gel": gel, "temp_min_c": tmin},
        "fenetres": fenetres,
        "cycle": bloc_cycle,
        "associations": {"aime": list(aime), "evite": list(evite)},
        "conseils": list(conseils),
    }
    if prof is not None:
        fiche["profondeur_semis_cm"] = prof
    if perenne:
        fiche["perenne"] = True
    CULTURES.append(fiche)
    return fiche


SOL_RICHE = "riche en humus, frais et bien drainé"
SOL_LEGER = "léger, meuble, sans cailloux"
SOL_ORDINAIRE = "ordinaire, bien drainé"

# =============================================================================
# Légumes-fruits
# =============================================================================

C("tomate", "Tomate", "Solanum lycopersicum", "Solanacées", "legume-fruit", "🍅",
  eau="eleve", freq=2, sol=SOL_RICHE, espacement=60, prof=0.5, diff=2, gel=False, tmin=5,
  semis_int=(-60, 30), plantation=(7, 30), cycle=(45, 110, 75, 90),
  eau_notes="Au pied, jamais sur le feuillage : c'est ainsi qu'arrive le mildiou.",
  aime=["basilic", "oeillet-inde", "carotte", "persil"],
  evite=["pomme-de-terre", "fenouil-bulbeux", "chou-cabus"],
  conseils=["Tailler les gourmands une fois par semaine",
            "Tuteurer dès la plantation, pas après",
            "Pailler dès juin pour stabiliser l'humidité"])

C("tomate-cerise", "Tomate cerise", "Solanum lycopersicum var. cerasiforme", "Solanacées",
  "legume-fruit", "🍅", eau="eleve", freq=2, sol=SOL_RICHE, espacement=50, prof=0.5,
  diff=1, gel=False, tmin=5, semis_int=(-60, 30), plantation=(7, 30), cycle=(45, 100, 70, 100),
  eau_notes="Plus tolérante que la grosse tomate, mais garder le sol frais.",
  aime=["basilic", "oeillet-inde"], evite=["pomme-de-terre", "fenouil-bulbeux"],
  conseils=["Se passe de taille si elle est bien tuteurée", "Idéale en pot sur un balcon"])

C("poivron", "Poivron", "Capsicum annuum", "Solanacées", "legume-fruit", "🫑",
  eau="moyen", freq=3, sol=SOL_RICHE, espacement=50, prof=0.5, diff=3, gel=False, tmin=10,
  semis_int=(-75, 30), plantation=(15, 25), cycle=(55, 130, 90, 70),
  eau_notes="Régulier et sans excès ; craint l'eau stagnante.",
  aime=["basilic", "carotte", "oignon-jaune"], evite=["haricot-nain", "fenouil-bulbeux"],
  conseils=["Chaleur indispensable : attendre un sol à 15 °C",
            "Pincer la première fleur pour renforcer le plant"])

C("piment", "Piment", "Capsicum annuum", "Solanacées", "legume-fruit", "🌶️",
  eau="moyen", freq=3, sol=SOL_RICHE, espacement=45, prof=0.5, diff=3, gel=False, tmin=10,
  semis_int=(-80, 30), plantation=(18, 25), cycle=(55, 135, 95, 80),
  eau_notes="Laisser sécher légèrement entre deux arrosages : le piment gagne en force.",
  aime=["basilic", "tomate"], evite=["fenouil-bulbeux"],
  conseils=["Semis très précoce indispensable sous nos latitudes",
            "Se cultive très bien en pot à rentrer l'hiver"])

C("aubergine", "Aubergine", "Solanum melongena", "Solanacées", "legume-fruit", "🍆",
  eau="eleve", freq=2, sol=SOL_RICHE, espacement=60, prof=0.5, diff=3, gel=False, tmin=12,
  semis_int=(-80, 30), plantation=(18, 25), cycle=(55, 140, 95, 70),
  eau_notes="Gourmande en eau dès la formation des fruits.",
  aime=["haricot-nain", "thym", "oeillet-inde"], evite=["pomme-de-terre"],
  conseils=["Tuteurer : les fruits sont lourds", "Limiter à 4-5 fruits par plant"])

C("courgette", "Courgette", "Cucurbita pepo", "Cucurbitacées", "legume-fruit", "🥒",
  eau="eleve", freq=2, sol=SOL_RICHE, espacement=100, prof=2, diff=1, gel=False, tmin=10,
  semis_int=(-30, 20), semis_dir=(15, 45), plantation=(15, 30), cycle=(28, 60, 50, 90),
  eau_notes="Beaucoup d'eau, au pied, sans mouiller les feuilles.",
  aime=["haricot-nain", "mais-doux", "capucine"], evite=["pomme-de-terre", "concombre"],
  conseils=["Récolter jeune et souvent : un plant freine dès qu'un fruit grossit",
            "Deux plants suffisent pour une famille"])

C("concombre", "Concombre", "Cucumis sativus", "Cucurbitacées", "legume-fruit", "🥒",
  eau="eleve", freq=2, sol=SOL_RICHE, espacement=80, prof=2, diff=2, gel=False, tmin=12,
  semis_int=(-30, 20), plantation=(15, 30), cycle=(28, 65, 55, 70),
  eau_notes="Un manque d'eau rend les fruits amers.",
  aime=["haricot-a-rames", "laitue", "aneth"], evite=["pomme-de-terre", "courgette"],
  conseils=["Palisser à la verticale : fruits plus droits, moins de maladies"])

C("cornichon", "Cornichon", "Cucumis sativus", "Cucurbitacées", "legume-fruit", "🥒",
  eau="eleve", freq=2, sol=SOL_RICHE, espacement=70, prof=2, diff=2, gel=False, tmin=12,
  semis_int=(-25, 20), semis_dir=(15, 40), cycle=(25, 60, 50, 60),
  eau_notes="Arrosage régulier, sinon les fruits avortent.",
  aime=["aneth", "haricot-nain"], evite=["pomme-de-terre"],
  conseils=["Cueillir tous les deux jours au plus fort de la production"])

C("courge-butternut", "Courge butternut", "Cucurbita moschata", "Cucurbitacées",
  "legume-fruit", "🎃", eau="moyen", freq=4, sol=SOL_RICHE, espacement=120, prof=3,
  diff=1, gel=False, tmin=10, semis_int=(-30, 20), plantation=(15, 30), cycle=(28, 120, 100, 45),
  eau_notes="Arrosages copieux mais espacés ; couper l'eau à l'approche de la récolte.",
  aime=["mais-doux", "haricot-a-rames", "capucine"], evite=["pomme-de-terre"],
  conseils=["Récolter quand le pédoncule est sec et liégeux",
            "Laisser ressuyer une semaine au soleil avant de stocker"])

C("potimarron", "Potimarron", "Cucurbita maxima", "Cucurbitacées", "legume-fruit", "🎃",
  eau="moyen", freq=4, sol=SOL_RICHE, espacement=120, prof=3, diff=1, gel=False, tmin=10,
  semis_int=(-30, 20), plantation=(15, 30), cycle=(28, 110, 95, 45),
  eau_notes="Comme la butternut : copieux et espacés.",
  aime=["mais-doux", "haricot-a-rames"], evite=["pomme-de-terre"],
  conseils=["Se conserve tout l'hiver dans une pièce fraîche et sèche"])

C("citrouille", "Citrouille", "Cucurbita maxima", "Cucurbitacées", "legume-fruit", "🎃",
  eau="moyen", freq=4, sol=SOL_RICHE, espacement=150, prof=3, diff=1, gel=False, tmin=10,
  semis_int=(-30, 20), plantation=(15, 30), cycle=(28, 115, 100, 45),
  eau_notes="Volume d'eau important, surtout pendant le grossissement.",
  aime=["mais-doux", "capucine"], evite=["pomme-de-terre"],
  conseils=["Glisser une planchette sous le fruit pour éviter qu'il pourrisse"])

C("melon", "Melon", "Cucumis melo", "Cucurbitacées", "legume-fruit", "🍈",
  eau="moyen", freq=3, sol=SOL_RICHE, espacement=100, prof=2, diff=3, gel=False, tmin=14,
  semis_int=(-45, 25), plantation=(20, 25), cycle=(35, 115, 90, 40),
  eau_notes="Réduire fortement l'eau dix jours avant la récolte : c'est ce qui fait le sucre.",
  aime=["mais-doux", "capucine"], evite=["concombre", "pomme-de-terre"],
  conseils=["Pailler avec une bâche ou de l'ardoise pour accumuler la chaleur",
            "Récolter quand le pédoncule se craquelle et que le parfum monte"])

C("pasteque", "Pastèque", "Citrullus lanatus", "Cucurbitacées", "legume-fruit", "🍉",
  eau="moyen", freq=3, sol=SOL_RICHE, espacement=140, prof=2, diff=3, gel=False, tmin=15,
  semis_int=(-45, 25), plantation=(22, 25), cycle=(35, 125, 100, 35),
  eau_notes="Comme le melon : couper l'eau en fin de cycle.",
  aime=["mais-doux"], evite=["pomme-de-terre"],
  conseils=["Exige un été chaud : réserver la place la plus abritée du jardin"])

C("mais-doux", "Maïs doux", "Zea mays", "Poacées", "legume-fruit", "🌽",
  eau="eleve", freq=3, sol=SOL_RICHE, espacement=40, prof=3, diff=1, gel=False, tmin=10,
  semis_dir=(15, 45), cycle=(None, 90, None, 25),
  eau_notes="Très assoiffé à la floraison : ne jamais laisser sécher à ce stade.",
  aime=["courgette", "haricot-a-rames", "potimarron"], evite=["betterave", "celeri-branche"],
  conseils=["Semer en bloc carré, jamais en ligne unique : la pollinisation en dépend",
            "Récolter quand les soies brunissent"])

C("physalis", "Physalis", "Physalis peruviana", "Solanacées", "legume-fruit", "🏮",
  eau="moyen", freq=3, sol=SOL_ORDINAIRE, espacement=80, prof=0.5, diff=2, gel=False, tmin=8,
  semis_int=(-60, 30), plantation=(15, 25), cycle=(45, 130, 95, 60),
  eau_notes="Supporte bien un léger stress hydrique.",
  aime=["tomate", "basilic"], evite=[],
  conseils=["Les fruits sont mûrs quand le calice est sec et qu'ils tombent seuls"])

# =============================================================================
# Légumes-gousses
# =============================================================================

C("haricot-nain", "Haricot vert nain", "Phaseolus vulgaris", "Fabacées", "legume-gousse", "🫘",
  eau="moyen", freq=3, sol=SOL_ORDINAIRE, espacement=10, prof=3, diff=1, gel=False, tmin=10,
  semis_dir=(15, 90), cycle=(None, 55, None, 40),
  eau_notes="Ne pas arroser avant la levée, puis régulièrement à la floraison.",
  aime=["carotte", "laitue", "courgette", "fraisier"], evite=["ail-blanc", "oignon-jaune", "echalote", "poireau"],
  conseils=["Semer tous les 15 jours jusqu'en juillet pour étaler la récolte",
            "Récolter tous les deux jours : un haricot oublié stoppe le plant"])

C("haricot-a-rames", "Haricot à rames", "Phaseolus vulgaris", "Fabacées", "legume-gousse", "🫘",
  eau="moyen", freq=3, sol=SOL_ORDINAIRE, espacement=15, prof=3, diff=1, gel=False, tmin=10,
  semis_dir=(20, 75), cycle=(None, 65, None, 60),
  eau_notes="Régulier dès la floraison.",
  aime=["mais-doux", "courgette", "laitue"], evite=["ail-blanc", "oignon-jaune", "poireau", "betterave"],
  conseils=["Installer les tuteurs avant de semer", "Produit plus longtemps que le nain"])

C("haricot-sec", "Haricot sec", "Phaseolus vulgaris", "Fabacées", "legume-gousse", "🫘",
  eau="faible", freq=6, sol=SOL_ORDINAIRE, espacement=12, prof=3, diff=1, gel=False, tmin=10,
  semis_dir=(20, 60), cycle=(None, 95, None, 25),
  eau_notes="Sobre ; arrêter l'arrosage dès que les gousses jaunissent.",
  aime=["carotte", "mais-doux"], evite=["ail-blanc", "oignon-jaune"],
  conseils=["Arracher les plants entiers et les faire sécher tête en bas"])

C("petit-pois", "Petit pois", "Pisum sativum", "Fabacées", "legume-gousse", "🫛",
  eau="moyen", freq=4, sol=SOL_ORDINAIRE, espacement=5, prof=3, diff=1, gel=True, tmin=-5,
  semis_dir=(-60, 60), cycle=(None, 90, None, 30),
  eau_notes="Craint la sécheresse à la floraison.",
  aime=["carotte", "radis", "navet", "laitue"], evite=["ail-blanc", "oignon-jaune", "echalote"],
  conseils=["Supporte le froid : un semis de février donne la première récolte",
            "Ramer dès 15 cm de hauteur"])

C("pois-mange-tout", "Pois mange-tout", "Pisum sativum", "Fabacées", "legume-gousse", "🫛",
  eau="moyen", freq=4, sol=SOL_ORDINAIRE, espacement=5, prof=3, diff=1, gel=True, tmin=-5,
  semis_dir=(-55, 60), cycle=(None, 80, None, 35),
  eau_notes="Comme le petit pois.",
  aime=["carotte", "radis", "laitue"], evite=["ail-blanc", "oignon-jaune"],
  conseils=["Récolter les gousses bien plates, avant que les grains ne se forment"])

C("feve", "Fève", "Vicia faba", "Fabacées", "legume-gousse", "🫘",
  eau="moyen", freq=5, sol=SOL_ORDINAIRE, espacement=20, prof=5, diff=1, gel=True, tmin=-8,
  semis_dir=(-15, 45), anchor_sd="premiere", cycle=(None, 180, None, 30),
  eau_notes="Peu exigeante, l'hiver s'en charge.",
  aime=["pomme-de-terre", "laitue", "epinard"], evite=["ail-blanc", "oignon-jaune", "betterave"],
  conseils=["Semée en novembre, elle passe l'hiver et devance les pucerons noirs",
            "Pincer les têtes dès l'apparition des premiers pucerons"])

C("pois-chiche", "Pois chiche", "Cicer arietinum", "Fabacées", "legume-gousse", "🫘",
  eau="faible", freq=8, sol="léger, calcaire, très drainé", espacement=15, prof=4,
  diff=2, gel=True, tmin=-4, semis_dir=(0, 30), cycle=(None, 120, None, 20),
  eau_notes="Résiste très bien au sec : ne pas arroser hors période de semis.",
  aime=["carotte", "sarriette"], evite=["ail-blanc", "oignon-jaune"],
  conseils=["Redoute l'excès d'eau plus que la sécheresse"])

# =============================================================================
# Légumes-racines et tubercules
# =============================================================================

C("carotte", "Carotte", "Daucus carota", "Apiacées", "legume-racine", "🥕",
  eau="moyen", freq=4, sol=SOL_LEGER, espacement=5, prof=0.5, diff=2, gel=True, tmin=-5,
  semis_dir=(-45, 150), cycle=(None, 100, None, 60),
  eau_notes="Humidité constante jusqu'à la levée, qui est lente (15 à 20 jours).",
  aime=["poireau", "oignon-jaune", "radis", "laitue", "petit-pois"], evite=["aneth", "betterave"],
  conseils=["Semer clair et éclaircir sans pitié : une carotte serrée reste un fil",
            "Le poireau voisin éloigne la mouche de la carotte"])

C("radis", "Radis", "Raphanus sativus", "Brassicacées", "legume-racine", "🥗",
  eau="eleve", freq=2, sol=SOL_LEGER, espacement=4, prof=1, diff=1, gel=True, tmin=-4,
  semis_dir=(-30, 150), cycle=(None, 25, None, 14),
  eau_notes="Jamais sec : un radis qui a soif devient piquant et creux.",
  aime=["carotte", "laitue", "petit-pois", "epinard"], evite=["concombre", "chou-cabus"],
  conseils=["Le plus rapide du potager : parfait pour débuter",
            "Semer une petite ligne tous les 10 jours plutôt qu'une grande d'un coup"])

C("radis-noir", "Radis noir d'hiver", "Raphanus sativus", "Brassicacées", "legume-racine", "🥗",
  eau="moyen", freq=3, sol=SOL_LEGER, espacement=15, prof=2, diff=1, gel=True, tmin=-8,
  semis_dir=(-90, 45), anchor_sd="premiere", cycle=(None, 70, None, 60),
  eau_notes="Régulier, sinon la racine se fend.",
  aime=["carotte", "laitue"], evite=["chou-cabus"],
  conseils=["Semé en août, il se récolte tout l'automne et se garde en cave"])

C("navet", "Navet", "Brassica rapa", "Brassicacées", "legume-racine", "🥗",
  eau="moyen", freq=3, sol=SOL_ORDINAIRE, espacement=12, prof=1, diff=1, gel=True, tmin=-6,
  semis_dir=(-20, 120), cycle=(None, 60, None, 30),
  eau_notes="Un arrosage irrégulier le rend fibreux.",
  aime=["petit-pois", "laitue"], evite=["chou-cabus", "radis"],
  conseils=["Récolter jeune, à la taille d'une balle de golf"])

C("betterave", "Betterave rouge", "Beta vulgaris", "Amaranthacées", "legume-racine", "🥗",
  eau="moyen", freq=4, sol=SOL_ORDINAIRE, espacement=12, prof=2, diff=1, gel=True, tmin=-4,
  semis_dir=(-15, 100), cycle=(None, 90, None, 45),
  eau_notes="Modéré et régulier.",
  aime=["laitue", "oignon-jaune", "chou-cabus"], evite=["haricot-a-rames", "mais-doux"],
  conseils=["Chaque graine donne plusieurs plants : éclaircir à 10 cm"])

C("panais", "Panais", "Pastinaca sativa", "Apiacées", "legume-racine", "🥕",
  eau="moyen", freq=5, sol=SOL_LEGER, espacement=15, prof=1, diff=2, gel=True, tmin=-15,
  semis_dir=(-30, 60), cycle=(None, 150, None, 90),
  eau_notes="Peu d'arrosage une fois installé, la racine va chercher loin.",
  aime=["radis", "laitue"], evite=["carotte", "celeri-rave"],
  conseils=["Le gel améliore son goût : le laisser en terre et récolter au besoin",
            "Graines à renouveler chaque année, elles perdent vite leur pouvoir germinatif"])

C("celeri-rave", "Céleri-rave", "Apium graveolens var. rapaceum", "Apiacées", "legume-racine", "🥬",
  eau="eleve", freq=2, sol=SOL_RICHE, espacement=35, prof=0.2, diff=3, gel=True, tmin=-5,
  semis_int=(-75, 30), plantation=(20, 30), cycle=(60, None, 120, 45),
  eau_notes="Jamais à sec : c'est la culture la plus assoiffée du potager.",
  aime=["poireau", "tomate", "haricot-nain"], evite=["carotte", "panais", "persil"],
  conseils=["Dégager la base de la boule en fin d'été pour qu'elle grossisse"])

C("salsifis", "Salsifis", "Tragopogon porrifolius", "Astéracées", "legume-racine", "🥕",
  eau="moyen", freq=5, sol=SOL_LEGER, espacement=10, prof=2, diff=2, gel=True, tmin=-12,
  semis_dir=(-15, 60), cycle=(None, 160, None, 60),
  eau_notes="Sobre après la levée.",
  aime=["carotte", "oignon-jaune"], evite=[],
  conseils=["Se récolte de novembre à mars, au fur et à mesure des besoins"])

C("pomme-de-terre", "Pomme de terre", "Solanum tuberosum", "Solanacées", "legume-racine", "🥔",
  eau="moyen", freq=4, sol=SOL_ORDINAIRE, espacement=35, prof=10, diff=1, gel=False, tmin=2,
  plantation=(-30, 45), cycle=(None, None, 100, 45),
  eau_notes="Régulier à la floraison, moment où les tubercules se forment.",
  aime=["haricot-nain", "chou-cabus", "feve", "epinard"],
  evite=["tomate", "aubergine", "courgette", "potimarron"],
  conseils=["Butter dès que les plants atteignent 20 cm",
            "Ne jamais replanter au même endroit avant 4 ans"])

C("patate-douce", "Patate douce", "Ipomoea batatas", "Convolvulacées", "legume-racine", "🍠",
  eau="moyen", freq=4, sol=SOL_LEGER, espacement=80, diff=2, gel=False, tmin=12,
  plantation=(20, 30), cycle=(None, None, 130, 30),
  eau_notes="Supporte le sec une fois installée.",
  aime=["haricot-nain"], evite=["pomme-de-terre"],
  conseils=["Planter les boutures quand le sol atteint 15 °C",
            "Récolter avant les premières gelées, le feuillage est très sensible"])

C("rutabaga", "Rutabaga", "Brassica napobrassica", "Brassicacées", "legume-racine", "🥗",
  eau="moyen", freq=4, sol=SOL_ORDINAIRE, espacement=25, prof=2, diff=1, gel=True, tmin=-10,
  semis_dir=(30, 45), cycle=(None, 100, None, 60),
  eau_notes="Régulier, il n'aime pas les à-coups.",
  aime=["petit-pois", "laitue"], evite=["chou-cabus", "navet"],
  conseils=["Se garde en terre tout l'hiver sous un paillage"])

C("topinambour", "Topinambour", "Helianthus tuberosus", "Astéracées", "legume-racine", "🥔",
  eau="faible", freq=8, sol=SOL_ORDINAIRE, espacement=60, prof=10, diff=1, gel=True, tmin=-20,
  plantation=(-45, 45), cycle=(None, None, 210, 120),
  eau_notes="Se débrouille seul, même en sol pauvre.",
  aime=[], evite=["pomme-de-terre"],
  conseils=["Très envahissant : lui réserver un coin dont il ne sortira pas",
            "Récolter au fur et à mesure, il ne se conserve pas hors de terre"])

C("crosne", "Crosne du Japon", "Stachys affinis", "Lamiacées", "legume-racine", "🥔",
  eau="moyen", freq=5, sol=SOL_LEGER, espacement=40, prof=8, diff=2, gel=True, tmin=-15,
  plantation=(-30, 30), cycle=(None, None, 210, 90),
  eau_notes="Arroser en été pour grossir les tubercules.",
  aime=[], evite=[],
  conseils=["Récolter après les premières gelées et ne pas chercher à les conserver"])

C("raifort", "Raifort", "Armoracia rusticana", "Brassicacées", "legume-racine", "🌿",
  eau="faible", freq=7, sol=SOL_LEGER, espacement=50, diff=1, gel=True, tmin=-20, perenne=True,
  plantation=(-45, 45), recolte=("10-15", 120), cycle=(None, None, None, 120),
  eau_notes="Rustique et sobre.",
  aime=["pomme-de-terre"], evite=[],
  conseils=["Aussi envahissant que le topinambour : le cantonner dans un bac"])

# =============================================================================
# Légumes-bulbes
# =============================================================================

C("oignon-jaune", "Oignon jaune", "Allium cepa", "Amaryllidacées", "legume-bulbe", "🧅",
  eau="faible", freq=7, sol=SOL_LEGER, espacement=12, prof=1, diff=1, gel=True, tmin=-8,
  semis_dir=(-60, 45), cycle=(None, 150, None, 30),
  eau_notes="Très peu d'eau : l'excès fait pourrir le bulbe.",
  aime=["carotte", "betterave", "laitue", "fraisier"], evite=["haricot-nain", "petit-pois", "feve"],
  conseils=["Coucher le feuillage en fin de cycle pour hâter la maturité",
            "Faire sécher au soleil une semaine avant de stocker"])

C("oignon-blanc", "Oignon blanc", "Allium cepa", "Amaryllidacées", "legume-bulbe", "🧅",
  eau="faible", freq=6, sol=SOL_LEGER, espacement=10, prof=1, diff=1, gel=True, tmin=-8,
  semis_dir=(-60, 30), anchor_sd="premiere", cycle=(None, 210, None, 45),
  eau_notes="Comme le jaune : sobre.",
  aime=["carotte", "laitue"], evite=["haricot-nain", "petit-pois"],
  conseils=["Semé en août, il se consomme frais au printemps suivant"])

C("echalote", "Échalote", "Allium cepa var. aggregatum", "Amaryllidacées", "legume-bulbe", "🧅",
  eau="faible", freq=7, sol=SOL_LEGER, espacement=15, prof=3, diff=1, gel=True, tmin=-10,
  plantation=(-75, 60), cycle=(None, None, 120, 21),
  eau_notes="Presque aucun arrosage.",
  aime=["carotte", "betterave", "fraisier"], evite=["haricot-nain", "petit-pois", "feve"],
  conseils=["Dicton fiable : plantée en février, récoltée en juillet",
            "Ne pas enterrer la pointe, elle doit affleurer"])

C("ail-blanc", "Ail blanc", "Allium sativum", "Amaryllidacées", "legume-bulbe", "🧄",
  eau="faible", freq=10, sol=SOL_LEGER, espacement=12, prof=3, diff=1, gel=True, tmin=-15,
  plantation=(-30, 45), anchor_pl="premiere", cycle=(None, None, 240, 21),
  eau_notes="Ne jamais arroser : l'ail déteste l'humidité.",
  aime=["carotte", "betterave", "fraisier", "tomate"], evite=["haricot-nain", "petit-pois", "chou-cabus"],
  conseils=["Planté en octobre-novembre, il profite du froid pour se diviser",
            "Couper les fleurs pour que le bulbe grossisse"])

C("ail-rose", "Ail rose", "Allium sativum", "Amaryllidacées", "legume-bulbe", "🧄",
  eau="faible", freq=10, sol=SOL_LEGER, espacement=12, prof=3, diff=1, gel=True, tmin=-12,
  plantation=(-75, 40), cycle=(None, None, 150, 21),
  eau_notes="Aucun arrosage.",
  aime=["carotte", "fraisier", "tomate"], evite=["haricot-nain", "petit-pois"],
  conseils=["Se plante en février, contrairement à l'ail blanc"])

C("poireau", "Poireau", "Allium ampeloprasum", "Amaryllidacées", "legume-bulbe", "🥬",
  eau="moyen", freq=4, sol=SOL_RICHE, espacement=15, prof=1, diff=2, gel=True, tmin=-15,
  semis_int=(-75, 45), plantation=(30, 60), cycle=(70, None, 120, 120),
  eau_notes="Régulier, surtout après la plantation.",
  aime=["carotte", "celeri-rave", "fraisier", "tomate"], evite=["haricot-nain", "petit-pois"],
  conseils=["Raccourcir racines et feuilles de moitié avant de planter",
            "Butter progressivement pour allonger le blanc"])

C("ciboule", "Ciboule", "Allium fistulosum", "Amaryllidacées", "legume-bulbe", "🌿",
  eau="moyen", freq=5, sol=SOL_ORDINAIRE, espacement=10, prof=1, diff=1, gel=True, tmin=-12,
  semis_dir=(-30, 90), cycle=(None, 90, None, 150),
  eau_notes="Modéré.",
  aime=["carotte", "fraisier"], evite=["haricot-nain", "petit-pois"],
  conseils=["Se coupe comme de la ciboulette et repousse toute la saison"])

# =============================================================================
# Légumes-feuilles
# =============================================================================

C("laitue", "Laitue", "Lactuca sativa", "Astéracées", "legume-feuille", "🥬",
  eau="eleve", freq=2, sol=SOL_RICHE, espacement=25, prof=0.5, diff=1, gel=True, tmin=-4,
  semis_int=(-60, 30), semis_dir=(-15, 150), cycle=(30, 60, 45, 30),
  eau_notes="Le matin, au pied : l'eau sur les feuilles au soleil les brûle.",
  aime=["carotte", "radis", "fraisier", "haricot-nain"], evite=["persil", "celeri-branche"],
  conseils=["Semer 6 à 8 pieds tous les 15 jours plutôt qu'une planche entière",
            "Ne pas enterrer la graine : elle a besoin de lumière pour germer"])

C("laitue-hiver", "Laitue d'hiver", "Lactuca sativa", "Astéracées", "legume-feuille", "🥬",
  eau="moyen", freq=4, sol=SOL_RICHE, espacement=25, prof=0.5, diff=2, gel=True, tmin=-10,
  semis_dir=(-75, 40), anchor_sd="premiere", cycle=(None, 150, None, 45),
  eau_notes="Modéré, l'hiver fournit l'essentiel.",
  aime=["mache", "epinard"], evite=["persil"],
  conseils=["Variétés 'Merveille d'hiver' ou 'Rougette' : les seules à passer le froid"])

C("mache", "Mâche", "Valerianella locusta", "Caprifoliacées", "legume-feuille", "🥬",
  eau="moyen", freq=4, sol=SOL_ORDINAIRE, espacement=10, prof=0.5, diff=1, gel=True, tmin=-15,
  semis_dir=(-75, 60), anchor_sd="premiere", cycle=(None, 90, None, 60),
  eau_notes="Garder frais jusqu'à la levée, puis l'oublier.",
  aime=["laitue-hiver", "epinard", "radis"], evite=[],
  conseils=["Semer sur sol tassé, surtout pas labouré : elle aime la terre ferme",
            "Plombez le semis en tapotant avec le dos du râteau"])

C("epinard", "Épinard", "Spinacia oleracea", "Amaranthacées", "legume-feuille", "🥬",
  eau="eleve", freq=3, sol=SOL_RICHE, espacement=15, prof=2, diff=1, gel=True, tmin=-12,
  semis_dir=(-75, 45), anchor_sd="premiere", cycle=(None, 60, None, 60),
  eau_notes="Généreux : la sécheresse le fait monter en graines aussitôt.",
  aime=["fraisier", "chou-cabus", "radis"], evite=["betterave"],
  conseils=["Culture d'automne et de printemps : l'été le fait monter",
            "Couper les feuilles extérieures, le pied continue de produire"])

C("blette", "Blette (poirée)", "Beta vulgaris var. cicla", "Amaranthacées", "legume-feuille", "🥬",
  eau="moyen", freq=3, sol=SOL_RICHE, espacement=35, prof=2, diff=1, gel=True, tmin=-8,
  semis_dir=(-15, 90), cycle=(None, 60, None, 150),
  eau_notes="Régulier ; très tolérante par ailleurs.",
  aime=["carotte", "laitue", "chou-cabus"], evite=["betterave", "epinard"],
  conseils=["Un seul semis nourrit du printemps aux gelées",
            "Récolter feuille à feuille, jamais le pied entier"])

C("roquette", "Roquette", "Eruca vesicaria", "Brassicacées", "legume-feuille", "🥬",
  eau="moyen", freq=3, sol=SOL_ORDINAIRE, espacement=10, prof=0.5, diff=1, gel=True, tmin=-6,
  semis_dir=(-30, 150), cycle=(None, 40, None, 30),
  eau_notes="Régulier, sinon elle devient très piquante et monte.",
  aime=["laitue", "carotte"], evite=["chou-cabus"],
  conseils=["Pousse si vite qu'un semis de printemps et un d'automne suffisent"])

C("chou-cabus", "Chou pommé", "Brassica oleracea var. capitata", "Brassicacées", "legume-feuille", "🥬",
  eau="eleve", freq=3, sol=SOL_RICHE, espacement=50, prof=1, diff=2, gel=True, tmin=-8,
  semis_int=(-45, 30), plantation=(30, 45), cycle=(40, None, 90, 45),
  eau_notes="Soutenu pendant la formation de la pomme.",
  aime=["betterave", "laitue", "epinard", "aneth"], evite=["tomate", "fraisier", "ail-blanc"],
  conseils=["Poser une collerette en carton au pied contre la mouche du chou",
            "Un filet anti-insectes règle le problème des piérides une fois pour toutes"])

C("chou-rouge", "Chou rouge", "Brassica oleracea var. capitata f. rubra", "Brassicacées",
  "legume-feuille", "🥬", eau="eleve", freq=3, sol=SOL_RICHE, espacement=50, prof=1,
  diff=2, gel=True, tmin=-8, semis_int=(-45, 30), plantation=(30, 45), cycle=(40, None, 100, 45),
  eau_notes="Comme le chou pommé.",
  aime=["betterave", "laitue", "aneth"], evite=["tomate", "fraisier"],
  conseils=["Se conserve plusieurs mois en cave"])

C("chou-fleur", "Chou-fleur", "Brassica oleracea var. botrytis", "Brassicacées", "legume-feuille", "🥬",
  eau="eleve", freq=2, sol=SOL_RICHE, espacement=60, prof=1, diff=3, gel=True, tmin=-6,
  semis_int=(-30, 45), plantation=(45, 45), cycle=(40, None, 100, 30),
  eau_notes="Le plus exigeant des choux : un coup de sec et la pomme avorte.",
  aime=["betterave", "celeri-branche", "aneth"], evite=["tomate", "fraisier"],
  conseils=["Casser une feuille sur la pomme pour la garder blanche",
            "Récolter avant que les grains ne s'écartent"])

C("brocoli", "Brocoli", "Brassica oleracea var. italica", "Brassicacées", "legume-feuille", "🥦",
  eau="eleve", freq=3, sol=SOL_RICHE, espacement=50, prof=1, diff=2, gel=True, tmin=-8,
  semis_int=(-30, 45), plantation=(40, 45), cycle=(35, None, 85, 60),
  eau_notes="Régulier et généreux.",
  aime=["betterave", "laitue", "aneth"], evite=["tomate", "fraisier"],
  conseils=["Couper la tête centrale incite les rejets latéraux à se développer"])

C("chou-bruxelles", "Chou de Bruxelles", "Brassica oleracea var. gemmifera", "Brassicacées",
  "legume-feuille", "🥬", eau="moyen", freq=4, sol=SOL_RICHE, espacement=60, prof=1,
  diff=2, gel=True, tmin=-12, semis_int=(-30, 30), plantation=(45, 30), cycle=(40, None, 150, 90),
  eau_notes="Modéré ; le froid fait le reste.",
  aime=["betterave", "laitue"], evite=["tomate", "fraisier"],
  conseils=["Pincer la tête en septembre pour grossir les choux du bas",
            "Meilleur après une gelée"])

C("chou-kale", "Chou frisé (kale)", "Brassica oleracea var. sabellica", "Brassicacées",
  "legume-feuille", "🥬", eau="moyen", freq=4, sol=SOL_RICHE, espacement=45, prof=1,
  diff=1, gel=True, tmin=-15, semis_int=(-15, 45), plantation=(45, 45), cycle=(35, None, 80, 180),
  eau_notes="Peu exigeant, très résistant.",
  aime=["betterave", "laitue", "aneth"], evite=["tomate", "fraisier"],
  conseils=["Le plus facile et le plus rustique des choux : il produit tout l'hiver",
            "Cueillir les feuilles du bas, le pied continue de monter"])

C("chou-milan", "Chou de Milan", "Brassica oleracea var. sabauda", "Brassicacées",
  "legume-feuille", "🥬", eau="eleve", freq=3, sol=SOL_RICHE, espacement=55, prof=1,
  diff=2, gel=True, tmin=-12, semis_int=(-30, 40), plantation=(40, 50), cycle=(40, None, 110, 60),
  eau_notes="Soutenu à la formation de la pomme.",
  aime=["betterave", "laitue"], evite=["tomate", "fraisier"],
  conseils=["Variété d'hiver : se récolte de novembre à mars"])

C("chou-chinois", "Chou chinois (pak choï)", "Brassica rapa var. chinensis", "Brassicacées",
  "legume-feuille", "🥬", eau="eleve", freq=2, sol=SOL_RICHE, espacement=30, prof=1,
  diff=2, gel=True, tmin=-5, semis_dir=(-90, 40), anchor_sd="premiere", cycle=(None, 70, None, 30),
  eau_notes="Jamais sec, sinon il monte immédiatement.",
  aime=["laitue", "radis"], evite=["chou-cabus"],
  conseils=["Culture d'arrière-saison : semé en juillet-août, il ne monte pas"])

C("endive", "Endive (chicon)", "Cichorium intybus", "Astéracées", "legume-feuille", "🥬",
  eau="moyen", freq=4, sol=SOL_LEGER, espacement=12, prof=1, diff=3, gel=True, tmin=-8,
  semis_dir=(30, 30), cycle=(None, 160, None, 90),
  eau_notes="Régulier pendant la formation de la racine.",
  aime=["carotte", "oignon-jaune"], evite=[],
  conseils=["Deux temps : la racine au jardin l'été, le forçage à l'obscurité l'hiver",
            "Arracher les racines en novembre et les forcer en cave par lots"])

C("scarole", "Scarole", "Cichorium endivia", "Astéracées", "legume-feuille", "🥬",
  eau="moyen", freq=3, sol=SOL_RICHE, espacement=35, prof=0.5, diff=2, gel=True, tmin=-6,
  semis_dir=(45, 60), cycle=(None, 85, None, 45),
  eau_notes="Régulier ; au pied uniquement.",
  aime=["carotte", "radis"], evite=["persil"],
  conseils=["Lier les feuilles ou poser une assiette dessus pour blanchir le cœur"])

C("cresson-alenois", "Cresson alénois", "Lepidium sativum", "Brassicacées", "legume-feuille", "🌿",
  eau="eleve", freq=2, sol=SOL_ORDINAIRE, espacement=5, prof=0.5, diff=1, gel=True, tmin=-5,
  semis_dir=(-30, 150), cycle=(None, 30, None, 20),
  eau_notes="Toujours humide.",
  aime=["radis", "laitue"], evite=[],
  conseils=["Prêt en trois semaines : le plus rapide après le radis"])

C("pourpier", "Pourpier d'été", "Portulaca oleracea", "Portulacacées", "legume-feuille", "🌿",
  eau="faible", freq=6, sol=SOL_LEGER, espacement=15, prof=0.5, diff=1, gel=False, tmin=8,
  semis_dir=(15, 90), cycle=(None, 50, None, 60),
  eau_notes="Supporte très bien la sécheresse : c'est une plante grasse.",
  aime=["carotte", "tomate"], evite=[],
  conseils=["Pousse là où rien ne pousse, en plein cagnard"])

C("tetragone", "Tétragone (épinard d'été)", "Tetragonia tetragonoides", "Aizoacées",
  "legume-feuille", "🥬", eau="moyen", freq=4, sol=SOL_ORDINAIRE, espacement=50, prof=2,
  diff=1, gel=False, tmin=8, semis_dir=(15, 45), cycle=(None, 60, None, 120),
  eau_notes="Modéré, bien plus tolérante que l'épinard.",
  aime=["tomate", "haricot-nain"], evite=[],
  conseils=["La solution à l'épinard qui monte en été : elle ne monte pas"])

C("celeri-branche", "Céleri branche", "Apium graveolens var. dulce", "Apiacées", "legume-feuille", "🥬",
  eau="eleve", freq=2, sol=SOL_RICHE, espacement=30, prof=0.2, diff=3, gel=True, tmin=-4,
  semis_int=(-75, 30), plantation=(25, 30), cycle=(60, None, 100, 60),
  eau_notes="Jamais sec, jamais : c'est une plante de marais.",
  aime=["poireau", "chou-fleur", "tomate"], evite=["carotte", "persil", "mais-doux"],
  conseils=["Butter ou lier en fin de culture pour blanchir les côtes"])

C("fenouil-bulbeux", "Fenouil bulbeux", "Foeniculum vulgare var. azoricum", "Apiacées",
  "legume-feuille", "🥬", eau="moyen", freq=3, sol=SOL_RICHE, espacement=25, prof=1,
  diff=2, gel=True, tmin=-5, semis_dir=(30, 60), cycle=(None, 100, None, 30),
  eau_notes="Régulier, sinon il monte sans faire de bulbe.",
  aime=["laitue", "concombre"], evite=["tomate", "haricot-nain", "carotte", "coriandre"],
  conseils=["Semer après le solstice : semé trop tôt, il monte systématiquement",
            "Mauvais voisin pour presque tout : lui donner un coin à part"])

C("artichaut", "Artichaut", "Cynara scolymus", "Astéracées", "legume-feuille", "🌿",
  eau="moyen", freq=4, sol=SOL_RICHE, espacement=100, diff=2, gel=True, tmin=-8, perenne=True,
  plantation=(-30, 45), recolte=("06-01", 75), cycle=(None, None, None, 75),
  eau_notes="Généreux en été, surtout la première année.",
  aime=["feve", "laitue"], evite=[],
  conseils=["Pailler le pied l'hiver : c'est le gel qui tue les artichauts",
            "Productif 4 à 5 ans, puis diviser les œilletons"])

C("asperge", "Asperge", "Asparagus officinalis", "Asparagacées", "legume-feuille", "🌿",
  eau="moyen", freq=5, sol=SOL_LEGER, espacement=50, diff=3, gel=True, tmin=-15, perenne=True,
  plantation=(-60, 45), recolte=("04-15", 45), cycle=(None, None, None, 45),
  eau_notes="Modéré ; craint l'eau stagnante en hiver.",
  aime=["tomate", "persil"], evite=["ail-blanc", "oignon-jaune"],
  conseils=["Patience : aucune récolte les deux premières années, puis 15 ans de production",
            "Butter la griffe au printemps pour obtenir des asperges blanches"])

C("rhubarbe", "Rhubarbe", "Rheum rhabarbarum", "Polygonacées", "legume-feuille", "🌿",
  eau="eleve", freq=3, sol=SOL_RICHE, espacement=100, diff=1, gel=True, tmin=-20, perenne=True,
  plantation=(-15, 60), anchor_pl="premiere", recolte=("04-20", 75), cycle=(None, None, None, 75),
  eau_notes="Aime les sols frais ; arroser en été.",
  aime=[], evite=[],
  conseils=["Ne rien récolter la première année",
            "Tirer les pétioles, ne pas les couper ; les feuilles sont toxiques"])

C("cardon", "Cardon", "Cynara cardunculus", "Astéracées", "legume-feuille", "🌿",
  eau="eleve", freq=3, sol=SOL_RICHE, espacement=90, prof=2, diff=2, gel=True, tmin=-5,
  semis_dir=(30, 30), cycle=(None, 150, None, 60),
  eau_notes="Soutenu : c'est un gros buveur.",
  aime=["feve"], evite=[],
  conseils=["Lier et emballer les côtes un mois avant la récolte pour les blanchir"])

# =============================================================================
# Aromatiques
# =============================================================================

C("basilic", "Basilic", "Ocimum basilicum", "Lamiacées", "aromatique", "🌿",
  eau="eleve", freq=2, sol=SOL_RICHE, espacement=25, prof=0.5, diff=1, gel=False, tmin=12,
  semis_int=(-45, 30), plantation=(20, 40), cycle=(35, 70, 45, 120),
  eau_notes="Le matin, au pied ; jamais le soir, l'humidité nocturne le fait noircir.",
  aime=["tomate", "poivron", "courgette"], evite=["concombre"],
  conseils=["Pincer les fleurs dès qu'elles apparaissent : elles arrêtent la production de feuilles",
            "Craint le froid plus que tout : attendre la mi-mai dehors"])

C("persil", "Persil", "Petroselinum crispum", "Apiacées", "aromatique", "🌿",
  eau="moyen", freq=3, sol=SOL_RICHE, espacement=15, prof=1, diff=2, gel=True, tmin=-10,
  semis_dir=(-30, 120), cycle=(None, 80, None, 240),
  eau_notes="Régulier ; il jaunit s'il a soif.",
  aime=["tomate", "carotte", "radis"], evite=["laitue", "celeri-rave"],
  conseils=["Germination très lente (3 semaines) : tremper les graines une nuit",
            "Bisannuel : il monte en graines la deuxième année, mieux vaut le ressemer"])

C("coriandre", "Coriandre", "Coriandrum sativum", "Apiacées", "aromatique", "🌿",
  eau="moyen", freq=3, sol=SOL_ORDINAIRE, espacement=15, prof=1, diff=1, gel=True, tmin=-5,
  semis_dir=(-15, 120), cycle=(None, 50, None, 45),
  eau_notes="Régulier ; le sec la fait monter aussitôt.",
  aime=["tomate"], evite=["fenouil-bulbeux"],
  conseils=["Monte très vite en été : semer peu et souvent, ou à l'ombre légère"])

C("aneth", "Aneth", "Anethum graveolens", "Apiacées", "aromatique", "🌿",
  eau="moyen", freq=4, sol=SOL_ORDINAIRE, espacement=20, prof=1, diff=1, gel=True, tmin=-5,
  semis_dir=(-15, 120), cycle=(None, 60, None, 60),
  eau_notes="Modéré.",
  aime=["chou-cabus", "concombre", "cornichon", "laitue"], evite=["carotte", "fenouil-bulbeux"],
  conseils=["Se ressème seul année après année si on le laisse fleurir"])

C("cerfeuil", "Cerfeuil", "Anthriscus cerefolium", "Apiacées", "aromatique", "🌿",
  eau="moyen", freq=3, sol=SOL_RICHE, espacement=15, prof=0.5, diff=1, gel=True, tmin=-8,
  semis_dir=(-30, 120), cycle=(None, 50, None, 60),
  eau_notes="Garder frais ; il aime la mi-ombre.",
  aime=["radis", "laitue"], evite=[],
  conseils=["Préfère la mi-ombre : parfait au pied des plus grands"])

C("sarriette", "Sarriette", "Satureja hortensis", "Lamiacées", "aromatique", "🌿",
  eau="faible", freq=6, sol=SOL_LEGER, espacement=20, prof=0.5, diff=1, gel=False, tmin=5,
  semis_dir=(15, 45), cycle=(None, 60, None, 90),
  eau_notes="Sobre, comme toutes les méditerranéennes.",
  aime=["haricot-nain", "oignon-jaune", "pois-chiche"], evite=[],
  conseils=["Plantée près des haricots, elle éloigne les pucerons noirs"])

C("ciboulette", "Ciboulette", "Allium schoenoprasum", "Amaryllidacées", "aromatique", "🌿",
  eau="moyen", freq=4, sol=SOL_RICHE, espacement=20, prof=1, diff=1, gel=True, tmin=-20, perenne=True,
  semis_dir=(-30, 60), recolte=("04-01", 210), cycle=(None, None, None, 210),
  eau_notes="Régulier, elle aime la fraîcheur.",
  aime=["carotte", "tomate", "fraisier"], evite=["haricot-nain", "petit-pois"],
  conseils=["Couper à 3 cm du sol, elle repousse trois à quatre fois par saison",
            "Diviser la touffe tous les 3 ans"])

C("thym", "Thym", "Thymus vulgaris", "Lamiacées", "aromatique", "🌿",
  eau="faible", freq=10, sol="pauvre, caillouteux, très drainé", espacement=30,
  diff=1, gel=True, tmin=-15, perenne=True,
  plantation=(-15, 60), recolte=("03-01", 270), cycle=(None, None, None, 270),
  eau_notes="Ne jamais arroser en pleine terre : il meurt d'excès d'eau, pas de sécheresse.",
  aime=["chou-cabus", "aubergine", "fraisier"], evite=[],
  conseils=["Le pire ennemi du thym est l'arrosoir",
            "Tailler après la floraison pour éviter qu'il se dégarnisse"])

C("romarin", "Romarin", "Salvia rosmarinus", "Lamiacées", "aromatique", "🌿",
  eau="faible", freq=12, sol="pauvre, caillouteux, très drainé", espacement=80,
  diff=1, gel=True, tmin=-12, perenne=True,
  plantation=(-15, 60), recolte=("01-01", 364), cycle=(None, None, None, 364),
  eau_notes="Aucun arrosage une fois installé.",
  aime=["chou-cabus", "carotte"], evite=[],
  conseils=["Se récolte toute l'année, même sous la neige",
            "Bouture très facilement : une branche dans un verre d'eau"])

C("sauge", "Sauge officinale", "Salvia officinalis", "Lamiacées", "aromatique", "🌿",
  eau="faible", freq=8, sol=SOL_LEGER, espacement=50, diff=1, gel=True, tmin=-15, perenne=True,
  plantation=(-15, 60), recolte=("04-01", 210), cycle=(None, None, None, 210),
  eau_notes="Sobre ; craint l'humidité hivernale.",
  aime=["chou-cabus", "carotte", "fraisier"], evite=["concombre"],
  conseils=["Rabattre d'un tiers au printemps pour la garder compacte"])

C("menthe", "Menthe", "Mentha spicata", "Lamiacées", "aromatique", "🌿",
  eau="eleve", freq=2, sol=SOL_RICHE, espacement=40, diff=1, gel=True, tmin=-18, perenne=True,
  plantation=(-30, 60), recolte=("05-01", 150), cycle=(None, None, None, 150),
  eau_notes="Aime avoir les pieds au frais, presque humides.",
  aime=["chou-cabus", "tomate"], evite=["persil", "camomille"],
  conseils=["À cultiver en pot, sans exception : en pleine terre elle colonise tout",
            "Rabattre au sol en fin d'été pour une repousse tendre"])

C("origan", "Origan", "Origanum vulgare", "Lamiacées", "aromatique", "🌿",
  eau="faible", freq=8, sol=SOL_LEGER, espacement=35, diff=1, gel=True, tmin=-15, perenne=True,
  plantation=(-15, 60), recolte=("05-01", 150), cycle=(None, None, None, 150),
  eau_notes="Sobre.",
  aime=["tomate", "poivron", "courgette"], evite=[],
  conseils=["Le plus parfumé juste avant la floraison : c'est le moment de le sécher"])

C("estragon", "Estragon", "Artemisia dracunculus", "Astéracées", "aromatique", "🌿",
  eau="moyen", freq=5, sol=SOL_LEGER, espacement=50, diff=2, gel=True, tmin=-10, perenne=True,
  plantation=(-15, 45), recolte=("05-01", 150), cycle=(None, None, None, 150),
  eau_notes="Modéré ; redoute l'humidité stagnante l'hiver.",
  aime=["tomate", "aubergine"], evite=[],
  conseils=["Protéger le pied l'hiver par un paillage sec",
            "Diviser tous les 3 ans, il s'épuise"])

C("laurier-sauce", "Laurier-sauce", "Laurus nobilis", "Lauracées", "aromatique", "🌿",
  eau="faible", freq=10, sol=SOL_ORDINAIRE, espacement=150, diff=1, gel=True, tmin=-12, perenne=True,
  plantation=(-30, 90), anchor_pl="premiere", recolte=("01-01", 364), cycle=(None, None, None, 364),
  eau_notes="Aucun arrosage une fois établi.",
  aime=[], evite=[],
  conseils=["Devient un arbre : prévoir la place ou le tailler en boule",
            "Se cueille toute l'année"])

C("liveche", "Livèche (ache des montagnes)", "Levisticum officinale", "Apiacées", "aromatique", "🌿",
  eau="moyen", freq=4, sol=SOL_RICHE, espacement=80, diff=1, gel=True, tmin=-20, perenne=True,
  plantation=(-30, 60), recolte=("04-15", 180), cycle=(None, None, None, 180),
  eau_notes="Aime la fraîcheur.",
  aime=[], evite=[],
  conseils=["Goût de céleri en plus puissant : quelques feuilles suffisent",
            "Monte à 2 m : à placer au fond du jardin"])

# =============================================================================
# Petits fruits
# =============================================================================

C("fraisier", "Fraisier", "Fragaria x ananassa", "Rosacées", "petit-fruit", "🍓",
  eau="eleve", freq=2, sol=SOL_RICHE, espacement=35, diff=1, gel=True, tmin=-15, perenne=True,
  plantation=(-60, 60), anchor_pl="premiere", recolte=("05-15", 45), cycle=(None, None, None, 45),
  eau_notes="Régulier, au pied : l'eau sur les fruits les fait pourrir.",
  aime=["ail-blanc", "echalote", "oignon-jaune", "epinard", "ciboulette"], evite=["chou-cabus"],
  conseils=["Planter en septembre pour récolter dès le printemps suivant",
            "Pailler pour garder les fruits propres et hors du sol",
            "Remplacer les pieds tous les 3 ans, le rendement s'effondre après"])

C("fraisier-remontant", "Fraisier remontant", "Fragaria x ananassa", "Rosacées", "petit-fruit", "🍓",
  eau="eleve", freq=2, sol=SOL_RICHE, espacement=35, diff=1, gel=True, tmin=-15, perenne=True,
  plantation=(-60, 60), anchor_pl="premiere", recolte=("06-01", 135), cycle=(None, None, None, 135),
  eau_notes="Comme le fraisier classique, mais sur une période bien plus longue.",
  aime=["ail-blanc", "echalote", "ciboulette"], evite=["chou-cabus"],
  conseils=["Produit par vagues de juin aux gelées", "Supprimer les stolons pour favoriser les fruits"])

C("framboisier", "Framboisier", "Rubus idaeus", "Rosacées", "petit-fruit", "🫐",
  eau="moyen", freq=3, sol=SOL_RICHE, espacement=50, diff=1, gel=True, tmin=-20, perenne=True,
  plantation=(-15, 90), anchor_pl="premiere", recolte=("06-20", 45), cycle=(None, None, None, 45),
  eau_notes="Aime les sols frais ; pailler plutôt qu'arroser beaucoup.",
  aime=["ail-blanc", "oeillet-inde"], evite=["pomme-de-terre"],
  conseils=["Palisser sur deux fils : sans cela c'est un roncier",
            "Non remontant : couper au sol les cannes qui ont fructifié"])

C("framboisier-remontant", "Framboisier remontant", "Rubus idaeus", "Rosacées", "petit-fruit", "🫐",
  eau="moyen", freq=3, sol=SOL_RICHE, espacement=50, diff=1, gel=True, tmin=-20, perenne=True,
  plantation=(-15, 90), anchor_pl="premiere", recolte=("08-15", 60), cycle=(None, None, None, 60),
  eau_notes="Comme le non remontant.",
  aime=["ail-blanc"], evite=["pomme-de-terre"],
  conseils=["Taille simple : tout rabattre au sol en février"])

C("groseillier", "Groseillier", "Ribes rubrum", "Grossulariacées", "petit-fruit", "🫐",
  eau="moyen", freq=4, sol=SOL_RICHE, espacement=120, diff=1, gel=True, tmin=-20, perenne=True,
  plantation=(-15, 90), anchor_pl="premiere", recolte=("06-25", 30), cycle=(None, None, None, 30),
  eau_notes="Modéré ; supporte la mi-ombre.",
  aime=["ciboulette"], evite=[],
  conseils=["Tolère très bien la mi-ombre : utile pour les coins ingrats",
            "Supprimer le bois de plus de 4 ans en hiver"])

C("cassissier", "Cassissier", "Ribes nigrum", "Grossulariacées", "petit-fruit", "🫐",
  eau="moyen", freq=3, sol=SOL_RICHE, espacement=130, diff=1, gel=True, tmin=-20, perenne=True,
  plantation=(-15, 90), anchor_pl="premiere", recolte=("07-01", 25), cycle=(None, None, None, 25),
  eau_notes="Aime la fraîcheur, plus exigeant que le groseillier.",
  aime=["ciboulette"], evite=[],
  conseils=["Fructifie sur le bois de l'année : tailler sévèrement les vieilles branches"])

C("murier", "Mûrier (ronce)", "Rubus fruticosus", "Rosacées", "petit-fruit", "🫐",
  eau="faible", freq=6, sol=SOL_ORDINAIRE, espacement=200, diff=1, gel=True, tmin=-20, perenne=True,
  plantation=(-15, 90), anchor_pl="premiere", recolte=("08-01", 45), cycle=(None, None, None, 45),
  eau_notes="Très sobre une fois installé.",
  aime=[], evite=[],
  conseils=["Choisir une variété sans épines, la cueillette change de nature",
            "Palisser sur un grillage et rabattre chaque hiver"])

C("myrtillier", "Myrtillier", "Vaccinium corymbosum", "Éricacées", "petit-fruit", "🫐",
  eau="eleve", freq=2, sol="acide (pH 4-5), terre de bruyère", espacement=120,
  diff=2, gel=True, tmin=-20, perenne=True,
  plantation=(-15, 90), anchor_pl="premiere", recolte=("07-10", 40), cycle=(None, None, None, 40),
  eau_notes="Eau non calcaire impérative : eau de pluie si possible.",
  aime=[], evite=[],
  conseils=["Sol acide obligatoire : en pot avec de la terre de bruyère si le jardin est calcaire",
            "Planter deux variétés différentes pour une bonne pollinisation"])

C("vigne-table", "Vigne (raisin de table)", "Vitis vinifera", "Vitacées", "petit-fruit", "🍇",
  eau="faible", freq=10, sol="caillouteux, drainé, même pauvre", espacement=150,
  diff=2, gel=True, tmin=-15, perenne=True,
  plantation=(-15, 90), anchor_pl="premiere", recolte=("09-01", 40), cycle=(None, None, None, 40),
  eau_notes="Ne pas arroser : la vigne cherche l'eau en profondeur et gagne en sucre au sec.",
  aime=[], evite=["chou-cabus"],
  conseils=["Taille d'hiver indispensable : 2 yeux par coursonne",
            "Plein sud contre un mur : c'est la chaleur restituée qui fait le raisin"])

C("kiwi", "Kiwi (actinidia)", "Actinidia deliciosa", "Actinidiacées", "petit-fruit", "🥝",
  eau="eleve", freq=3, sol=SOL_RICHE, espacement=400, diff=2, gel=True, tmin=-12, perenne=True,
  plantation=(-15, 90), anchor_pl="premiere", recolte=("10-25", 30), cycle=(None, None, None, 30),
  eau_notes="Gros besoins en été ; le feuillage flétrit vite s'il manque d'eau.",
  aime=[], evite=[],
  conseils=["Un pied mâle pour cinq femelles, sauf variété autofertile",
            "Prévoir une pergola solide : il devient très lourd",
            "Récolter avant les gelées et laisser mûrir en cagette"])

# =============================================================================
# Arbres fruitiers
# =============================================================================

C("pommier", "Pommier", "Malus domestica", "Rosacées", "fruitier", "🍎",
  eau="faible", freq=10, sol=SOL_ORDINAIRE, espacement=400, diff=1, gel=True, tmin=-25, perenne=True,
  plantation=(15, 75), anchor_pl="premiere", recolte=("09-10", 40), cycle=(None, None, None, 40),
  eau_notes="Aucun arrosage une fois établi, sauf été de canicule les 3 premières années.",
  aime=["capucine", "ciboulette"], evite=[],
  conseils=["À la Sainte-Catherine (25 novembre), tout bois prend racine",
            "Deux variétés différentes pour la pollinisation",
            "Éclaircir les fruits en juin : moins de pommes, mais plus belles"])

C("poirier", "Poirier", "Pyrus communis", "Rosacées", "fruitier", "🍐",
  eau="faible", freq=10, sol=SOL_ORDINAIRE, espacement=400, diff=2, gel=True, tmin=-20, perenne=True,
  plantation=(15, 75), anchor_pl="premiere", recolte=("09-01", 35), cycle=(None, None, None, 35),
  eau_notes="Sobre une fois installé.",
  aime=["capucine"], evite=[],
  conseils=["Fleurit tôt : éviter les fonds de vallée gélifs",
            "Cueillir légèrement avant maturité et finir en fruitier"])

C("cerisier", "Cerisier", "Prunus avium", "Rosacées", "fruitier", "🍒",
  eau="faible", freq=12, sol=SOL_ORDINAIRE, espacement=500, diff=1, gel=True, tmin=-25, perenne=True,
  plantation=(15, 75), anchor_pl="premiere", recolte=("06-05", 25), cycle=(None, None, None, 25),
  eau_notes="Ne pas arroser en période de fruits : les cerises éclatent.",
  aime=["ciboulette"], evite=[],
  conseils=["Tailler le moins possible, et seulement après la récolte : il gomme",
            "Un filet est la seule défense réaliste contre les oiseaux"])

C("prunier", "Prunier", "Prunus domestica", "Rosacées", "fruitier", "🫐",
  eau="faible", freq=10, sol=SOL_ORDINAIRE, espacement=450, diff=1, gel=True, tmin=-25, perenne=True,
  plantation=(15, 75), anchor_pl="premiere", recolte=("08-05", 30), cycle=(None, None, None, 30),
  eau_notes="Sobre.",
  aime=[], evite=[],
  conseils=["Le plus facile des fruitiers à noyau sous climat océanique",
            "Étayer les branches chargées, elles cassent"])

C("pecher", "Pêcher", "Prunus persica", "Rosacées", "fruitier", "🍑",
  eau="moyen", freq=6, sol=SOL_LEGER, espacement=400, diff=3, gel=True, tmin=-18, perenne=True,
  plantation=(15, 75), anchor_pl="premiere", recolte=("07-20", 30), cycle=(None, None, None, 30),
  eau_notes="Arroser en été, mais jamais le feuillage.",
  aime=["ail-blanc", "capucine"], evite=[],
  conseils=["La cloque est la difficulté principale : décoction de prêle dès le débourrement",
            "Planter de l'ail au pied, vieux remède de jardinier contre la cloque"])

C("abricotier", "Abricotier", "Prunus armeniaca", "Rosacées", "fruitier", "🍑",
  eau="faible", freq=10, sol=SOL_LEGER, espacement=450, diff=3, gel=True, tmin=-20, perenne=True,
  plantation=(15, 75), anchor_pl="premiere", recolte=("07-05", 20), cycle=(None, None, None, 20),
  eau_notes="Sobre ; redoute l'humidité.",
  aime=[], evite=[],
  conseils=["Floraison très précoce : une gelée de mars supprime la récolte",
            "Lui donner l'emplacement le plus abrité et le plus tardif à se réchauffer"])

C("figuier", "Figuier", "Ficus carica", "Moracées", "fruitier", "🫒",
  eau="faible", freq=10, sol=SOL_ORDINAIRE, espacement=400, diff=1, gel=True, tmin=-15, perenne=True,
  plantation=(15, 75), anchor_pl="premiere", recolte=("08-15", 45), cycle=(None, None, None, 45),
  eau_notes="Très sobre ; trop d'eau dilue le goût des figues.",
  aime=[], evite=[],
  conseils=["Se plaît contre un mur au sud, racines contenues",
            "Parfaitement adapté au climat de la Loire-Atlantique"])

C("noisetier", "Noisetier", "Corylus avellana", "Bétulacées", "fruitier", "🌰",
  eau="faible", freq=10, sol=SOL_ORDINAIRE, espacement=400, diff=1, gel=True, tmin=-25, perenne=True,
  plantation=(15, 75), anchor_pl="premiere", recolte=("09-15", 30), cycle=(None, None, None, 30),
  eau_notes="Aucun arrosage une fois installé.",
  aime=[], evite=[],
  conseils=["Deux variétés différentes pour la pollinisation",
            "Le balanin perce les noisettes : ramasser et détruire les fruits tombés"])

C("noyer", "Noyer", "Juglans regia", "Juglandacées", "fruitier", "🌰",
  eau="faible", freq=12, sol=SOL_RICHE, espacement=1000, diff=1, gel=True, tmin=-25, perenne=True,
  plantation=(15, 75), anchor_pl="premiere", recolte=("09-25", 30), cycle=(None, None, None, 30),
  eau_notes="Aucun arrosage une fois établi.",
  aime=[], evite=["pomme-de-terre", "tomate"],
  conseils=["Rien ne pousse sous un noyer : la juglone inhibe les voisins",
            "Prévoir 10 m de dégagement, c'est un arbre de 20 m"])

# =============================================================================
# Fleurs compagnes — elles se sèment au potager et y jouent un rôle
# =============================================================================

C("oeillet-inde", "Œillet d'Inde", "Tagetes patula", "Astéracées", "fleur-compagne", "🌼",
  eau="moyen", freq=4, sol=SOL_ORDINAIRE, espacement=25, prof=0.5, diff=1, gel=False, tmin=5,
  semis_int=(-45, 30), semis_dir=(15, 60), cycle=(30, 70, 55, 150),
  eau_notes="Modéré ; très tolérant.",
  aime=["tomate", "aubergine", "framboisier", "pomme-de-terre"], evite=[],
  conseils=["Ses racines assainissent le sol des nématodes : le compagnon numéro un de la tomate",
            "Supprimer les fleurs fanées pour prolonger la floraison jusqu'aux gelées"])

C("capucine", "Capucine", "Tropaeolum majus", "Tropaeolacées", "fleur-compagne", "🌼",
  eau="faible", freq=5, sol="pauvre, sinon elle fait des feuilles et pas de fleurs",
  espacement=40, prof=2, diff=1, gel=False, tmin=5,
  semis_dir=(10, 60), cycle=(None, 55, None, 150),
  eau_notes="Sobre ; trop d'eau et d'engrais la font monter en feuilles.",
  aime=["courgette", "citrouille", "pommier", "poirier", "pecher", "haricot-a-rames"], evite=[],
  conseils=["Plante-piège à pucerons : ils s'y installent plutôt que sur vos légumes",
            "Fleurs et jeunes feuilles se mangent, goût poivré"])

C("bourrache", "Bourrache", "Borago officinalis", "Boraginacées", "fleur-compagne", "🌼",
  eau="faible", freq=6, sol=SOL_ORDINAIRE, espacement=40, prof=1, diff=1, gel=True, tmin=-8,
  semis_dir=(-15, 90), cycle=(None, 60, None, 120),
  eau_notes="Très sobre.",
  aime=["tomate", "courgette", "fraisier", "chou-cabus"], evite=[],
  conseils=["Aimant à bourdons : elle fait grimper la pollinisation des courgettes",
            "Se ressème seule indéfiniment"])

C("souci", "Souci (calendula)", "Calendula officinalis", "Astéracées", "fleur-compagne", "🌼",
  eau="faible", freq=5, sol=SOL_ORDINAIRE, espacement=30, prof=1, diff=1, gel=True, tmin=-8,
  semis_dir=(-30, 120), cycle=(None, 60, None, 180),
  eau_notes="Sobre.",
  aime=["tomate", "laitue", "chou-cabus", "pomme-de-terre"], evite=[],
  conseils=["Attire les syrphes, dont les larves dévorent les pucerons",
            "Fleurit du printemps aux gelées et se ressème seul"])

C("phacelie", "Phacélie", "Phacelia tanacetifolia", "Boraginacées", "fleur-compagne", "🌼",
  eau="faible", freq=7, sol=SOL_ORDINAIRE, espacement=15, prof=1, diff=1, gel=True, tmin=-8,
  semis_dir=(-30, 150), cycle=(None, 60, None, 60),
  eau_notes="Aucun arrosage.",
  aime=[], evite=[],
  conseils=["Engrais vert et pompe à pollinisateurs : à semer sur toute planche vide",
            "Faucher avant la montée en graines et laisser sur place"])

C("camomille", "Camomille romaine", "Chamaemelum nobile", "Astéracées", "aromatique", "🌼",
  eau="faible", freq=6, sol=SOL_LEGER, espacement=30, prof=0.5, diff=1, gel=True, tmin=-15,
  perenne=True, plantation=(-15, 60), recolte=("06-01", 90), cycle=(None, None, None, 90),
  eau_notes="Sobre une fois installée.",
  aime=["chou-cabus", "oignon-jaune"], evite=["menthe"],
  conseils=["Se récolte en fleurs, à sécher à l'ombre"])
