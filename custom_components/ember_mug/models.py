"""Data class to persist configuration state."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ember_mug import EmberMug

    from .coordinator import MugDataUpdateCoordinator


@dataclass
class HassMugData:
    """Class to persist state."""

    mug: EmberMug
    coordinator: MugDataUpdateCoordinator
