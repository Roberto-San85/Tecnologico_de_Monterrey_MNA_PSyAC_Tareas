from __future__ import annotations
from dataclasses import dataclass
import uuid


def _new_id() -> str:
    """Genera un identificador único."""
    return uuid.uuid4().hex


@dataclass(frozen=True, slots=True)
class Hotel:
    """Representa un hotel con capacidad finita de habitaciones."""

    id: str
    name: str
    total_rooms: int

    @staticmethod
    def create(name: str, total_rooms: int) -> "Hotel":
        if not name or not name.strip():
            raise ValueError("Hotel.name no puede estar vacío")
        if total_rooms <= 0:
            raise ValueError("Hotel.total_rooms debe ser > 0")
        return Hotel(id=_new_id(), name=name.strip(), total_rooms=total_rooms)
