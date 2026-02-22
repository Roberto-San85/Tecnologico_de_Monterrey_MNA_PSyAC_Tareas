from __future__ import annotations
from typing import Optional

from .models import Hotel, Customer
from .storage import JsonStorage


class HotelService:
    """Operaciones para hoteles."""

    def __init__(self, storage: JsonStorage) -> None:
        self.storage = storage

    def create(self, name: str, total_rooms: int) -> Hotel:
        hotels = self.storage.load_hotels()
        hotel = Hotel.create(name, total_rooms)
        hotels.append(hotel)
        self.storage.save_hotels(hotels)
        return hotel

    def delete(self, hotel_id: str) -> bool:
        hotels = self.storage.load_hotels()
        new_hotels = [h for h in hotels if h.id != hotel_id]
        if len(new_hotels) == len(hotels):
            return False
        self.storage.save_hotels(new_hotels)
        return True

    def get(self, hotel_id: str) -> Optional[Hotel]:
        for h in self.storage.load_hotels():
            if h.id == hotel_id:
                return h
        return None

    def update(self, hotel_id: str, *, name: Optional[str] = None,
               total_rooms: Optional[int] = None) -> Optional[Hotel]:
        hotels = self.storage.load_hotels()
        updated = None
        new_hotels: list[Hotel] = []
        for h in hotels:
            if h.id == hotel_id:
                new_name = (name.strip() if isinstance(name, str)
                            and name.strip() else h.name)
                new_total = (total_rooms if isinstance(total_rooms, int)
                             and total_rooms > 0 else h.total_rooms)
                updated = Hotel(id=h.id, name=new_name, total_rooms=new_total)
                new_hotels.append(updated)
            else:
                new_hotels.append(h)
        if updated is None:
            return None
        self.storage.save_hotels(new_hotels)
        return updated


class CustomerService:
    """Operaciones para clientes."""

    def __init__(self, storage: JsonStorage) -> None:
        self.storage = storage

    def create(self, name: str, email: str) -> Customer:
        customers = self.storage.load_customers()
        c = Customer.create(name, email)
        customers.append(c)
        self.storage.save_customers(customers)
        return c

    def delete(self, customer_id: str) -> bool:
        customers = self.storage.load_customers()
        new_customers = [c for c in customers if c.id != customer_id]
        if len(new_customers) == len(customers):
            return False
        self.storage.save_customers(new_customers)
        return True

    def get(self, customer_id: str) -> Optional[Customer]:
        for c in self.storage.load_customers():
            if c.id == customer_id:
                return c
        return None

    def update(self, customer_id: str, *, name: Optional[str] = None,
               email: Optional[str] = None) -> Optional[Customer]:
        customers = self.storage.load_customers()
        updated = None
        new_customers: list[Customer] = []
        for c in customers:
            if c.id == customer_id:
                new_name = (name.strip() if isinstance(name, str)
                            and name.strip() else c.name)
                new_email = (email.strip() if isinstance(email, str)
                             and email.strip() else c.email)
                updated = Customer(id=c.id, name=new_name, email=new_email)
                new_customers.append(updated)
            else:
                new_customers.append(c)
        if updated is None:
            return None
        self.storage.save_customers(new_customers)
        return updated
