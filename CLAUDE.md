# Mon Potager — passation

Tu reprends une intégration Home Assistant personnalisée, `potager`, écrite de
zéro et déployée en production chez son unique utilisateur. Ce document te
donne ce qui ne se devine pas en lisant le code.

## Le produit

Un potager dans Home Assistant : un catalogue de 172 cultures, un jardin
virtuel, un panneau latéral, des rappels, et un suivi d'arrosage.

**L'idée centrale, qui gouverne tout le reste : le calendrier est piloté par ce
qui s'est vraiment passé, pas par une moyenne saisonnière.** Dès qu'une date
réelle entre au journal, les étapes suivantes s'enchaînent depuis elle. Semer
trois semaines en retard décale la récolte d'autant, et une plante déjà semée
ne réclame plus jamais de la semer. Toute évolution doit préserver ça.

## Où

- Source : `~/Documents/apps/ha-potager`
- Dépôt : `https://github.com/MaximeRiviere56/ha-potager` (public)
- Déploiement : HACS en dépôt personnalisé → `/config/custom_components/potager/`
  sur l'instance. **Modifier les sources ne change rien chez l'utilisateur**
  tant qu'une release n'est pas publiée et téléchargée par HACS.

## Architecture

### Modules purs — aucun import Home Assistant, donc testables hors instance

| Module | Rôle |
|---|---|
| `lifecycle.py` | journal d'une plante, machine à états, transitions |
| `phenology.py` | calcul des étapes culturales, théoriques et recalculées |
| `rotation.py` | avertissement de rotation des cultures |
| `watering.py` | arrosage : fréquence, échéance, exclusions |

**C'est la convention la plus importante du projet.** Toute logique métier non
triviale va dans un module pur et arrive avec ses tests. Home Assistant ne peut
pas être exécuté sur le poste de développement : ces modules sont le seul filet.

### Couche Home Assistant

`__init__.py` (setup, panneau, services) · `config_flow.py` · `coordinator.py`
(`DataUpdateCoordinator`, vue calculée partagée) · `store.py` (persistance) ·
`catalog.py` (catalogue livré + fiches personnelles fusionnées) ·
`websocket.py` (API du panneau) · `notifier.py` · `sensor.py` `switch.py`
`calendar.py` `todo.py` · `frontend/potager-panel.js` et `potager-card.js`.

### Frontend

Web components natifs, **zéro étape de build**, zéro dépendance. Le fichier
servi est celui qu'on lit. Ne pas introduire de bundler.

## Invariants à ne pas casser

1. **Un fait du journal gagne toujours sur une fenêtre saisonnière.**
2. **Le décalage de zone ne s'applique jamais à une date réelle.** Une prévision
   se décale, un fait non.
3. **Aucune date en dur dans le catalogue.** Chaque fenêtre est un décalage en
   jours par rapport aux gelées locales de l'utilisateur. Seules les pérennes
   déclarent une récolte à date fixe.
4. **La phase se déduit toujours du journal par repli**, jamais stockée comme
   fait indépendant. C'est ce qui rend l'annulation fiable.
5. **Toute mutation passe par `coordinator.async_appliquer`**, qui écrit sur
   disque *et attend* avant de rendre la main. Une sauvegarde différée a déjà
   coûté un jardin entier au redémarrage.
6. **L'arrosage n'est pas un événement du journal.** Il ne fait pas avancer le
   cycle et se répète trop souvent : liste séparée `arrosages`.
7. **Un rappel qu'on ignore discrédite tous les autres.** Chaque garde-fou
   existant (plante pas en terre, hiver en pleine terre, pérenne installée)
   est là pour ça.

## Outillage — lis ceci avant de proposer quoi que ce soit

Le Mac de développement a **Python 3.9.6 système uniquement**. Pas de pytest,
pas de Node, pas de pip utilisable.

- Tests : `python3 -m unittest discover -s tests -p 'test_*.py'` avec
  `PYTHONPATH=tests`. **94 tests, zéro dépendance.**
- **Éviter la syntaxe Python 3.12+** (`type X = ...` notamment) bien que HA
  tourne en 3.14 : cela garde un contrôle statique local possible sur tous les
  fichiers avant déploiement.
- Le JavaScript se vérifie dans un navigateur, pas par un linter.
- Git passe par HTTPS avec le jeton `gh` (aucune clé SSH sur ce poste).

## Vérification

```bash
PYTHONPATH=tests python3 -m unittest discover -s tests -p 'test_*.py'
python3 tools/auditer_catalogue.py      # 172 fiches, 0 impossible, 0 douteuse
python3 tools/build_catalog.py          # régénère data/catalog.json
python3 tools/banc_fixture.py && python3 -m http.server 8777
#   http://localhost:8777/tools/banc.html        — le panneau, six vues
#   http://localhost:8777/tools/banc-carte.html  — la carte Lovelace
```

Le **banc d'essai** monte le frontend hors de Home Assistant, avec un `hass`
factice alimenté par le vrai moteur et le vrai catalogue. Il a attrapé la
plupart des défauts réels du projet : libellés sans accents, récolte annoncée
en janvier pour une courgette, calendrier vide, « depuis 692 jours » sur un
pommier, lecture d'`entity_id` sur un objet qui ne le porte pas. **Utilise-le
systématiquement avant de publier.**

Le catalogue se modifie dans `tools/catalogue_source.py` (table compacte), pas
dans le JSON généré.

## Honnêteté sur les données

**Les 172 fiches n'ont été confrontées à aucune base de référence.** Les API du
domaine ne fournissent pas de calendriers de semis — OpenFarm est mort,
Growstuff n'a pas d'API officielle, Permapeople ne couvre pas les semis. Le
catalogue a été écrit de mémoire horticole.

Trois atténuations : le réel prime dès le premier semis noté ; l'utilisateur
peut corriger n'importe quelle fiche, y compris livrée ; et
`tools/auditer_catalogue.py` prouve qu'aucune fiche n'est *impossible* (huit
règles de cohérence interne). Les durées de cycle restent hors de portée de
toute vérification automatique. **Ne présente jamais ces données comme
sourcées.**

## Conventions

- Tout en français : code, commentaires, commits, interface, documentation.
- Les commentaires disent **pourquoi**, pas quoi. Ceux qui expliquent un choix
  contre-intuitif ont de la valeur ; les autres non.
- Messages de commit : ce qui change, et le raisonnement derrière. Les défauts
  trouvés y sont consignés avec leur cause.
- Versionner à chaque livraison : bump `manifest.json`, tag, release GitHub avec
  des notes rédigées, puis `ha_manage_hacs` (update_information + download).

## État au 23 octobre 2026

v0.6.0 publiée. L'utilisateur a **plusieurs versions téléchargées mais pas
activées** : il lui reste un redémarrage de Home Assistant pour que v0.3.0 à
v0.6.0 prennent effet. Vérifie l'état réel avant de conclure quoi que ce soit —
une commande WebSocket inconnue de l'instance signifie que le code tourne en
version antérieure.

Son instance : HA 2026.10.2, Bouguenais (44), zone 9a, gelées 15/04 et 15/11,
notifications vers `notify.mobile_app_fairphone_6`.

Pistes restantes, par ordre de valeur : alerte gel via l'entité météo
(`weather.bouguenais` existe, `rusticite.gel` est dans chaque fiche), arrosage
réellement journalisé par zone, export du journal.
