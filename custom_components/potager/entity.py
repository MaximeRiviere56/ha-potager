"""Socle commun des entites et gestion de leur apparition dynamique.

Particularite de cette integration : ses entites ne sont pas connues au
demarrage. Une plante ajoutee depuis le panneau doit faire apparaitre ses
entites sans rechargement, et une plante retiree doit les faire disparaitre du
registre — sinon le potager se remplirait de capteurs fantomes.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, PANEL_TITLE
from .coordinator import PotagerCoordinator


def info_appareil(entry: ConfigEntry) -> DeviceInfo:
    """Un seul appareil regroupe tout : le potager lui-meme.

    Un appareil par plante donnerait une page par legume, mais ferait churner
    le registre a chaque ajout ou retrait.
    """
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=PANEL_TITLE,
        manufacturer="Mon Potager",
        entry_type=DeviceEntryType.SERVICE,
    )


class PotagerEntity(CoordinatorEntity[PotagerCoordinator]):
    """Base des entites globales du potager."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: PotagerCoordinator, cle: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{cle}"
        self._attr_device_info = info_appareil(coordinator.entry)


class PotagerPlanteEntity(PotagerEntity):
    """Base des entites rattachees a une plante du jardin."""

    def __init__(self, coordinator: PotagerCoordinator, uid: str, suffixe: str) -> None:
        super().__init__(coordinator, f"{uid}_{suffixe}")
        self._uid = uid

    @property
    def entree(self) -> dict | None:
        """La plante telle que calculee, ou None si elle a ete retiree."""
        return self.coordinator.data["plantes"].get(self._uid)

    @property
    def available(self) -> bool:
        return super().available and self.entree is not None

    @property
    def name(self) -> str | None:
        entree = self.entree
        return entree["nom_affiche"] if entree else None


@callback
def suivre_les_plantes(
    hass: HomeAssistant,
    entry: ConfigEntry,
    coordinator: PotagerCoordinator,
    async_add_entities: AddEntitiesCallback,
    fabrique: Callable[[PotagerCoordinator, str], Iterable],
    plateforme: str,
    suffixe: str,
) -> None:
    """Cree les entites des nouvelles plantes, nettoie celles des disparues."""
    connus: set[str] = set()

    @callback
    def _synchroniser() -> None:
        presents = set(coordinator.data["plantes"])

        nouveaux = presents - connus
        if nouveaux:
            connus.update(nouveaux)
            entites = [
                entite
                for uid in sorted(nouveaux)
                for entite in fabrique(coordinator, uid)
            ]
            if entites:
                async_add_entities(entites)

        for uid in connus - presents:
            connus.discard(uid)
            _retirer_du_registre(hass, entry, uid, plateforme, suffixe)

    _synchroniser()
    entry.async_on_unload(coordinator.async_add_listener(_synchroniser))


@callback
def _retirer_du_registre(
    hass: HomeAssistant,
    entry: ConfigEntry,
    uid: str,
    plateforme: str,
    suffixe: str,
) -> None:
    registre = er.async_get(hass)
    entity_id = registre.async_get_entity_id(
        plateforme, DOMAIN, f"{entry.entry_id}_{uid}_{suffixe}"
    )
    if entity_id:
        registre.async_remove(entity_id)
