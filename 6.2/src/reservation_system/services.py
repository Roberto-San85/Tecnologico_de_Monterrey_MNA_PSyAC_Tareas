from __future__ import annotations
from typing import Optional
from .models import Hotel
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
