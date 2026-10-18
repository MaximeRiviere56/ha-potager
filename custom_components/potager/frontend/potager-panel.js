/**
 * Panneau « Mon Potager ».
 *
 * Ecrit en web components natifs, sans bundler ni dependance : le fichier que
 * Home Assistant sert est celui qu'on lit ici. C'est ce qui garde l'install
 * HACS sans etape de build et le projet modifiable dans un an.
 *
 * Toutes les couleurs viennent des variables CSS de Home Assistant : le
 * panneau suit le theme de l'utilisateur, mode sombre compris, sans code.
 */

const VUES = [
  { id: "aujourdhui", nom: "Aujourd'hui", icone: "mdi:white-balance-sunny" },
  { id: "potager", nom: "Mon potager", icone: "mdi:sprout" },
  { id: "catalogue", nom: "Catalogue", icone: "mdi:book-open-variant" },
  { id: "calendrier", nom: "Calendrier", icone: "mdi:calendar-month" },
  { id: "journal", nom: "Journal", icone: "mdi:notebook-outline" },
];

const CATEGORIES = {
  "legume-fruit": "Légumes-fruits",
  "legume-racine": "Racines",
  "legume-gousse": "Gousses",
  "legume-bulbe": "Bulbes",
  "legume-feuille": "Feuilles",
  aromatique: "Aromatiques",
  "petit-fruit": "Petits fruits",
  fruitier: "Fruitiers",
  "fleur-compagne": "Fleurs compagnes",
};

const EXPOSITIONS = {
  "plein-soleil": { label: "Plein soleil", icone: "mdi:weather-sunny" },
  "mi-ombre": { label: "Mi-ombre", icone: "mdi:weather-partly-cloudy" },
  ombre: { label: "Ombre", icone: "mdi:weather-cloudy" },
};

const EAU = { faible: "Peu d'eau", moyen: "Arrosage modéré", eleve: "Beaucoup d'eau" };

const COULEURS_ETAPE = {
  semis_interieur: "var(--potager-semis)",
  semis_direct: "var(--potager-semis)",
  repiquage: "var(--potager-plantation)",
  plantation: "var(--potager-plantation)",
  recolte: "var(--potager-recolte)",
};

/** Miroir cote client de JOURNAL_POUR_ETAPE (notifier.py) : ce qu'un
 *  « C'est fait » inscrit au journal selon l'etape concernee. */
const EVT_POUR_ETAPE = {
  semis_interieur: { evenement: "seme", mode: "interieur" },
  semis_direct: { evenement: "seme", mode: "direct" },
  repiquage: { evenement: "repique" },
  plantation: { evenement: "plante" },
  recolte: { evenement: "recolte" },
};

const LIBELLES_EVT = {
  seme: "Semé",
  repique: "Repiqué",
  plante: "Planté",
  recolte: "Récolté",
  termine: "Terminé",
  perdu: "Perdu",
};

const MOIS = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"];
const MOIS_LONGS = [
  "janvier", "février", "mars", "avril", "mai", "juin",
  "juillet", "août", "septembre", "octobre", "novembre", "décembre",
];

const jour = (iso) => new Date(`${iso}T12:00:00`);
const fmtCourt = (iso) =>
  jour(iso).toLocaleDateString("fr-FR", { day: "numeric", month: "short" });
const fmtLong = (iso) =>
  jour(iso).toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" });
const kg = (grammes) =>
  grammes >= 1000 ? `${(grammes / 1000).toFixed(grammes % 1000 ? 2 : 0)} kg` : `${grammes} g`;

function echappe(texte) {
  const div = document.createElement("div");
  div.textContent = texte == null ? "" : String(texte);
  return div.innerHTML;
}

/** Jours entre aujourd'hui et une date ISO. Negatif si elle est passee. */
function joursJusqu(iso) {
  const aujourdhui = new Date();
  aujourdhui.setHours(12, 0, 0, 0);
  return Math.round((jour(iso) - aujourdhui) / 86400000);
}

const estDansFenetre = (etape) =>
  joursJusqu(etape.debut) <= 0 && joursJusqu(etape.fin) >= 0;

/** « C'est le moment », « Demain », « Dans 5 jours », « Il y a 3 jours ». */
function quand(joursRestants, enCours) {
  if (enCours) return "C'est le moment";
  if (joursRestants === 0) return "Aujourd'hui";
  if (joursRestants === 1) return "Demain";
  if (joursRestants > 1) return `Dans ${joursRestants} jours`;
  if (joursRestants === -1) return "Depuis hier";
  return `Depuis ${Math.abs(joursRestants)} jours`;
}

const STYLES = `
  :host {
    --potager-semis: #7cb342;
    --potager-plantation: #00897b;
    --potager-recolte: #ef6c00;
    --potager-rayon: var(--ha-card-border-radius, 12px);
    display: block;
    height: 100%;
    overflow: hidden;
    background: var(--primary-background-color);
    color: var(--primary-text-color);
    font-family: var(--paper-font-body1_-_font-family, Roboto, system-ui, sans-serif);
  }
  * { box-sizing: border-box; }

  .enveloppe { display: flex; flex-direction: column; height: 100%; }

  header {
    background: var(--app-header-background-color, var(--primary-color));
    color: var(--app-header-text-color, #fff);
    flex: 0 0 auto;
  }
  .barre-titre {
    display: flex; align-items: center; gap: 12px;
    padding: 0 16px; height: var(--header-height, 56px);
  }
  .barre-titre h1 { font-size: 20px; font-weight: 400; margin: 0; flex: 1; }
  .compteur-entete {
    background: rgba(255,255,255,.2); border-radius: 999px;
    padding: 3px 10px; font-size: 13px; font-weight: 500;
  }
  nav { display: flex; overflow-x: auto; scrollbar-width: none; }
  nav::-webkit-scrollbar { display: none; }
  nav button {
    flex: 1 0 auto; display: flex; align-items: center; justify-content: center; gap: 6px;
    min-width: 64px; padding: 10px 14px; border: 0; cursor: pointer;
    background: none; color: inherit; opacity: .7;
    border-bottom: 3px solid transparent; font-size: 13px; font-weight: 500;
    font-family: inherit; white-space: nowrap;
  }
  nav button[aria-selected="true"] { opacity: 1; border-bottom-color: currentColor; }
  nav button:hover { opacity: 1; background: rgba(255,255,255,.08); }

  main { flex: 1 1 auto; overflow-y: auto; padding: 16px; }
  .contenu { max-width: 1100px; margin: 0 auto; }

  h2 { font-size: 15px; font-weight: 500; margin: 24px 0 10px;
       color: var(--secondary-text-color); text-transform: uppercase; letter-spacing: .5px; }
  h2:first-child { margin-top: 0; }

  .carte {
    background: var(--card-background-color, #fff);
    border-radius: var(--potager-rayon);
    box-shadow: var(--ha-card-box-shadow, 0 1px 3px rgba(0,0,0,.12));
    border: var(--ha-card-border-width, 1px) solid var(--ha-card-border-color, transparent);
  }

  .grille { display: grid; gap: 12px; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); }
  .grille-large { grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); }

  /* --- Cartes d'action --------------------------------------------------- */
  .action { display: flex; align-items: center; gap: 14px; padding: 14px; }
  .action .emoji { font-size: 32px; line-height: 1; flex: 0 0 auto; }
  .action .corps { flex: 1 1 auto; min-width: 0; }
  .action .titre { font-size: 16px; font-weight: 500; }
  .action .detail { font-size: 13px; color: var(--secondary-text-color); margin-top: 2px; }
  .action .verbe { font-weight: 500; }
  .urgent .verbe { color: var(--potager-recolte); }

  /* --- Cartes de plante ------------------------------------------------- */
  .plante { padding: 14px; cursor: pointer; transition: box-shadow .15s, transform .15s; }
  .plante:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,.16); }
  .plante-tete { display: flex; align-items: flex-start; gap: 12px; }
  .plante-tete .emoji { font-size: 30px; line-height: 1; }
  .plante-nom { font-size: 16px; font-weight: 500; }
  .plante-zone { font-size: 12px; color: var(--secondary-text-color); }
  .progression { height: 5px; border-radius: 3px; background: var(--divider-color); margin-top: 12px; overflow: hidden; }
  .progression > div { height: 100%; border-radius: 3px; }

  .badge {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 11px; font-weight: 600; padding: 3px 9px; border-radius: 999px;
    background: var(--divider-color); color: var(--primary-text-color); white-space: nowrap;
  }
  .badge.prevu { background: color-mix(in srgb, var(--secondary-text-color) 18%, transparent); }
  .badge.seme { background: color-mix(in srgb, var(--potager-semis) 25%, transparent); }
  .badge.plante { background: color-mix(in srgb, var(--potager-plantation) 25%, transparent); }
  .badge.en_recolte { background: color-mix(in srgb, var(--potager-recolte) 28%, transparent); }
  .badge.termine, .badge.perdu { background: color-mix(in srgb, var(--error-color) 20%, transparent); }

  /* --- Boutons ----------------------------------------------------------- */
  button.bouton {
    display: inline-flex; align-items: center; justify-content: center; gap: 6px;
    border: 0; border-radius: 999px; padding: 9px 16px; cursor: pointer;
    font-size: 14px; font-weight: 500; font-family: inherit;
    background: var(--primary-color); color: var(--text-primary-color, #fff);
  }
  button.bouton:hover { filter: brightness(1.08); }
  button.bouton.discret { background: var(--divider-color); color: var(--primary-text-color); }
  button.bouton.danger { background: var(--error-color); color: #fff; }
  button.bouton:disabled { opacity: .5; cursor: default; }
  button.icone {
    border: 0; background: none; cursor: pointer; color: var(--secondary-text-color);
    padding: 8px; border-radius: 50%; display: inline-flex;
  }
  button.icone:hover { background: var(--divider-color); color: var(--primary-text-color); }

  /* --- Recherche et filtres --------------------------------------------- */
  .recherche { display: flex; align-items: center; gap: 10px; padding: 10px 14px; margin-bottom: 12px; }
  .recherche input {
    flex: 1; border: 0; background: none; outline: none; font-size: 16px;
    color: var(--primary-text-color); font-family: inherit; min-width: 0;
  }
  .puces { display: flex; gap: 8px; overflow-x: auto; padding-bottom: 10px; scrollbar-width: none; }
  .puces::-webkit-scrollbar { display: none; }
  .puce {
    flex: 0 0 auto; border: 1px solid var(--divider-color); background: var(--card-background-color);
    color: var(--primary-text-color); border-radius: 999px; padding: 7px 14px;
    font-size: 13px; cursor: pointer; font-family: inherit; white-space: nowrap;
  }
  .puce[aria-pressed="true"] { background: var(--primary-color); color: var(--text-primary-color, #fff); border-color: transparent; }

  /* --- Etat vide --------------------------------------------------------- */
  .vide { text-align: center; padding: 48px 20px; color: var(--secondary-text-color); }
  .vide .gros { font-size: 52px; margin-bottom: 12px; }
  .vide p { margin: 0 0 18px; line-height: 1.5; }

  /* --- Calendrier ------------------------------------------------------- */
  .cal-defilement { overflow-x: auto; padding: 4px; }
  .cal { min-width: 680px; }
  .cal-ligne { display: grid; grid-template-columns: 150px 1fr; align-items: center; gap: 10px; padding: 5px 0; }
  .cal-nom { font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .cal-piste { position: relative; height: 24px; background: var(--divider-color); border-radius: 4px; }
  .cal-bande { position: absolute; top: 3px; height: 18px; border-radius: 4px; min-width: 3px; }
  .cal-bande.prevue { opacity: .4; background-image: repeating-linear-gradient(45deg, rgba(255,255,255,.5) 0 3px, transparent 3px 6px); }
  .cal-entete { display: grid; grid-template-columns: 150px 1fr; gap: 10px; padding-bottom: 6px; }
  .cal-mois { display: grid; grid-template-columns: repeat(12, 1fr); font-size: 11px; color: var(--secondary-text-color); text-align: center; }
  .cal-aujourdhui { position: absolute; top: -3px; bottom: -3px; width: 2px; background: var(--error-color); z-index: 2; }
  .legende { display: flex; flex-wrap: wrap; gap: 16px; margin-top: 16px; font-size: 12px; color: var(--secondary-text-color); }
  .legende span { display: inline-flex; align-items: center; gap: 6px; }
  .pastille { width: 12px; height: 12px; border-radius: 3px; display: inline-block; }

  /* --- Journal ---------------------------------------------------------- */
  .journal-ligne { display: flex; gap: 14px; padding: 12px 14px; align-items: flex-start; }
  .journal-date { flex: 0 0 72px; font-size: 12px; color: var(--secondary-text-color); padding-top: 2px; }
  .journal-corps { flex: 1; min-width: 0; }
  .journal-note { font-size: 13px; color: var(--secondary-text-color); margin-top: 2px; font-style: italic; }
  .bilan { display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); margin-bottom: 20px; }
  .bilan .tuile { padding: 16px; text-align: center; }
  .bilan .chiffre { font-size: 26px; font-weight: 500; }
  .bilan .etiquette { font-size: 12px; color: var(--secondary-text-color); margin-top: 2px; }

  /* --- Fiche (panneau lateral) ------------------------------------------ */
  .voile {
    position: fixed; inset: 0; background: rgba(0,0,0,.45);
    display: flex; justify-content: flex-end; z-index: 10;
  }
  .fiche {
    width: min(560px, 100%); height: 100%; overflow-y: auto;
    background: var(--primary-background-color);
    box-shadow: -4px 0 24px rgba(0,0,0,.25);
    animation: glisse .18s ease-out;
  }
  @keyframes glisse { from { transform: translateX(24px); opacity: .6; } }
  .fiche-tete {
    position: sticky; top: 0; z-index: 1; display: flex; align-items: center; gap: 12px;
    padding: 14px 16px; background: var(--card-background-color);
    border-bottom: 1px solid var(--divider-color);
  }
  .fiche-tete .emoji { font-size: 30px; }
  .fiche-tete h3 { margin: 0; font-size: 18px; font-weight: 500; flex: 1; }
  .fiche-corps { padding: 16px; display: flex; flex-direction: column; gap: 16px; }
  .bloc { padding: 14px; }
  .bloc h4 { margin: 0 0 10px; font-size: 13px; text-transform: uppercase;
             letter-spacing: .5px; color: var(--secondary-text-color); font-weight: 500; }
  .faits { display: grid; gap: 10px; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); }
  .fait { font-size: 13px; }
  .fait .cle { color: var(--secondary-text-color); font-size: 11px; text-transform: uppercase; }
  .fait .valeur { margin-top: 2px; }
  ul.conseils { margin: 0; padding-left: 20px; font-size: 14px; line-height: 1.6; }
  .compagnes { display: flex; flex-wrap: wrap; gap: 6px; }
  .compagne { font-size: 12px; padding: 4px 10px; border-radius: 999px; background: var(--divider-color); }
  .frise { display: flex; flex-direction: column; gap: 0; }
  .frise-etape { display: flex; gap: 12px; }
  .frise-trait { flex: 0 0 12px; display: flex; flex-direction: column; align-items: center; }
  .frise-point { width: 10px; height: 10px; border-radius: 50%; background: var(--primary-color); margin-top: 5px; }
  .frise-barre { flex: 1; width: 2px; background: var(--divider-color); min-height: 14px; }
  .frise-texte { flex: 1; padding-bottom: 14px; font-size: 14px; }
  .frise-texte .date { font-size: 12px; color: var(--secondary-text-color); }
  .reglage { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 9px 0; }
  .reglage label { font-size: 14px; }
  .reglage select, .reglage input {
    border: 1px solid var(--divider-color); border-radius: 8px; padding: 7px 10px;
    background: var(--card-background-color); color: var(--primary-text-color);
    font-family: inherit; font-size: 14px; max-width: 58%;
  }
  .actions-fiche { display: flex; flex-wrap: wrap; gap: 8px; }

  .erreur {
    background: color-mix(in srgb, var(--error-color) 15%, transparent);
    color: var(--error-color); padding: 12px 14px; border-radius: var(--potager-rayon);
    margin-bottom: 14px; font-size: 14px;
  }
  .chargement { text-align: center; padding: 48px; color: var(--secondary-text-color); }

  @media (max-width: 600px) {
    main { padding: 12px; }
    nav button span.etiquette { display: none; }
    nav button { min-width: 0; }
    .fiche { width: 100%; }
  }
`;

class PotagerPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._vue = "aujourdhui";
    this._jardin = null;
    this._catalogue = null;
    this._fiche = null;
    this._erreur = null;
    this._chargement = true;
    this._recherche = "";
    this._filtreCategorie = null;
    this._filtreDifficulte = null;
    this._filtreJournal = null;
    this._anneeCal = new Date().getFullYear();
    this._signature = null;
    this._rendu = false;
  }

  /** Home Assistant pousse un nouvel objet `hass` a chaque changement d'etat.
   *  On s'en sert comme signal de rafraichissement : si le capteur d'actions a
   *  bouge, le jardin a change, y compris depuis un autre appareil. */
  set hass(hass) {
    const premier = !this._hass;
    this._hass = hass;
    if (premier) {
      this._rendreCoquille();
      this._charger();
      return;
    }
    const signature = this._signatureEtat();
    if (signature !== this._signature) {
      this._signature = signature;
      this._charger({ discret: true });
    }
  }

  _signatureEtat() {
    const etats = this._hass?.states || {};
    return Object.keys(etats)
      .filter((id) => id.startsWith("sensor.potager") || id.startsWith("switch.potager"))
      .map((id) => `${id}:${etats[id].state}:${etats[id].last_updated}`)
      .join(",");
  }

  connectedCallback() {
    if (this._hass && !this._rendu) {
      this._rendreCoquille();
      this._charger();
    }
  }

  // --- Donnees -------------------------------------------------------------

  async _charger({ discret = false } = {}) {
    if (!discret) this._chargement = true;
    try {
      const [jardin, catalogue] = await Promise.all([
        this._hass.callWS({ type: "potager/jardin" }),
        this._hass.callWS({ type: "potager/catalogue" }),
      ]);
      this._jardin = jardin;
      this._catalogue = catalogue;
      this._erreur = null;
      this._signature = this._signatureEtat();
    } catch (err) {
      this._erreur = err?.message || "Impossible de joindre Mon Potager.";
    } finally {
      this._chargement = false;
      this._rendreVue();
    }
  }

  async _appeler(message) {
    try {
      const reponse = await this._hass.callWS(message);
      await this._charger({ discret: true });
      return reponse;
    } catch (err) {
      this._erreur = err?.message || "Action refusée.";
      this._rendreVue();
      return null;
    }
  }

  _noter(uid, evenement, extra = {}) {
    return this._appeler({ type: "potager/noter", uid, evenement, ...extra });
  }

  // --- Coquille ------------------------------------------------------------

  _rendreCoquille() {
    this._rendu = true;
    this.shadowRoot.innerHTML = `
      <style>${STYLES}</style>
      <div class="enveloppe">
        <header>
          <div class="barre-titre">
            <ha-icon icon="mdi:sprout"></ha-icon>
            <h1>Mon Potager</h1>
            <span class="compteur-entete" id="compteur" hidden></span>
          </div>
          <nav id="nav"></nav>
        </header>
        <main><div class="contenu" id="vue"></div></main>
      </div>
      <div id="fiche"></div>
    `;

    const nav = this.shadowRoot.getElementById("nav");
    nav.innerHTML = VUES.map(
      (v) => `<button data-vue="${v.id}" aria-selected="${v.id === this._vue}">
          <ha-icon icon="${v.icone}"></ha-icon><span class="etiquette">${v.nom}</span>
        </button>`
    ).join("");
    nav.addEventListener("click", (ev) => {
      const bouton = ev.target.closest("button[data-vue]");
      if (!bouton) return;
      this._vue = bouton.dataset.vue;
      nav.querySelectorAll("button").forEach((b) =>
        b.setAttribute("aria-selected", String(b.dataset.vue === this._vue))
      );
      this._rendreVue();
      this.shadowRoot.querySelector("main").scrollTop = 0;
    });
  }

  _rendreVue() {
    const hote = this.shadowRoot?.getElementById("vue");
    if (!hote) return;

    const compteur = this.shadowRoot.getElementById("compteur");
    const nbActions = this._jardin?.actions?.length || 0;
    if (nbActions > 0) {
      compteur.textContent = `${nbActions} à faire`;
      compteur.hidden = false;
    } else {
      compteur.hidden = true;
    }

    if (this._chargement && !this._jardin) {
      hote.innerHTML = `<div class="chargement">Chargement du potager…</div>`;
      return;
    }

    const banniere = this._erreur
      ? `<div class="erreur">${echappe(this._erreur)}</div>`
      : "";

    const vues = {
      aujourdhui: () => this._vueAujourdhui(),
      potager: () => this._vuePotager(),
      catalogue: () => this._vueCatalogue(),
      calendrier: () => this._vueCalendrier(),
      journal: () => this._vueJournal(),
    };
    hote.innerHTML = banniere + (vues[this._vue] || vues.aujourdhui)();
    this._brancherVue(hote);
    this._rendreFiche();
  }

  // --- Vue : Aujourd'hui ---------------------------------------------------

  _vueAujourdhui() {
    const actions = this._jardin?.actions || [];
    const plantes = this._jardin?.plantes || [];

    if (!plantes.length) {
      return `<div class="vide">
          <div class="gros">🌱</div>
          <p>Votre potager est vide.<br>
             Choisissez vos premiers légumes dans le catalogue&nbsp;:
             ${this._catalogue?.total || 108} cultures vous attendent.</p>
          <button class="bouton" data-aller="catalogue">
            <ha-icon icon="mdi:book-open-variant"></ha-icon> Ouvrir le catalogue
          </button>
        </div>`;
    }

    if (!actions.length) {
      return `<div class="vide">
          <div class="gros">☕</div>
          <p>Rien à faire au potager aujourd'hui.<br>
             ${plantes.length} plante${plantes.length > 1 ? "s" : ""} suivie${
        plantes.length > 1 ? "s" : ""
      }, prochaine échéance plus tard.</p>
          <button class="bouton discret" data-aller="potager">
            <ha-icon icon="mdi:sprout"></ha-icon> Voir mon potager
          </button>
        </div>`;
    }

    const maintenant = actions.filter((a) => a.en_cours);
    const bientot = actions.filter((a) => !a.en_cours);
    const arrosage = this._pensebeteArrosage();

    return `
      ${
        maintenant.length
          ? `<h2>C'est le moment</h2>
             <div class="grille grille-large">${maintenant
               .map((a) => this._carteAction(a, true))
               .join("")}</div>`
          : ""
      }
      ${
        bientot.length
          ? `<h2>À préparer</h2>
             <div class="grille grille-large">${bientot
               .map((a) => this._carteAction(a, false))
               .join("")}</div>`
          : ""
      }
      ${arrosage}`;
  }

  /** Pense-bete, et non planning : l'integration ne sait pas quand vous avez
   *  arrose pour la derniere fois, et pretendre le contraire serait mentir. */
  _pensebeteArrosage() {
    const assoiffees = (this._jardin?.plantes || [])
      .filter(
        (p) =>
          ["seme", "plante", "en_recolte"].includes(p.phase) &&
          p.arrosage.besoin === "eleve"
      )
      .sort((a, b) => a.arrosage.frequence_jours - b.arrosage.frequence_jours);

    if (!assoiffees.length) return "";
    return `<h2>Pense-bête arrosage</h2>
      <div class="carte" style="padding:4px 0">
        ${assoiffees
          .map(
            (p) => `<div class="journal-ligne">
              <div style="font-size:22px">${p.emoji}</div>
              <div class="journal-corps">
                <div>${echappe(p.nom)} <span class="badge">${echappe(
              p.zone.nom
            )}</span></div>
                <div class="journal-note">Tous les ${
                  p.arrosage.frequence_jours
                } jours — ${echappe(p.arrosage.notes)}</div>
              </div>
            </div>`
          )
          .join("")}
      </div>`;
  }

  _carteAction(action, urgent) {
    const etape = action.etape;
    const correspondance = EVT_POUR_ETAPE[etape.type];
    const largeur = action.en_cours ? this._avancementFenetre(etape) : 0;
    return `
      <div class="carte action ${urgent ? "urgent" : ""}">
        <div class="emoji">${action.emoji}</div>
        <div class="corps">
          <div class="titre">${echappe(action.nom)}</div>
          <div class="detail">
            <span class="verbe">${echappe(etape.libelle)}</span> ·
            ${quand(action.jours_restants, action.en_cours)} ·
            ${echappe(action.zone)}
          </div>
          <div class="detail">Fenêtre jusqu'au ${fmtCourt(etape.fin)}${
      etape.reelle ? " · d'après votre journal" : ""
    }</div>
          ${
            largeur
              ? `<div class="progression"><div style="width:${largeur}%;background:${
                  COULEURS_ETAPE[etape.type]
                }"></div></div>`
              : ""
          }
        </div>
        ${
          correspondance
            ? `<button class="bouton" data-fait="${action.uid}"
                 data-etape="${etape.type}" title="Enregistrer au journal">
                 <ha-icon icon="mdi:check"></ha-icon> Fait
               </button>`
            : ""
        }
      </div>`;
  }

  _avancementFenetre(etape) {
    const debut = jour(etape.debut).getTime();
    const fin = jour(etape.fin).getTime();
    if (fin <= debut) return 100;
    const part = ((Date.now() - debut) / (fin - debut)) * 100;
    return Math.min(100, Math.max(4, Math.round(part)));
  }

  // --- Vue : Mon potager ---------------------------------------------------

  _vuePotager() {
    const plantes = this._jardin?.plantes || [];
    if (!plantes.length) {
      return `<div class="vide">
          <div class="gros">🪴</div>
          <p>Aucune plante pour l'instant.</p>
          <button class="bouton" data-aller="catalogue">
            <ha-icon icon="mdi:plus"></ha-icon> Ajouter des légumes
          </button>
        </div>`;
    }

    const parZone = new Map();
    for (const plante of plantes) {
      const cle = plante.zone.nom;
      if (!parZone.has(cle)) parZone.set(cle, []);
      parZone.get(cle).push(plante);
    }

    return [...parZone.entries()]
      .map(
        ([zone, liste]) => `
          <h2>${echappe(zone)} · ${liste.length}</h2>
          <div class="grille">${liste.map((p) => this._cartePlante(p)).join("")}</div>`
      )
      .join("");
  }

  _cartePlante(plante) {
    const prochaine = plante.prochaine;
    const largeur = prochaine ? this._avancementFenetre(prochaine) : 0;
    return `
      <div class="carte plante" data-fiche="${plante.uid}">
        <div class="plante-tete">
          <div class="emoji">${plante.emoji}</div>
          <div style="flex:1;min-width:0">
            <div class="plante-nom">${echappe(plante.nom)}</div>
            <div class="plante-zone">${echappe(plante.zone.nom)}${
      plante.total_recolte_g ? ` · ${kg(plante.total_recolte_g)} récoltés` : ""
    }</div>
          </div>
          <span class="badge ${plante.phase}">${echappe(plante.phase_libelle)}</span>
        </div>
        <div class="detail" style="margin-top:10px;font-size:13px;color:var(--secondary-text-color)">
          ${
            prochaine
              ? `${echappe(prochaine.libelle)} · ${quand(
                  joursJusqu(prochaine.debut),
                  estDansFenetre(prochaine)
                )}`
              : "Rien de prévu"
          }
        </div>
        ${
          prochaine
            ? `<div class="progression"><div style="width:${largeur || 3}%;background:${
                COULEURS_ETAPE[prochaine.type]
              }"></div></div>`
            : ""
        }
      </div>`;
  }

  // --- Vue : Catalogue -----------------------------------------------------

  _vueCatalogue() {
    const cultures = this._cataloguFiltre();
    const categories = this._catalogue?.categories || [];

    return `
      <div class="carte recherche">
        <ha-icon icon="mdi:magnify"></ha-icon>
        <input id="champ-recherche" type="search" placeholder="Chercher un légume, un fruit, une famille…"
               value="${echappe(this._recherche)}" autocomplete="off">
        ${
          this._recherche
            ? `<button class="icone" data-vider="1"><ha-icon icon="mdi:close"></ha-icon></button>`
            : ""
        }
      </div>

      <div class="puces">
        <button class="puce" data-filtre-semable="1"
                aria-pressed="${this._filtreDifficulte === "semable"}">
          🌱 Semable maintenant
        </button>
        <button class="puce" data-filtre-facile="1"
                aria-pressed="${this._filtreDifficulte === "facile"}">
          ★ Facile
        </button>
        ${categories
          .map(
            (c) => `<button class="puce" data-filtre-cat="${c}"
                 aria-pressed="${this._filtreCategorie === c}">${
              CATEGORIES[c] || c
            }</button>`
          )
          .join("")}
      </div>

      <div class="detail" style="margin:4px 0 12px;font-size:13px;color:var(--secondary-text-color)">
        ${cultures.length} culture${cultures.length > 1 ? "s" : ""} sur ${
      this._catalogue?.total || 0
    }
      </div>

      ${
        cultures.length
          ? `<div class="grille">${cultures.map((c) => this._carteCulture(c)).join("")}</div>`
          : `<div class="vide"><div class="gros">🔍</div><p>Aucune culture ne correspond.</p></div>`
      }`;
  }

  _cataloguFiltre() {
    let cultures = this._catalogue?.cultures || [];
    if (this._filtreCategorie) {
      cultures = cultures.filter((c) => c.categorie === this._filtreCategorie);
    }
    if (this._filtreDifficulte === "facile") {
      cultures = cultures.filter((c) => c.difficulte === 1);
    }
    if (this._filtreDifficulte === "semable") {
      cultures = cultures.filter((c) => c.semable_maintenant);
    }
    if (this._recherche) {
      const terme = this._recherche
        .toLowerCase()
        .normalize("NFD")
        .replace(/[̀-ͯ]/g, "");
      cultures = cultures.filter((c) =>
        `${c.nom} ${c.famille}`
          .toLowerCase()
          .normalize("NFD")
          .replace(/[̀-ͯ]/g, "")
          .includes(terme)
      );
    }
    return cultures;
  }

  _carteCulture(culture) {
    const expo = EXPOSITIONS[culture.exposition] || {};
    const dejaAu = (this._jardin?.plantes || []).filter(
      (p) => p.culture_id === culture.id
    ).length;

    return `
      <div class="carte plante" data-culture="${culture.id}">
        <div class="plante-tete">
          <div class="emoji">${culture.emoji}</div>
          <div style="flex:1;min-width:0">
            <div class="plante-nom">${echappe(culture.nom)}</div>
            <div class="plante-zone">${CATEGORIES[culture.categorie] || ""} · ${
      "★".repeat(culture.difficulte)
    }</div>
          </div>
          ${
            dejaAu
              ? `<span class="badge plante">${dejaAu} au potager</span>`
              : culture.semable_maintenant
              ? `<span class="badge seme">🌱 maintenant</span>`
              : ""
          }
        </div>
        <div class="detail" style="margin-top:10px;font-size:13px;color:var(--secondary-text-color)">
          <ha-icon icon="${expo.icone || "mdi:weather-sunny"}" style="--mdc-icon-size:16px"></ha-icon>
          ${expo.label || ""} · ${EAU[culture.arrosage.besoin] || ""}
        </div>
        <div class="detail" style="margin-top:4px;font-size:13px;color:var(--secondary-text-color)">
          ${
            culture.prochain_depart
              ? `${echappe(culture.prochain_depart.libelle)} : ${fmtCourt(
                  culture.prochain_depart.debut
                )} → ${fmtCourt(culture.prochain_depart.fin)}`
              : culture.perenne
              ? "Plantation pérenne"
              : ""
          }
        </div>
      </div>`;
  }

  // --- Vue : Calendrier ----------------------------------------------------

  _vueCalendrier() {
    const plantes = this._jardin?.plantes || [];
    if (!plantes.length) {
      return `<div class="vide"><div class="gros">📅</div>
        <p>Le calendrier se remplira dès que vous aurez ajouté des cultures.</p></div>`;
    }

    const annee = this._anneeCal;
    const debutAnnee = new Date(annee, 0, 1).getTime();
    const finAnnee = new Date(annee + 1, 0, 1).getTime();
    const duree = finAnnee - debutAnnee;
    const position = (iso) =>
      Math.max(0, Math.min(100, ((jour(iso).getTime() - debutAnnee) / duree) * 100));

    const maintenant = Date.now();
    const repere =
      maintenant >= debutAnnee && maintenant < finAnnee
        ? `<div class="cal-aujourdhui" style="left:${
            ((maintenant - debutAnnee) / duree) * 100
          }%"></div>`
        : "";

    const lignes = plantes
      .map((plante) => {
        const bandes = (plante.etapes || [])
          .filter((e) => jour(e.fin).getTime() >= debutAnnee && jour(e.debut).getTime() < finAnnee)
          .map((e) => {
            const gauche = position(e.debut);
            const largeur = Math.max(1.2, position(e.fin) - gauche);
            return `<div class="cal-bande ${e.reelle ? "" : "prevue"}"
              style="left:${gauche}%;width:${largeur}%;background:${
              COULEURS_ETAPE[e.type] || "var(--primary-color)"
            }"
              title="${echappe(e.libelle)} : ${fmtCourt(e.debut)} → ${fmtCourt(e.fin)}"></div>`;
          })
          .join("");

        const faits = (plante.evenements || [])
          .filter((evt) => evt.date.startsWith(String(annee)))
          .map(
            (evt) => `<div class="cal-bande"
              style="left:${position(evt.date)}%;width:1.2%;background:var(--primary-text-color)"
              title="${echappe(evt.libelle)} le ${fmtCourt(evt.date)}"></div>`
          )
          .join("");

        return `<div class="cal-ligne">
            <div class="cal-nom" title="${echappe(plante.nom)}">${plante.emoji} ${echappe(
          plante.nom
        )}</div>
            <div class="cal-piste">${bandes}${faits}${repere}</div>
          </div>`;
      })
      .join("");

    return `
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">
        <button class="icone" data-annee="${annee - 1}"><ha-icon icon="mdi:chevron-left"></ha-icon></button>
        <strong style="font-size:17px">${annee}</strong>
        <button class="icone" data-annee="${annee + 1}"><ha-icon icon="mdi:chevron-right"></ha-icon></button>
      </div>

      <div class="carte cal-defilement">
        <div class="cal">
          <div class="cal-entete">
            <div></div>
            <div class="cal-mois">${MOIS.map((m) => `<span>${m}</span>`).join("")}</div>
          </div>
          ${lignes}
        </div>
      </div>

      <div class="legende">
        <span><i class="pastille" style="background:var(--potager-semis)"></i> Semis</span>
        <span><i class="pastille" style="background:var(--potager-plantation)"></i> Plantation, repiquage</span>
        <span><i class="pastille" style="background:var(--potager-recolte)"></i> Récolte</span>
        <span><i class="pastille" style="background:var(--primary-text-color)"></i> Noté au journal</span>
        <span>Trame claire&nbsp;: prévu · Plein&nbsp;: calculé d'après votre journal</span>
      </div>`;
  }

  // --- Vue : Journal -------------------------------------------------------

  _vueJournal() {
    const plantes = this._jardin?.plantes || [];
    const entrees = [];
    for (const plante of plantes) {
      for (const evt of plante.evenements || []) {
        entrees.push({ ...evt, plante });
      }
    }
    entrees.sort((a, b) => (a.date < b.date ? 1 : -1));

    if (!entrees.length) {
      return `<div class="vide"><div class="gros">📖</div>
        <p>Votre journal est vide.<br>
           Dès que vous noterez un semis — depuis « Aujourd'hui », une notification
           ou la liste de tâches — il s'écrira ici tout seul.</p></div>`;
    }

    const total = this._jardin.total_recolte_g || 0;
    const pertes = entrees.filter((e) => e.type === "perdu");
    const recoltes = entrees.filter((e) => e.type === "recolte");
    const filtrees = this._filtreJournal
      ? entrees.filter((e) => e.type === this._filtreJournal)
      : entrees;

    const typesPresents = [...new Set(entrees.map((e) => e.type))];

    return `
      <div class="bilan">
        <div class="carte tuile">
          <div class="chiffre">${kg(total)}</div>
          <div class="etiquette">récoltés cette saison</div>
        </div>
        <div class="carte tuile">
          <div class="chiffre">${recoltes.length}</div>
          <div class="etiquette">récolte${recoltes.length > 1 ? "s" : ""} notée${
      recoltes.length > 1 ? "s" : ""
    }</div>
        </div>
        <div class="carte tuile">
          <div class="chiffre">${plantes.length}</div>
          <div class="etiquette">plantes suivies</div>
        </div>
        ${
          pertes.length
            ? `<div class="carte tuile">
                 <div class="chiffre">${pertes.length}</div>
                 <div class="etiquette">perte${pertes.length > 1 ? "s" : ""}</div>
               </div>`
            : ""
        }
      </div>

      <div class="puces">
        <button class="puce" data-filtre-journal="" aria-pressed="${!this._filtreJournal}">Tout</button>
        ${typesPresents
          .map(
            (t) => `<button class="puce" data-filtre-journal="${t}"
              aria-pressed="${this._filtreJournal === t}">${LIBELLES_EVT[t] || t}</button>`
          )
          .join("")}
      </div>

      <div class="carte" style="padding:4px 0">
        ${filtrees
          .map(
            (e) => `<div class="journal-ligne">
              <div class="journal-date">${fmtCourt(e.date)}</div>
              <div style="font-size:20px">${e.plante.emoji}</div>
              <div class="journal-corps">
                <div><strong>${echappe(e.libelle)}</strong> · ${echappe(
              e.plante.nom
            )} <span class="badge">${echappe(e.plante.zone.nom)}</span></div>
                ${
                  e.quantite_g
                    ? `<div class="journal-note">${kg(e.quantite_g)}</div>`
                    : ""
                }
                ${e.cause ? `<div class="journal-note">Cause : ${echappe(e.cause)}</div>` : ""}
                ${e.note ? `<div class="journal-note">${echappe(e.note)}</div>` : ""}
              </div>
            </div>`
          )
          .join("")}
      </div>`;
  }

  // --- Branchement des interactions ---------------------------------------

  _brancherVue(hote) {
    hote.querySelectorAll("[data-aller]").forEach((el) =>
      el.addEventListener("click", () => {
        this._vue = el.dataset.aller;
        this.shadowRoot
          .getElementById("nav")
          .querySelectorAll("button")
          .forEach((b) => b.setAttribute("aria-selected", String(b.dataset.vue === this._vue)));
        this._rendreVue();
      })
    );

    hote.querySelectorAll("[data-fait]").forEach((el) =>
      el.addEventListener("click", async (ev) => {
        ev.stopPropagation();
        el.disabled = true;
        const corr = EVT_POUR_ETAPE[el.dataset.etape];
        if (corr) {
          if (corr.evenement === "recolte") {
            this._demanderRecolte(el.dataset.fait);
            el.disabled = false;
            return;
          }
          await this._noter(el.dataset.fait, corr.evenement,
            corr.mode ? { mode: corr.mode } : {});
        }
      })
    );

    hote.querySelectorAll("[data-fiche]").forEach((el) =>
      el.addEventListener("click", () => {
        this._ouvrirFichePlante(el.dataset.fiche);
      })
    );

    hote.querySelectorAll("[data-culture]").forEach((el) =>
      el.addEventListener("click", () => {
        this._fiche = { type: "culture", id: el.dataset.culture };
        this._ouvrirFicheCulture(el.dataset.culture);
      })
    );

    const champ = hote.querySelector("#champ-recherche");
    if (champ) {
      champ.addEventListener("input", () => {
        this._recherche = champ.value;
        clearTimeout(this._tempo);
        this._tempo = setTimeout(() => {
          const position = champ.selectionStart;
          this._rendreVue();
          const nouveau = this.shadowRoot.querySelector("#champ-recherche");
          if (nouveau) {
            nouveau.focus();
            nouveau.setSelectionRange(position, position);
          }
        }, 180);
      });
    }

    const vider = hote.querySelector("[data-vider]");
    if (vider) {
      vider.addEventListener("click", () => {
        this._recherche = "";
        this._rendreVue();
      });
    }

    hote.querySelectorAll("[data-filtre-cat]").forEach((el) =>
      el.addEventListener("click", () => {
        this._filtreCategorie =
          this._filtreCategorie === el.dataset.filtreCat ? null : el.dataset.filtreCat;
        this._rendreVue();
      })
    );
    hote.querySelectorAll("[data-filtre-facile]").forEach((el) =>
      el.addEventListener("click", () => {
        this._filtreDifficulte = this._filtreDifficulte === "facile" ? null : "facile";
        this._rendreVue();
      })
    );
    hote.querySelectorAll("[data-filtre-semable]").forEach((el) =>
      el.addEventListener("click", () => {
        this._filtreDifficulte = this._filtreDifficulte === "semable" ? null : "semable";
        this._rendreVue();
      })
    );
    hote.querySelectorAll("[data-filtre-journal]").forEach((el) =>
      el.addEventListener("click", () => {
        this._filtreJournal = el.dataset.filtreJournal || null;
        this._rendreVue();
      })
    );
    hote.querySelectorAll("[data-annee]").forEach((el) =>
      el.addEventListener("click", () => {
        this._anneeCal = Number(el.dataset.annee);
        this._rendreVue();
      })
    );
  }

  // --- Fiche detaillee -----------------------------------------------------

  async _ouvrirFicheCulture(cultureId) {
    this._ficheDetail = null;
    this._rendreFiche();
    try {
      this._ficheDetail = await this._hass.callWS({
        type: "potager/culture",
        culture_id: cultureId,
      });
    } catch (err) {
      this._erreur = err?.message || "Fiche indisponible.";
    }
    this._rendreFiche();
  }

  async _ouvrirFichePlante(uid) {
    const plante = (this._jardin?.plantes || []).find((p) => p.uid === uid);
    this._fiche = { type: "plante", uid };
    this._ficheDetail = null;
    this._rendreFiche();
    if (plante) {
      try {
        this._ficheDetail = await this._hass.callWS({
          type: "potager/culture",
          culture_id: plante.culture_id,
        });
      } catch (err) {
        /* la fiche reste utilisable sans ses compagnes */
      }
      this._rendreFiche();
    }
  }

  _fermerFiche() {
    this._fiche = null;
    this._ficheDetail = null;
    this._rendreFiche();
  }

  _rendreFiche() {
    const hote = this.shadowRoot?.getElementById("fiche");
    if (!hote) return;

    if (!this._fiche) {
      hote.innerHTML = "";
      return;
    }

    const contenu =
      this._fiche.type === "plante" ? this._fichePlante() : this._ficheCulture();
    if (contenu === null) {
      hote.innerHTML = "";
      this._fiche = null;
      return;
    }

    hote.innerHTML = `<div class="voile" id="voile"><div class="fiche">${contenu}</div></div>`;
    this._brancherFiche(hote);
  }

  _fichePlante() {
    const plante = (this._jardin?.plantes || []).find(
      (p) => p.uid === this._fiche.uid
    );
    if (!plante) return null;

    const culture = this._ficheDetail?.culture;
    const prochaine = plante.prochaine;
    const corr = prochaine ? EVT_POUR_ETAPE[prochaine.type] : null;
    const zones = this._jardin?.zones || [];

    return `
      <div class="fiche-tete">
        <div class="emoji">${plante.emoji}</div>
        <h3>${echappe(plante.nom)}</h3>
        <span class="badge ${plante.phase}">${echappe(plante.phase_libelle)}</span>
        <button class="icone" data-fermer="1"><ha-icon icon="mdi:close"></ha-icon></button>
      </div>

      <div class="fiche-corps">
        ${
          prochaine
            ? `<div class="carte bloc">
                 <h4>Prochaine étape</h4>
                 <div style="font-size:17px;font-weight:500">${echappe(
                   prochaine.libelle
                 )}</div>
                 <div style="font-size:13px;color:var(--secondary-text-color);margin:4px 0 12px">
                   Du ${fmtLong(prochaine.debut)} au ${fmtLong(prochaine.fin)}
                   ${
                     prochaine.reelle
                       ? "<br>Calculée depuis votre journal, et non depuis une moyenne saisonnière."
                       : ""
                   }
                 </div>
                 ${
                   corr
                     ? `<button class="bouton" data-fait-fiche="${plante.uid}"
                          data-etape="${prochaine.type}">
                          <ha-icon icon="mdi:check"></ha-icon>
                          ${
                            corr.evenement === "recolte"
                              ? "Noter une récolte"
                              : `C'est fait : ${prochaine.libelle.toLowerCase()}`
                          }
                        </button>`
                     : ""
                 }
               </div>`
            : `<div class="carte bloc"><h4>Prochaine étape</h4>
                 <div style="color:var(--secondary-text-color)">Plus rien de prévu
                 pour cette plante.</div></div>`
        }

        ${
          ["seme", "plante", "en_recolte"].includes(plante.phase)
            ? `<div class="carte bloc">
                 <h4>Noter une récolte</h4>
                 <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
                   <input id="qte-recolte" type="number" min="0" step="10" placeholder="grammes"
                          style="border:1px solid var(--divider-color);border-radius:8px;padding:8px 10px;
                                 background:var(--card-background-color);color:var(--primary-text-color);
                                 font-family:inherit;width:120px">
                   <button class="bouton" data-recolter="${plante.uid}">
                     <ha-icon icon="mdi:basket"></ha-icon> Enregistrer
                   </button>
                 </div>
                 <div style="font-size:12px;color:var(--secondary-text-color);margin-top:8px">
                   La quantité est facultative. ${
                     plante.nb_recoltes
                       ? `${plante.nb_recoltes} récolte${
                           plante.nb_recoltes > 1 ? "s" : ""
                         } déjà notée${plante.nb_recoltes > 1 ? "s" : ""}, ${kg(
                           plante.total_recolte_g
                         )} au total.`
                       : ""
                   }
                 </div>
               </div>`
            : ""
        }

        ${this._blocFrise(plante)}

        <div class="carte bloc">
          <h4>Réglages</h4>
          <div class="reglage">
            <label for="sel-zone">Zone</label>
            <select id="sel-zone" data-uid="${plante.uid}">
              ${zones
                .map(
                  (z) => `<option value="${z.id}" ${
                    z.id === plante.zone.id ? "selected" : ""
                  }>${echappe(z.nom)}${
                    z.decalage_jours
                      ? ` (${z.decalage_jours > 0 ? "+" : ""}${z.decalage_jours} j)`
                      : ""
                  }</option>`
                )
                .join("")}
            </select>
          </div>
          <div class="reglage">
            <label for="champ-surnom">Surnom</label>
            <input id="champ-surnom" type="text" data-uid="${plante.uid}"
                   value="${echappe(plante.surnom || "")}" placeholder="variété, emplacement…">
          </div>
          <div class="reglage">
            <label for="bascule-notifs">Rappels pour cette plante</label>
            <input id="bascule-notifs" type="checkbox" data-uid="${plante.uid}"
                   ${plante.notifs ? "checked" : ""} style="width:20px;height:20px">
          </div>
          <div class="reglage">
            <label for="champ-rappel">Prévenir à l'avance</label>
            <input id="champ-rappel" type="number" min="0" max="30" data-uid="${plante.uid}"
                   value="${
                     plante.rappel_jours ?? this._jardin?.rappel_jours ?? 3
                   }" style="width:90px">
          </div>
        </div>

        ${culture ? this._blocCulture(culture) : ""}
        ${this._ficheDetail ? this._blocCompagnes(this._ficheDetail.compagnes) : ""}

        <div class="carte bloc">
          <h4>Corriger</h4>
          <div class="actions-fiche">
            ${
              plante.evenements.length
                ? `<button class="bouton discret" data-annuler="${plante.uid}">
                     <ha-icon icon="mdi:undo"></ha-icon>
                     Annuler « ${echappe(
                       plante.evenements[plante.evenements.length - 1].libelle
                     )} »
                   </button>`
                : ""
            }
            <button class="bouton danger" data-retirer="${plante.uid}">
              <ha-icon icon="mdi:delete-outline"></ha-icon> Retirer du potager
            </button>
          </div>
        </div>
      </div>`;
  }

  _blocFrise(plante) {
    if (!plante.evenements.length) {
      return `<div class="carte bloc"><h4>Journal</h4>
        <div style="color:var(--secondary-text-color);font-size:14px">
          Rien de noté pour l'instant. Le premier « C'est fait » démarrera la frise,
          et les dates suivantes se calculeront depuis lui.
        </div></div>`;
    }

    const etapes = plante.evenements
      .map(
        (evt, index) => `
          <div class="frise-etape">
            <div class="frise-trait">
              <div class="frise-point"></div>
              ${
                index < plante.evenements.length - 1
                  ? `<div class="frise-barre"></div>`
                  : ""
              }
            </div>
            <div class="frise-texte">
              <strong>${echappe(evt.libelle)}</strong>
              ${evt.quantite_g ? ` · ${kg(evt.quantite_g)}` : ""}
              <div class="date">${fmtLong(evt.date)}${
          evt.cause ? ` · ${echappe(evt.cause)}` : ""
        }</div>
              ${evt.note ? `<div class="journal-note">${echappe(evt.note)}</div>` : ""}
            </div>
          </div>`
      )
      .join("");

    return `<div class="carte bloc"><h4>Journal</h4><div class="frise">${etapes}</div></div>`;
  }

  _ficheCulture() {
    const detail = this._ficheDetail;
    if (!detail) {
      return `<div class="fiche-tete">
          <h3>Chargement…</h3>
          <button class="icone" data-fermer="1"><ha-icon icon="mdi:close"></ha-icon></button>
        </div>`;
    }

    const culture = detail.culture;
    const zones = this._jardin?.zones || [];
    const dejaAu = (this._jardin?.plantes || []).filter(
      (p) => p.culture_id === culture.id
    );

    return `
      <div class="fiche-tete">
        <div class="emoji">${culture.emoji}</div>
        <h3>${echappe(culture.nom)}</h3>
        <button class="icone" data-fermer="1"><ha-icon icon="mdi:close"></ha-icon></button>
      </div>

      <div class="fiche-corps">
        <div class="carte bloc">
          <h4>Ajouter à mon potager</h4>
          ${
            dejaAu.length
              ? `<div style="font-size:13px;color:var(--secondary-text-color);margin-bottom:10px">
                   Déjà ${dejaAu.length} au potager (${dejaAu
                  .map((p) => echappe(p.zone.nom))
                  .join(", ")}). En ajouter un autre permet d'échelonner les semis.
                 </div>`
              : ""
          }
          <div class="reglage">
            <label for="sel-zone-ajout">Zone</label>
            <select id="sel-zone-ajout">
              ${zones
                .map(
                  (z) => `<option value="${z.id}">${echappe(z.nom)}${
                    z.decalage_jours
                      ? ` (${z.decalage_jours > 0 ? "+" : ""}${z.decalage_jours} j)`
                      : ""
                  }</option>`
                )
                .join("")}
            </select>
          </div>
          <div class="reglage">
            <label for="champ-surnom-ajout">Surnom</label>
            <input id="champ-surnom-ajout" type="text" placeholder="variété, emplacement…">
          </div>
          <button class="bouton" data-ajouter="${culture.id}" style="margin-top:8px">
            <ha-icon icon="mdi:plus"></ha-icon> Ajouter
          </button>
        </div>

        ${this._blocFenetres(detail.fenetres)}
        ${this._blocCulture(culture)}
        ${this._blocCompagnes(detail.compagnes)}
      </div>`;
  }

  _blocFenetres(fenetres) {
    if (!fenetres?.length) return "";
    return `<div class="carte bloc">
        <h4>Calendrier type, chez vous</h4>
        ${fenetres
          .map(
            (f) => `<div style="display:flex;justify-content:space-between;gap:12px;
                        padding:7px 0;border-bottom:1px solid var(--divider-color)">
              <span style="display:inline-flex;align-items:center;gap:8px">
                <i class="pastille" style="background:${
                  COULEURS_ETAPE[f.type] || "var(--primary-color)"
                }"></i>
                ${echappe(f.libelle)}
              </span>
              <span style="color:var(--secondary-text-color);font-size:13px;text-align:right">
                ${fmtCourt(f.debut)} → ${fmtCourt(f.fin)}
              </span>
            </div>`
          )
          .join("")}
        <div style="font-size:12px;color:var(--secondary-text-color);margin-top:10px">
          Calculé depuis vos dates de gelées (${
            this._jardin?.gelees?.derniere || "?"
          } et ${this._jardin?.gelees?.premiere || "?"}), pas depuis une moyenne nationale.
        </div>
      </div>`;
  }

  _blocCulture(culture) {
    const expo = EXPOSITIONS[culture.exposition] || {};
    return `
      <div class="carte bloc">
        <h4>La culture</h4>
        <div class="faits">
          <div class="fait"><div class="cle">Exposition</div>
            <div class="valeur">${expo.label || culture.exposition}</div></div>
          <div class="fait"><div class="cle">Arrosage</div>
            <div class="valeur">${EAU[culture.arrosage.besoin] || ""}, tous les ${
      culture.arrosage.frequence_jours
    } j</div></div>
          <div class="fait"><div class="cle">Espacement</div>
            <div class="valeur">${culture.espacement_cm} cm</div></div>
          <div class="fait"><div class="cle">Famille</div>
            <div class="valeur">${echappe(culture.famille)}</div></div>
          <div class="fait"><div class="cle">Difficulté</div>
            <div class="valeur">${"★".repeat(culture.difficulte)}${"☆".repeat(
      3 - culture.difficulte
    )}</div></div>
          <div class="fait"><div class="cle">Gel</div>
            <div class="valeur">${
              culture.rusticite.gel
                ? `Supporte${
                    culture.rusticite.temp_min_c != null
                      ? ` jusqu'à ${culture.rusticite.temp_min_c} °C`
                      : ""
                  }`
                : "Craint le gel"
            }</div></div>
        </div>
        <div style="margin-top:12px;font-size:14px">
          <div style="color:var(--secondary-text-color);font-size:11px;text-transform:uppercase">Sol</div>
          ${echappe(culture.sol)}
        </div>
        ${
          culture.arrosage.notes
            ? `<div style="margin-top:10px;font-size:14px;line-height:1.5">
                 💧 ${echappe(culture.arrosage.notes)}</div>`
            : ""
        }
        ${
          culture.conseils?.length
            ? `<div style="margin-top:12px">
                 <div style="color:var(--secondary-text-color);font-size:11px;
                             text-transform:uppercase;margin-bottom:6px">Conseils</div>
                 <ul class="conseils">${culture.conseils
                   .map((c) => `<li>${echappe(c)}</li>`)
                   .join("")}</ul>
               </div>`
            : ""
        }
      </div>`;
  }

  _blocCompagnes(compagnes) {
    if (!compagnes) return "";
    const aime = compagnes.aime || [];
    const evite = compagnes.evite || [];
    if (!aime.length && !evite.length) return "";
    return `
      <div class="carte bloc">
        <h4>Voisinage</h4>
        ${
          aime.length
            ? `<div style="font-size:13px;margin-bottom:4px">Bons voisins</div>
               <div class="compagnes" style="margin-bottom:12px">${aime
                 .map((c) => `<span class="compagne">${c.emoji} ${echappe(c.nom)}</span>`)
                 .join("")}</div>`
            : ""
        }
        ${
          evite.length
            ? `<div style="font-size:13px;margin-bottom:4px">À éloigner</div>
               <div class="compagnes">${evite
                 .map((c) => `<span class="compagne">${c.emoji} ${echappe(c.nom)}</span>`)
                 .join("")}</div>`
            : ""
        }
      </div>`;
  }

  _demanderRecolte(uid) {
    this._ouvrirFichePlante(uid);
  }

  _brancherFiche(hote) {
    const voile = hote.querySelector("#voile");
    if (voile) {
      voile.addEventListener("click", (ev) => {
        if (ev.target === voile) this._fermerFiche();
      });
    }
    hote.querySelectorAll("[data-fermer]").forEach((el) =>
      el.addEventListener("click", () => this._fermerFiche())
    );

    hote.querySelectorAll("[data-fait-fiche]").forEach((el) =>
      el.addEventListener("click", async () => {
        const corr = EVT_POUR_ETAPE[el.dataset.etape];
        if (!corr) return;
        if (corr.evenement === "recolte") {
          const champ = hote.querySelector("#qte-recolte");
          champ?.focus();
          return;
        }
        el.disabled = true;
        await this._noter(el.dataset.faitFiche, corr.evenement,
          corr.mode ? { mode: corr.mode } : {});
      })
    );

    hote.querySelectorAll("[data-recolter]").forEach((el) =>
      el.addEventListener("click", async () => {
        const champ = hote.querySelector("#qte-recolte");
        const brut = champ?.value?.trim();
        el.disabled = true;
        await this._noter(el.dataset.recolter, "recolte",
          brut ? { quantite_g: Number(brut) } : {});
      })
    );

    hote.querySelectorAll("[data-ajouter]").forEach((el) =>
      el.addEventListener("click", async () => {
        el.disabled = true;
        const zone = hote.querySelector("#sel-zone-ajout")?.value;
        const surnom = hote.querySelector("#champ-surnom-ajout")?.value?.trim();
        const reponse = await this._appeler({
          type: "potager/ajouter",
          culture_id: el.dataset.ajouter,
          zone: zone || "pleine-terre",
          surnom: surnom || null,
        });
        if (reponse?.uid) {
          this._vue = "potager";
          this.shadowRoot
            .getElementById("nav")
            .querySelectorAll("button")
            .forEach((b) =>
              b.setAttribute("aria-selected", String(b.dataset.vue === "potager"))
            );
          this._fermerFiche();
          this._rendreVue();
        }
      })
    );

    hote.querySelectorAll("[data-annuler]").forEach((el) =>
      el.addEventListener("click", async () => {
        el.disabled = true;
        await this._appeler({ type: "potager/annuler", uid: el.dataset.annuler });
      })
    );

    hote.querySelectorAll("[data-retirer]").forEach((el) =>
      el.addEventListener("click", async () => {
        if (!confirm("Retirer cette plante et son journal ?")) return;
        el.disabled = true;
        await this._appeler({ type: "potager/retirer", uid: el.dataset.retirer });
        this._fermerFiche();
      })
    );

    const modifier = (champs) =>
      this._appeler({ type: "potager/modifier", ...champs });

    const zone = hote.querySelector("#sel-zone");
    if (zone) {
      zone.addEventListener("change", () =>
        modifier({ uid: zone.dataset.uid, zone: zone.value })
      );
    }
    const surnom = hote.querySelector("#champ-surnom");
    if (surnom) {
      surnom.addEventListener("change", () =>
        modifier({ uid: surnom.dataset.uid, surnom: surnom.value.trim() || null })
      );
    }
    const notifs = hote.querySelector("#bascule-notifs");
    if (notifs) {
      notifs.addEventListener("change", () =>
        modifier({ uid: notifs.dataset.uid, notifs: notifs.checked })
      );
    }
    const rappel = hote.querySelector("#champ-rappel");
    if (rappel) {
      rappel.addEventListener("change", () =>
        modifier({ uid: rappel.dataset.uid, rappel_jours: Number(rappel.value) })
      );
    }
  }
}

customElements.define("potager-panel", PotagerPanel);
