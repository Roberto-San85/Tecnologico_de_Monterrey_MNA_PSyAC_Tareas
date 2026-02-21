from __future__ import annotations
from dataclasses import dataclass
import uuid
import re


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

# ... (encima ya existe Hotel y _new_id)


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True, slots=True)
class Customer:
    """Cliente con email válido."""
    id: str
    name: str
    email: str

    @staticmethod
    def create(name: str, email: str) -> "Customer":
        if not name or not name.strip():
            raise ValueError("Customer.name no puede estar vacío")
        if not EMAIL_RE.match(email or ""):
            raise ValueError("Customer.email inválido")
        return Customer(id=_new_id(), name=name.strip(), email=email.strip())
