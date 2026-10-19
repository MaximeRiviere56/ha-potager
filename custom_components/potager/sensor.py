"""Capteurs : etat du potager, recolte de la saison, et une fiche par plante."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfMass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import PotagerCoordinator, libelle_phase
from .entity import PotagerEntity, PotagerPlanteEntity, suivre_les_plantes
from .lifecycle import PHASES_LIBELLES

PLATEFORME = "sensor"
SUFFIXE = "etat"


async def async_setup_entry(
    hass: HomeAssistant, entry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: PotagerCoordinator = entry.runtime_data
    async_add_entities([ActionsSensor(coordinator), RecolteSensor(coordinator)])

    suivre_les_plantes(
        hass,
        entry,
        coordinator,
        async_add_entities,
        lambda coord, uid: [PlanteSensor(coord, uid)],
        PLATEFORME,
        SUFFIXE,
    )


class ActionsSensor(PotagerEntity, SensorEntity):
    """Combien d'actions reclament une attention, et lesquelles."""

    _attr_name = "Actions à mener"
    _attr_icon = "mdi:sprout"
    _attr_native_unit_of_measurement = "actions"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: PotagerCoordinator) -> None:
        super().__init__(coordinator, "actions")

    @property
    def native_value(self) -> int:
        return len(self.coordinator.data["actions"])

    @property
    def extra_state_attributes(self) -> dict:
        return {
            # `uid` et `etape` ne sont pas decoratifs : ils permettent a la
            # carte Lovelace d'enregistrer « C'est fait » sans autre requete.
            "actions": [
                {
                    "uid": action["uid"],
                    "plante": action["nom"],
                    "emoji": action["emoji"],
                    "action": action["etape"].libelle,
                    "etape": action["etape"].type,
                    "zone": action["zone"],
                    "debut": action["etape"].debut.isoformat(),
                    "fin": action["etape"].fin.isoformat(),
                    "jours_restants": action["jours_restants"],
                    "en_cours": action["en_cours"],
                }
                for action in self.coordinator.data["actions"]
            ],
            "nb_plantes": len(self.coordinator.data["plantes"]),
        }


class RecolteSensor(PotagerEntity, SensorEntity):
    """Total recolte, en kilos. `total` plutot que `total_increasing` : une
    annulation au journal doit pouvoir faire redescendre le compteur."""

    _attr_name = "Récolte de la saison"
    _attr_icon = "mdi:basket"
    _attr_device_class = SensorDeviceClass.WEIGHT
    _attr_native_unit_of_measurement = UnitOfMass.KILOGRAMS
    _attr_state_class = SensorStateClass.TOTAL
    _attr_suggested_display_precision = 2

    def __init__(self, coordinator: PotagerCoordinator) -> None:
        super().__init__(coordinator, "recolte")

    @property
    def native_value(self) -> float:
        return round(self.coordinator.data["total_recolte_g"] / 1000, 3)

    @property
    def extra_state_attributes(self) -> dict:
        par_culture: dict[str, int] = {}
        for entree in self.coordinator.data["plantes"].values():
            grammes = entree["resume"]["total_recolte_g"]
            if grammes:
                nom = entree["culture"]["nom"]
                par_culture[nom] = par_culture.get(nom, 0) + grammes
        return {
            "par_culture_g": dict(
                sorted(par_culture.items(), key=lambda kv: -kv[1])
            ),
            "nb_recoltes": sum(
                e["resume"]["nb_recoltes"]
                for e in self.coordinator.data["plantes"].values()
            ),
        }


class PlanteSensor(PotagerPlanteEntity, SensorEntity):
    """Une plante du jardin : sa phase en etat, sa fiche en attributs."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = list(PHASES_LIBELLES.values())

    def __init__(self, coordinator: PotagerCoordinator, uid: str) -> None:
        super().__init__(coordinator, uid, SUFFIXE)

    @property
    def icon(self) -> str:
        entree = self.entree
        if entree is None:
            return "mdi:sprout"
        return {
            "prevu": "mdi:calendar-clock",
            "seme": "mdi:seed",
            "plante": "mdi:sprout",
            "en_recolte": "mdi:basket",
            "termine": "mdi:check-circle-outline",
            "perdu": "mdi:emoticon-sad-outline",
        }.get(entree["resume"]["phase"], "mdi:sprout")

    @property
    def native_value(self) -> str | None:
        entree = self.entree
        return libelle_phase(entree["resume"]["phase"]) if entree else None

    @property
    def extra_state_attributes(self) -> dict:
        entree = self.entree
        if entree is None:
            return {}

        fiche = entree["culture"]
        infos = entree["resume"]
        prochaine = entree["prochaine"]
        aujourdhui = self.coordinator.data["calcule_le"]

        attributs = {
            # L'uid est ce que reclament les services `potager.*`. Sans lui
            # expose ici, il faudrait aller le chercher dans le stockage
            # interne : les services seraient inutilisables en automatisation.
            "uid": entree["uid"],
            "culture": fiche["nom"],
            "culture_id": fiche["id"],
            "famille": fiche["famille"],
            "zone": entree["zone"]["nom"],
            "exposition": fiche["exposition"],
            "arrosage_besoin": fiche["arrosage"]["besoin"],
            "arrosage_tous_les_jours": fiche["arrosage"]["frequence_jours"],
            "arrosage_notes": fiche["arrosage"]["notes"],
            "espacement_cm": fiche["espacement_cm"],
            "sol": fiche["sol"],
            "perenne": bool(fiche.get("perenne")),
            "conseils": fiche["conseils"],
            "date_semis": (
                infos["date_semis"].isoformat() if infos["date_semis"] else None
            ),
            "date_mise_en_place": (
                infos["date_mise_en_place"].isoformat()
                if infos["date_mise_en_place"]
                else None
            ),
            "nb_recoltes": infos["nb_recoltes"],
            "recolte_totale_g": infos["total_recolte_g"],
            "notifs_actives": entree["plante"].get("notifs", True),
        }

        if prochaine is not None:
            attributs.update(
                {
                    "prochaine_action": prochaine.libelle,
                    "prochaine_date": prochaine.debut.isoformat(),
                    "prochaine_fin": prochaine.fin.isoformat(),
                    "jours_restants": prochaine.jours_restants(aujourdhui),
                    "fenetre_ouverte": prochaine.contient(aujourdhui),
                    # « reelle » signale une date calculee depuis le journal, et
                    # non depuis la moyenne saisonniere.
                    "calculee_depuis_le_journal": prochaine.reelle,
                }
            )
        else:
            attributs["prochaine_action"] = None

        return attributs
