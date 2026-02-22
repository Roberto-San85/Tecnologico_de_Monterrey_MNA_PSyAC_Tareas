from __future__ import annotations
from typing import Iterable
import json
import logging
import os
import tempfile
from dataclasses import asdict
from pathlib import Path
from .models import Hotel

LOGGER = logging.getLogger(__name__)


class JsonStorage:
    """Persistencia en JSON. Robusta ante datos inválidos."""

    def __init__(self, base_dir: str | Path) -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._files = {
            "hotels": self.base_dir / "hotels.json",
        }
        for f in self._files.values():
            if not f.exists():
                f.write_text("[]", encoding="utf-8")

    @staticmethod
    def _safe_load(path: Path) -> list:
        try:
            raw = path.read_text(encoding="utf-8")
            if not raw.strip():
                return []
            data = json.loads(raw)
            if isinstance(data, list):
                return data
            LOGGER.error("Archivo %s no contiene una lista JSON; se ignora",
                         path)
            return []
        except (json.JSONDecodeError, ValueError) as exc:  # noqa: BLE001
            LOGGER.error("Error leyendo %s: %s", path, exc)
            return []

    @staticmethod
    def _safe_dump(path: Path, data: Iterable[dict]) -> None:
        tmp_fd, tmp_name = tempfile.mkstemp(prefix=path.name, dir=path.parent)
        try:
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as fh:
                json.dump(list(data), fh, ensure_ascii=False, indent=2)
            os.replace(tmp_name, path)
        finally:
            try:
                if os.path.exists(tmp_name):
                    os.remove(tmp_name)
            except OSError:
                pass

    def load_hotels(self) -> list[Hotel]:
        items: list[Hotel] = []
        for obj in self._safe_load(self._files["hotels"]):
            try:
                items.append(Hotel(id=str(obj["id"]),
                                   name=str(obj.get("name")),
                                   total_rooms=int(obj.get("total_rooms"))))
            except (json.JSONDecodeError, ValueError,
                    TypeError) as exc:  # noqa: BLE001
                LOGGER.error("Hotel inválido en JSON: %s", exc)
        return items

    def save_hotels(self, hotels: Iterable[Hotel]) -> None:
        self._safe_dump(self._files["hotels"], (asdict(h) for h in hotels))
