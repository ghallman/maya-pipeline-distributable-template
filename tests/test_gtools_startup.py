"""
Tests for gTools/setup/startup/gTools_startup.py

The core startup builds the gTools menu inside Maya. With the Maya stubs
in conftest, we monkeypatch cmds.menu/menuItem/deleteUI to record calls
and assert the menu construction contract.
"""

import pytest


@pytest.fixture
def gtools_startup():
    # Monkeypatch in each test gives per-test isolation, so a cached import
    # is fine here — no need to reload the module.
    from startup import gTools_startup
    return gTools_startup


class TestMenuSpec:
    """
    MENU_SPEC + _buildMenuItems is the Humble-Object split of menuSetup:
    the spec is pure data (testable with no Maya), the builder is a thin
    shell tested by the existing menuSetup tests below.
    """

    def test_spec_contains_expected_entries(self, gtools_startup):
        labels = [item["label"] for item in gtools_startup.MENU_SPEC]
        assert labels == ["Art", "Animation", "Tech", "Rigging", "Skinning"]

    def test_dividers_and_submenus_are_correctly_typed(self, gtools_startup):
        kinds = {
            item["label"]: ("divider" if item.get("divider") else "subMenu")
            for item in gtools_startup.MENU_SPEC
        }
        assert kinds == {
            "Art": "divider",
            "Animation": "subMenu",
            "Tech": "divider",
            "Rigging": "subMenu",
            "Skinning": "subMenu",
        }

    def test_build_menu_items_calls_cmds_with_spec(self, gtools_startup, monkeypatch):
        captured = []
        monkeypatch.setattr(
            gtools_startup.cmds,
            "menuItem",
            lambda **kw: captured.append(kw),
        )
        gtools_startup._buildMenuItems("PARENT", gtools_startup.MENU_SPEC)
        assert len(captured) == len(gtools_startup.MENU_SPEC)
        assert all(kw["parent"] == "PARENT" for kw in captured)
        # Dividers and submenus translate to the matching cmds.menuItem kwarg.
        art = next(kw for kw in captured if kw["label"] == "Art")
        animation = next(kw for kw in captured if kw["label"] == "Animation")
        assert art.get("divider") is True
        assert animation.get("subMenu") is True


class TestMenuSetup:
    def test_creates_top_level_menu_when_parent_exists(self, gtools_startup, monkeypatch):
        menu_calls = []
        item_calls = []

        def _menu(*args, **kwargs):
            menu_calls.append((args, kwargs))
            if kwargs.get("exists"):
                return False
            return "gToolsMenu"  # truthy handle so item-creation branch runs

        monkeypatch.setattr(gtools_startup.cmds, "menu", _menu)
        monkeypatch.setattr(
            gtools_startup.cmds,
            "menuItem",
            lambda *a, **kw: item_calls.append((a, kw)),
        )

        gtools_startup.menuSetup()

        create_calls = [kw for _, kw in menu_calls if not kw.get("exists")]
        assert any(kw.get("l") == "gTools" for kw in create_calls)
        # Expect at least the five labelled items defined in menuSetup.
        labels = {kw.get("label") for _, kw in item_calls}
        assert {"Art", "Animation", "Tech", "Rigging", "Skinning"} <= labels

    def test_deletes_existing_menu_before_recreating(self, gtools_startup, monkeypatch):
        deleted = []

        def _menu(*args, **kwargs):
            if kwargs.get("exists"):
                return True
            return "gToolsMenu"

        monkeypatch.setattr(gtools_startup.cmds, "menu", _menu)
        monkeypatch.setattr(gtools_startup.cmds, "menuItem", lambda *a, **kw: None)
        monkeypatch.setattr(
            gtools_startup.cmds, "deleteUI", lambda *a, **kw: deleted.append(a)
        )
        gtools_startup.menuSetup()
        assert deleted == [("gToolsMenu",)]

    def test_warns_when_menu_handle_is_falsy(self, gtools_startup, monkeypatch):
        warnings = []
        monkeypatch.setattr(gtools_startup.cmds, "menu", lambda *a, **kw: None)
        monkeypatch.setattr(
            gtools_startup.cmds, "warning", lambda msg: warnings.append(msg)
        )
        gtools_startup.menuSetup()
        assert warnings, "expected a cmds.warning when the menu handle is falsy"


class TestStart:
    def test_success_path_runs_menusetup(self, gtools_startup, monkeypatch):
        called = []
        monkeypatch.setattr(
            gtools_startup, "menuSetup", lambda parent="MayaWindow": called.append(parent)
        )
        gtools_startup.start()
        assert called == ["MayaWindow"]

    def test_failure_in_menusetup_is_swallowed(self, gtools_startup, monkeypatch):
        def _boom(*a, **kw):
            raise RuntimeError("menu blew up")

        monkeypatch.setattr(gtools_startup, "menuSetup", _boom)
        # Should not propagate — start() catches bare Exception.
        gtools_startup.start()

    def test_import_error_in_menusetup_is_swallowed(self, gtools_startup, monkeypatch):
        def _boom(*a, **kw):
            raise ImportError("missing module")

        monkeypatch.setattr(gtools_startup, "menuSetup", _boom)
        gtools_startup.start()
