"""
Tests for gTools/setup/userSetup.py

userSetup orchestrates the Maya-side boot:
  - bootImporter(impDic) — dynamically imports & runs a startup module.
  - bootCore() — boots the core startup, returns True/False.
  - bootStartups() — iterates additional startups, swallows per-entry failures.
  - bootLoader() — top-level orchestrator that gates on startupImported.
"""

import importlib
import sys
import types

import pytest


@pytest.fixture
def userSetup():
    """Reload userSetup fresh so module-level flags are not stale."""
    sys.modules.pop("userSetup", None)
    import userSetup as us
    return importlib.reload(us)


# ---------------------------------------------------------------------------
# bootImporter — Python 2 idioms, broken on Py3
# ---------------------------------------------------------------------------

class TestBootImporter:
    def test_imports_module_and_calls_start(self, userSetup, monkeypatch):
        # Stub the module-local _reload seam — hot-reload is a dev-loop
        # side-effect, not what this test pins. Patching userSetup._reload
        # (instead of userSetup.importlib.reload) avoids mutating the global
        # importlib module for the duration of the test.
        started = []
        fake = types.ModuleType("startup.fake_thing")
        fake.start = lambda: started.append("started")
        sys.modules["startup.fake_thing"] = fake
        monkeypatch.setattr(userSetup, "_reload", lambda m: m)
        try:
            impDic = {
                "fileName": "fake_thing_startup.py",
                "importName": "fake_thing",
                "toolName": "fake_thing",
            }
            userSetup.bootImporter(impDic)
            assert started == ["started"]
        finally:
            sys.modules.pop("startup.fake_thing", None)

    def test_propagates_import_error_for_missing_module(self, userSetup):
        impDic = {
            "fileName": "no_such_thing_startup.py",
            "importName": "no_such_thing_xyz_zzz",
            "toolName": "no_such_thing",
        }
        with pytest.raises(ImportError):
            userSetup.bootImporter(impDic)


# ---------------------------------------------------------------------------
# bootCore
# ---------------------------------------------------------------------------

class TestBootCore:
    def test_returns_false_when_core_dict_empty(self, userSetup, monkeypatch):
        import startup
        monkeypatch.setattr(startup, "core", {})
        assert userSetup.bootCore() is False

    def test_returns_true_when_bootimporter_succeeds(self, userSetup, monkeypatch):
        import startup
        core_dict = {
            "fileName": "x_startup.py",
            "importName": "x_startup",
            "toolName": "x",
        }
        monkeypatch.setattr(startup, "core", core_dict)
        called = []
        monkeypatch.setattr(userSetup, "bootImporter", lambda d: called.append(d))
        assert userSetup.bootCore() is True
        assert called == [core_dict]

    def test_returns_false_when_bootimporter_raises(self, userSetup, monkeypatch):
        import startup
        monkeypatch.setattr(
            startup,
            "core",
            {"fileName": "x.py", "importName": "x", "toolName": "x"},
        )

        def _boom(_):
            raise RuntimeError("nope")

        monkeypatch.setattr(userSetup, "bootImporter", _boom)
        assert userSetup.bootCore() is False


# ---------------------------------------------------------------------------
# bootStartups
# ---------------------------------------------------------------------------

class TestBootStartups:
    def test_returns_false_when_startup_list_is_empty(self, userSetup, monkeypatch):
        import startup
        monkeypatch.setattr(startup, "startupList", [])
        assert userSetup.bootStartups() is False

    def test_calls_bootimporter_for_each_entry(self, userSetup, monkeypatch):
        import startup
        entries = [
            {"fileName": "a.py", "importName": "a", "toolName": "a"},
            {"fileName": "b.py", "importName": "b", "toolName": "b"},
        ]
        monkeypatch.setattr(startup, "startupList", entries)
        called = []
        monkeypatch.setattr(userSetup, "bootImporter", lambda d: called.append(d))
        userSetup.bootStartups()
        assert called == entries

    def test_continues_after_individual_failure(self, userSetup, monkeypatch):
        import startup
        entries = [
            {"fileName": "a.py", "importName": "a", "toolName": "a"},
            {"fileName": "b.py", "importName": "b", "toolName": "b"},
        ]
        monkeypatch.setattr(startup, "startupList", entries)
        called = []

        def _maybe_fail(d):
            called.append(d)
            if d["importName"] == "a":
                raise RuntimeError("nope")

        monkeypatch.setattr(userSetup, "bootImporter", _maybe_fail)
        userSetup.bootStartups()
        assert called == entries  # second entry still attempted after first failed


# ---------------------------------------------------------------------------
# bootLoader
# ---------------------------------------------------------------------------

class TestBootLoader:
    def test_short_circuits_when_startup_not_imported(self, userSetup, monkeypatch):
        monkeypatch.setattr(userSetup, "startupImported", False)
        called = []
        monkeypatch.setattr(userSetup, "bootCore", lambda: called.append("core") or True)
        monkeypatch.setattr(userSetup, "bootStartups", lambda: called.append("startups"))
        userSetup.bootLoader()
        assert called == []

    def test_runs_startups_after_successful_core(self, userSetup, monkeypatch):
        monkeypatch.setattr(userSetup, "startupImported", True)
        called = []
        monkeypatch.setattr(
            userSetup, "bootCore", lambda: (called.append("core"), True)[1]
        )
        monkeypatch.setattr(userSetup, "bootStartups", lambda: called.append("startups"))
        userSetup.bootLoader()
        assert called == ["core", "startups"]

    def test_skips_startups_when_core_fails(self, userSetup, monkeypatch):
        monkeypatch.setattr(userSetup, "startupImported", True)
        called = []
        monkeypatch.setattr(
            userSetup, "bootCore", lambda: (called.append("core"), False)[1]
        )
        monkeypatch.setattr(userSetup, "bootStartups", lambda: called.append("startups"))
        userSetup.bootLoader()
        assert called == ["core"]


# ---------------------------------------------------------------------------
# End-to-end boot smoke test (Spring contextLoads-equivalent)
# ---------------------------------------------------------------------------

class TestBootSmoke:
    def test_bootloader_drives_full_pipeline_to_menu_creation(
        self, userSetup, monkeypatch
    ):
        """
        Spring `contextLoads()`-style smoke: run the boot pipeline end-to-end
        with no module-level fakes and assert the gTools menu actually got
        built. Catches regressions in the seams between userSetup -> bootCore
        -> bootImporter -> gTools_startup.start -> menuSetup that the
        per-branch unit tests can't see.
        """
        import maya.cmds as cmds

        menu_create_calls = []

        def _menu(*args, **kwargs):
            if kwargs.get("exists"):
                return False
            menu_create_calls.append(kwargs)
            return "gToolsMenu"

        monkeypatch.setattr(cmds, "menu", _menu)
        monkeypatch.setattr(cmds, "menuItem", lambda *a, **kw: None)

        userSetup.bootLoader()

        assert any(kw.get("l") == "gTools" for kw in menu_create_calls), (
            "expected the full boot pipeline to reach menuSetup and create "
            "the gTools menu"
        )


# ---------------------------------------------------------------------------
# Module-level wiring
# ---------------------------------------------------------------------------

class TestModuleLevelWiring:
    def test_evaldeferred_called_for_bootloader(self, monkeypatch):
        # Capture cmds.evalDeferred during a fresh import and verify
        # bootLoader is the registered callback.
        recorded = []
        import maya.cmds as cmds

        monkeypatch.setattr(
            cmds, "evalDeferred", lambda fn, **kw: recorded.append((fn, kw))
        )
        sys.modules.pop("userSetup", None)
        import userSetup as us  # noqa: F401

        assert recorded, "expected userSetup to register a deferred callback"
        fn, kwargs = recorded[-1]
        assert fn is us.bootLoader
        assert kwargs.get("lp") is True
