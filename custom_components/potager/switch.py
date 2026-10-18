"""Un interrupteur de rappels par plante.

Pourquoi une entite plutot qu'une simple case dans le panneau : un interrupteur
est automatisable. « Coupe les rappels du potager quand je suis en vacances »
devient une automatisation ordinaire, sans rien connaitre de l'integration.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import PotagerCoordinator
from .entity import PotagerPlanteEntity, suivre_les_plantes

PLATEFORME = "switch"
SUFFIXE = "notifs"


async def async_setup_entry(
    hass: HomeAssistant, entry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: PotagerCoordinator = entry.runtime_data
    suivre_les_plantes(
        hass,
        entry,
        coordinator,
        async_add_entities,
        lambda coord, uid: [NotifsSwitch(coord, uid)],
        PLATEFORME,
        SUFFIXE,
    )


class NotifsSwitch(PotagerPlanteEntity, SwitchEntity):
    """L'etat vit dans le store, pas dans l'entite : le panneau et
    l'interrupteur lisent ainsi la meme verite."""

    _attr_icon = "mdi:bell-ring-outline"

    def __init__(self, coordinator: PotagerCoordinator, uid: str) -> None:
        super().__init__(coordinator, uid, SUFFIXE)

    @property
    def name(self) -> str | None:
        entree = self.entree
        return f"Rappels {entree['nom_affiche']}" if entree else None

    @property
    def is_on(self) -> bool:
        entree = self.entree
        return bool(entree["plante"].get("notifs", True)) if entree else False

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._async_definir(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._async_definir(False)

    async def _async_definir(self, actif: bool) -> None:
        store = self.coordinator.store
        await self.coordinator.async_appliquer(
            lambda: store.modifier_plante(self._uid, notifs=actif)
        )
