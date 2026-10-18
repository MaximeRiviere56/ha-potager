/**
 * Carte Lovelace « Tâches du potager ».
 *
 * Elle lit les attributs du capteur `sensor.*_actions_a_mener` : aucune requête
 * supplémentaire, donc elle s'affiche instantanément sur un tableau de bord
 * déjà chargé. Le bouton « Fait » écrit au journal par la même commande que le
 * panneau, ce qui en fait un troisième chemin vers le suivi réel.
 *
 * Usage :
 *   type: custom:potager-card
 *   entity: sensor.mon_potager_actions_a_mener   # facultatif, détecté sinon
 *   titre: Au potager
 *   max: 5
 */

const EVT_POUR_ETAPE = {
  semis_interieur: { evenement: "seme", mode: "interieur" },
  semis_direct: { evenement: "seme", mode: "direct" },
  repiquage: { evenement: "repique" },
  plantation: { evenement: "plante" },
  recolte: { evenement: "recolte" },
};

const echappe = (texte) => {
  const div = document.createElement("div");
  div.textContent = texte == null ? "" : String(texte);
  return div.innerHTML;
};

const quand = (jours, enCours) => {
  if (enCours) return "c'est le moment";
  if (jours === 0) return "aujourd'hui";
  if (jours === 1) return "demain";
  if (jours > 1) return `dans ${jours} jours`;
  return `depuis ${Math.abs(jours)} jours`;
};

class PotagerCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._occupe = new Set();
  }

  setConfig(config) {
    this._config = { titre: "Au potager", max: 5, ...config };
    this._rendu = false;
  }

  getCardSize() {
    return 1 + Math.min(this._actions().length, this._config?.max ?? 5);
  }

  set hass(hass) {
    this._hass = hass;
    this._rendre();
  }

  /** Le capteur est détecté si l'utilisateur ne l'a pas nommé : une entité de
   *  plus à saisir pour rien est une entité de trop. */
  _entite() {
    if (this._config?.entity) return this._config.entity;
    return Object.keys(this._hass?.states || {}).find(
      (id) => id.startsWith("sensor.") && id.endsWith("_actions_a_mener")
    );
  }

  _actions() {
    const etat = this._hass?.states?.[this._entite()];
    return etat?.attributes?.actions || [];
  }

  async _noter(action, bouton) {
    const corr = EVT_POUR_ETAPE[action.etape];
    if (!corr) return;
    bouton.disabled = true;
    this._occupe.add(action.uid);
    try {
      await this._hass.callWS({
        type: "potager/noter",
        uid: action.uid,
        evenement: corr.evenement,
        ...(corr.mode ? { mode: corr.mode } : {}),
      });
    } catch (err) {
      bouton.disabled = false;
      this._erreur = err?.message || "Action refusée.";
      this._rendu = false;
      this._rendre();
    } finally {
      this._occupe.delete(action.uid);
    }
  }

  _rendre() {
    if (!this._hass || !this._config) return;

    const entite = this._entite();
    if (!entite) {
      this.shadowRoot.innerHTML = `<ha-card header="${echappe(this._config.titre)}">
          <div style="padding:16px;color:var(--secondary-text-color)">
            Capteur du potager introuvable. L'intégration Mon Potager est-elle installée ?
          </div>
        </ha-card>`;
      return;
    }

    const actions = this._actions().slice(0, this._config.max);
    const signature = JSON.stringify(actions) + (this._erreur || "");
    if (this._rendu && signature === this._signature) return;
    this._signature = signature;
    this._rendu = true;

    this.shadowRoot.innerHTML = `
      <style>
        ha-card { overflow: hidden; }
        .ligne {
          display: flex; align-items: center; gap: 12px;
          padding: 10px 16px; border-top: 1px solid var(--divider-color);
        }
        .ligne:first-of-type { border-top: 0; }
        .emoji { font-size: 24px; line-height: 1; }
        .corps { flex: 1; min-width: 0; }
        .nom { font-size: 15px; }
        .detail { font-size: 12px; color: var(--secondary-text-color); margin-top: 1px; }
        .urgent .verbe { color: var(--warning-color, #ef6c00); font-weight: 500; }
        button {
          border: 0; border-radius: 999px; padding: 7px 14px; cursor: pointer;
          background: var(--primary-color); color: var(--text-primary-color, #fff);
          font-size: 13px; font-weight: 500; font-family: inherit;
        }
        button:disabled { opacity: .5; cursor: default; }
        .vide { padding: 20px 16px; color: var(--secondary-text-color); text-align: center; }
        .erreur { padding: 10px 16px; color: var(--error-color); font-size: 13px; }
        a.lien {
          display: block; padding: 10px 16px; text-align: center;
          color: var(--primary-color); text-decoration: none; font-size: 13px;
          border-top: 1px solid var(--divider-color);
        }
      </style>
      <ha-card header="${echappe(this._config.titre)}">
        ${this._erreur ? `<div class="erreur">${echappe(this._erreur)}</div>` : ""}
        ${
          actions.length
            ? actions
                .map(
                  (a, index) => `
              <div class="ligne ${a.en_cours ? "urgent" : ""}">
                <div class="emoji">${a.emoji || "🌱"}</div>
                <div class="corps">
                  <div class="nom">${echappe(a.plante)}</div>
                  <div class="detail">
                    <span class="verbe">${echappe(a.action)}</span> ·
                    ${quand(a.jours_restants, a.en_cours)} · ${echappe(a.zone)}
                  </div>
                </div>
                ${
                  EVT_POUR_ETAPE[a.etape]
                    ? `<button data-index="${index}">Fait</button>`
                    : ""
                }
              </div>`
                )
                .join("")
            : `<div class="vide">Rien à faire au potager aujourd'hui 🌿</div>`
        }
        <a class="lien" href="/potager">Ouvrir Mon Potager →</a>
      </ha-card>`;

    this.shadowRoot.querySelectorAll("button[data-index]").forEach((bouton) =>
      bouton.addEventListener("click", () => {
        this._erreur = null;
        this._noter(actions[Number(bouton.dataset.index)], bouton);
      })
    );
  }

  static getStubConfig() {
    return { titre: "Au potager", max: 5 };
  }
}

customElements.define("potager-card", PotagerCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "potager-card",
  name: "Tâches du potager",
  description: "Ce qu'il y a à semer, repiquer ou récolter, avec un bouton pour le noter.",
  preview: true,
});
