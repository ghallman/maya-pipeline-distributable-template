"""
Asset repository (sketch) — the data-access seam.

`AssetRepository` is an abstract interface; `SQLiteAssetRepository` is the v1
local-file implementation built on stdlib `sqlite3` (no server, no third-party
deps). The UI and host adapters depend on the *interface*, never on sqlite, so a
future shared/served/synced backend is a new subclass — a swap, not a rewrite.
This is the hook that makes the producer/ecosystem ambitions cheap.

In real gTools this DB path comes from `core.config.get_db_path()`.
"""

import sqlite3
from abc import ABC, abstractmethod
from typing import List, Optional

from core.assetmanager.models import Asset


# --------------------------------------------------------------------------- #
# Interface
# --------------------------------------------------------------------------- #
class AssetRepository(ABC):
    """Backend-agnostic CRUD surface for assets."""

    @abstractmethod
    def init_schema(self) -> None:
        """Create tables/indexes if they do not already exist."""

    @abstractmethod
    def add(self, asset: Asset) -> Asset:
        """Insert and return the asset stamped with its new id."""

    @abstractmethod
    def get(self, asset_id: int) -> Optional[Asset]:
        """Fetch one asset by id, or None."""

    @abstractmethod
    def list(self, asset_type: Optional[str] = None) -> List[Asset]:
        """List all assets, optionally filtered by type."""

    @abstractmethod
    def update(self, asset: Asset) -> Asset:
        """Persist changes to an existing asset (must have an id)."""

    @abstractmethod
    def delete(self, asset_id: int) -> None:
        """Remove an asset by id."""

    @abstractmethod
    def close(self) -> None:
        """Release any underlying connection/handles."""


# --------------------------------------------------------------------------- #
# v1 implementation — local single-file SQLite
# --------------------------------------------------------------------------- #
_TAG_SEP = ","


def _tags_to_str(tags) -> str:
    return _TAG_SEP.join(t.strip() for t in tags if t.strip())


def _str_to_tags(text: str):
    if not text:
        return tuple()
    return tuple(t for t in text.split(_TAG_SEP) if t)


class SQLiteAssetRepository(AssetRepository):
    """Single-file SQLite backend. Pass ':memory:' for a throwaway test DB."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        # check_same_thread=False keeps it usable from a Qt event loop later.
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self.init_schema()

    def init_schema(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS assets (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT    NOT NULL,
                asset_type TEXT    NOT NULL,
                path       TEXT    NOT NULL DEFAULT '',
                version    INTEGER NOT NULL DEFAULT 1,
                status     TEXT    NOT NULL DEFAULT 'wip',
                tags       TEXT    NOT NULL DEFAULT ''
            )
            """
        )
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_assets_type ON assets(asset_type)"
        )
        self._conn.commit()

    @staticmethod
    def _row_to_asset(row: sqlite3.Row) -> Asset:
        return Asset(
            id=row["id"],
            name=row["name"],
            asset_type=row["asset_type"],
            path=row["path"],
            version=row["version"],
            status=row["status"],
            tags=_str_to_tags(row["tags"]),
        )

    def add(self, asset: Asset) -> Asset:
        cur = self._conn.execute(
            "INSERT INTO assets (name, asset_type, path, version, status, tags) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                asset.name,
                asset.asset_type,
                asset.path,
                asset.version,
                asset.status,
                _tags_to_str(asset.tags),
            ),
        )
        self._conn.commit()
        return asset.with_id(cur.lastrowid)

    def get(self, asset_id: int) -> Optional[Asset]:
        row = self._conn.execute(
            "SELECT * FROM assets WHERE id = ?", (asset_id,)
        ).fetchone()
        return self._row_to_asset(row) if row else None

    def list(self, asset_type: Optional[str] = None) -> List[Asset]:
        if asset_type:
            rows = self._conn.execute(
                "SELECT * FROM assets WHERE asset_type = ? ORDER BY name", (asset_type,)
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM assets ORDER BY name"
            ).fetchall()
        return [self._row_to_asset(r) for r in rows]

    def update(self, asset: Asset) -> Asset:
        if asset.id is None:
            raise ValueError("Cannot update an asset without an id.")
        self._conn.execute(
            "UPDATE assets SET name=?, asset_type=?, path=?, version=?, status=?, tags=? "
            "WHERE id=?",
            (
                asset.name,
                asset.asset_type,
                asset.path,
                asset.version,
                asset.status,
                _tags_to_str(asset.tags),
                asset.id,
            ),
        )
        self._conn.commit()
        return asset

    def delete(self, asset_id: int) -> None:
        self._conn.execute("DELETE FROM assets WHERE id = ?", (asset_id,))
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()
