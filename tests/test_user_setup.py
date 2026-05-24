"""
Tests for gTools/setup/userSetup.py

userSetup orchestrates the Maya-side boot:
  - `bootImporter(impDic)` — dynamically imports & runs a startup module.
  - `bootCore()` — boots the core startup, returns True/False.
  - `bootStartups()` — iterates additional startups, swallows per-entry failures.
  - `bootLoader()` — top-level orchestrator that gates on `startupImported`.

The file uses Python 2 idioms (`exec ('...')` then `reload(tempMod)`) that
are broken on Python 3. The bootImporter test pins this so a future port
surfaces here.
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
    def test_uses_undefined_reload_on_py3(self, userSetup):
        # BUG: bootImporter does `exec ('import startup.X as tempMod')` then
        # `reload(tempMod)`. On Py3 `reload` is no longer a builtin (moved
        # to importlib.reload) and `exec` inside a function does not write
        # to the function's locals, so `tempMod` is also undefined. Either
        # way, this raises NameError. Pinning so a port to Py3 surfaces.
        fake = types.ModuleType("startup.fake_thing")
        fake.start = lambda: None
        sys.modules["startup.fake_thing"] = fake
        try:
            impDic = {
                "fileName": "fake_thing_startup.py",
                "importName": "fake_thing",
                "toolName": "fake_thing",
            }
            with pytest.raises(NameError):
                userSetup.bootImporter(impDic)
        finally:
            sys.modules.pop("startup.fake_thing", None)


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
