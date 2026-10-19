# Mon Potager

Une intégration Home Assistant pour gérer un potager : choisir ses légumes dans
un catalogue de 108 cultures, les suivre dans un jardin virtuel, et recevoir au
bon moment un rappel pour semer, repiquer ou récolter.

> **L'idée centrale.** Le calendrier n'est pas une fiche théorique figée : il
> est piloté par ce qui s'est vraiment passé. Vous semez vos tomates trois
> semaines en retard ? La date de récolte se décale de trois semaines. Et la
> plante déjà semée ne vous réclamera plus jamais de la semer.

## Ce que ça donne

**Un panneau « Mon Potager » dans la barre latérale**, avec cinq vues :
Aujourd'hui, Mon potager, Catalogue, Calendrier, Journal.

**Des entités** pour vos tableaux de bord et vos automatisations :

| Entité | Rôle |
|---|---|
| `sensor.mon_potager_actions_a_mener` | Nombre d'actions du jour, détail en attributs |
| `sensor.mon_potager_recolte_de_la_saison` | Total récolté en kg (`state_class: total`, exploitable dans les statistiques) |
| `sensor.<plante>` | Phase de la plante, et toute sa fiche en attributs |
| `switch.rappels_<plante>` | Rappels de cette plante — automatisable (« coupe tout pendant les vacances ») |
| `calendar.mon_potager` | Étapes prévues **et** journal passé |
| `todo.mon_potager` | Tâches en cours — **cocher enregistre l'événement** |

**Une carte Lovelace** `custom:potager-card` pour votre tableau de bord principal.

## Le suivi réel, sans formulaire

Un journal qu'on doit tenir à la main ne se tient pas. Il y a donc trois chemins
pour enregistrer un geste, et aucun ne demande de saisir une date :

1. le bouton **« C'est fait »** sur la notification ;
2. la **case à cocher** de `todo.mon_potager` ;
3. le bouton **« Fait »** sur la carte Lovelace ou dans le panneau.

Chacun inscrit l'événement au journal à la date du jour, ce qui recalcule
immédiatement la suite du cycle.

```
prévu ──semé le──▶ semé ──repiqué le──▶ planté ──1ʳᵉ récolte──▶ en récolte ──▶ terminé
                     │                     │
                     └─ repiquage prévu    └─ récolte prévue
                        = cette date + jours_semis_a_repiquage
```

Les récoltes se cumulent : un plant de tomates se récolte vingt fois, et vous
obtenez un total par culture et par saison. `potager.annuler_dernier_evenement`
défait la dernière entrée — on se trompe toujours une fois.

## Installation

### Par HACS (recommandé)

1. HACS → menu ⋮ → **Dépôts personnalisés**
2. URL `https://github.com/MaximeRiviere56/ha-potager`, catégorie **Integration**
3. Installer **Mon Potager**, puis redémarrer Home Assistant
4. **Paramètres → Appareils et services → Ajouter une intégration → Mon Potager**

### À la main

Copier `custom_components/potager/` dans le dossier `config/` de Home
Assistant, redémarrer, puis ajouter l'intégration.

### La carte Lovelace

Le fichier est servi par l'intégration. L'ajouter dans **Paramètres →
Tableaux de bord → Ressources** :

- URL : `/potager-frontend/potager-card.js`
- Type : **Module JavaScript**

```yaml
type: custom:potager-card
titre: Au potager
max: 5
```

## Configuration

Deux réglages comptent vraiment.

**Vos dates de gelées.** Elles calent tout le calendrier. Le formulaire propose
des préselections climatiques (Ouest océanique, Nord et Est, Midi, Montagne) ;
vous pouvez aussi saisir vos dates au format `MM-JJ`. Aucune date n'est écrite
en dur dans le catalogue : tout est un décalage en jours par rapport à la
dernière gelée de printemps ou à la première gelée d'automne. C'est ce qui rend
le calendrier juste chez vous, et pas seulement en moyenne nationale.

**Les destinataires des rappels.** Choisissez vos applications mobiles : seuls
les services `notify.mobile_app_*` transportent des boutons d'action, et c'est
le bouton « C'est fait » qui remplit votre journal sans effort.

### Les zones

Pleine terre, serre, châssis, balcon — chacune porte un décalage en jours
(la serre prend trois semaines d'avance par défaut) qui avance ou retarde tout
le calendrier des plantes qui s'y trouvent.

Le décalage ne s'applique **jamais** à une date du journal : une date réelle est
un fait, pas une prévision.

## Le catalogue

108 cultures : légumes-fruits, racines, gousses, bulbes, feuilles, aromatiques,
petits fruits, arbres fruitiers et fleurs compagnes. Chaque fiche porte
l'exposition, les besoins en eau, le sol, l'espacement, la rusticité, les bons
et mauvais voisins, des conseils, et ses fenêtres culturales.

Le catalogue est **embarqué** : aucune API, aucun compte, aucun service externe
susceptible de disparaître. Les API publiques du domaine ont d'ailleurs mal
vieilli — OpenFarm est mort, Growstuff n'a jamais eu d'API officielle, et
Permapeople ne fournit pas de calendrier de semis.

Une culture gélive voit sa fenêtre de récolte plafonnée à la première gelée :
une courgette ne se récolte pas en janvier.

### Ajouter une culture

Les fiches vivent dans une table compacte, une ligne par culture :

```bash
$EDITOR tools/catalogue_source.py
python3 tools/build_catalog.py     # valide puis régénère data/catalog.json
```

La validation refuse une fiche dont la récolte ne serait pas calculable, dont un
compagnon n'existe pas, ou à qui il manque `rusticite.gel`.

## Services

| Service | Effet |
|---|---|
| `potager.ajouter_plante` | Ajoute une culture au jardin |
| `potager.retirer_plante` | La retire, avec son journal |
| `potager.marquer_seme` | Semis à sa date réelle (`mode` : `direct` ou `interieur`) |
| `potager.marquer_repique` | Mise en place |
| `potager.marquer_recolte` | Récolte, avec `quantite_g` facultatif |
| `potager.marquer_perdu` | Perte, avec sa `cause` |
| `potager.marquer_termine` | Clôt la culture |
| `potager.annuler_dernier_evenement` | Défait la dernière entrée du journal |
| `potager.rafraichir` | Recalcule tout de suite |

## Développement

```bash
python3 -m unittest discover -s tests -p 'test_*.py'   # 52 tests, sans dépendance
```

`lifecycle.py` (le journal) et `phenology.py` (le calcul des étapes) n'importent
rien de Home Assistant : ils sont testables hors instance, et c'est là que vit
toute la logique qui coûterait cher si elle était fausse — un calendrier faux ne
se voit qu'une saison plus tard.

Le panneau et la carte se vérifient sans instance :

```bash
python3 tools/banc_fixture.py && python3 -m http.server 8777
# http://localhost:8777/tools/banc.html        — le panneau, cinq vues
# http://localhost:8777/tools/banc-carte.html  — la carte Lovelace
```

Les données du banc sortent du vrai catalogue et du vrai moteur : il montre donc
le panneau face à ce qu'il recevra réellement.

## Licence

MIT.
