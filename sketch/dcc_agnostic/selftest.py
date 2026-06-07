"""
Headless proof (sketch) — runs the asset-manager CORE with NO Qt and NO Maya.

This demonstrates the central claim of the DCC-agnostic design: the data layer
stands entirely on its own, which is what makes the standalone (producer) app and
future services possible. Uses an in-memory SQLite DB so it leaves nothing behind.

Run:  py -3 sketch/dcc_agnostic/selftest.py
"""

import os
import sys

# Make this folder importable as the package root (stands in for a future gTools/).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.assetmanager.models import Asset
from core.assetmanager.repository import SQLiteAssetRepository


def main():
    repo = SQLiteAssetRepository(":memory:")   # no DCC, no Qt, no file on disk

    repo.add(Asset(name="hero", asset_type="character", path="/p/hero.ma",
                   tags=("playable", "rigged")))
    repo.add(Asset(name="barrel", asset_type="prop", path="/p/barrel.ma"))
    repo.add(Asset(name="dungeon", asset_type="environment", path="/p/dungeon.ma",
                   status="review"))

    all_assets = repo.list()
    props = repo.list(asset_type="prop")

    # Round-trip an update.
    hero = next(a for a in all_assets if a.name == "hero")
    repo.update(Asset(name="hero", asset_type="character", path=hero.path,
                      version=2, status="approved", tags=hero.tags, id=hero.id))
    hero2 = repo.get(hero.id)

    print("Asset manager CORE self-test (no Qt, no Maya)")
    print("-" * 48)
    print("total assets : {}".format(len(all_assets)))
    print("prop assets  : {}".format([a.name for a in props]))
    print("hero v{} status={} tags={}".format(hero2.version, hero2.status, hero2.tags))

    assert len(all_assets) == 3
    assert [a.name for a in props] == ["barrel"]
    assert hero2.version == 2 and hero2.status == "approved"
    assert hero2.tags == ("playable", "rigged")

    repo.close()
    print("-" * 48)
    print("PASS - core runs DCC-free; standalone/maya only differ by adapter.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
