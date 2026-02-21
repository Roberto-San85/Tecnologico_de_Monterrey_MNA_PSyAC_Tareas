from __future__ import annotations
from dataclasses import dataclass
from datetime import date
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


@dataclass(frozen=True, slots=True)
class Reservation:
    """Reservación entre cliente y hotel en un rango de fechas."""
    id: str
    customer_id: str
    hotel_id: str
    check_in: date
    check_out: date

    def __post_init__(self) -> None:
        if self.check_in >= self.check_out:
            raise ValueError("Reservation.check_in debe ser < check_out")
        if not self.customer_id:
            raise ValueError("Reservation.customer_id requerido")
        if not self.hotel_id:
            raise ValueError("Reservation.hotel_id requerido")

    @staticmethod
    def create(customer_id: str,
               hotel_id: str,
               check_in: date,
               check_out: date) -> "Reservation":
        return Reservation(id=_new_id(),
                           customer_id=customer_id,
                           hotel_id=hotel_id,
                           check_in=check_in,
                           check_out=check_out)

    def overlaps(self, other: "Reservation") -> bool:
        latest_start = max(self.check_in, other.check_in)
        earliest_end = min(self.check_out, other.check_out)
        return latest_start < earliest_end


def date_from_iso(value: str) -> date:
    parts = [int(p) for p in (value or "").split("-")]
    if len(parts) != 3:
        raise ValueError("Fecha inválida, formato esperado YYYY-MM-DD")
    return date(parts[0], parts[1], parts[2])


def date_to_iso(d: date) -> str:
    return d.isoformat()
