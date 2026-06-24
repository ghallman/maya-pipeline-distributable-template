"""
Tests for gTools/setup/startup/__init__.py

This package-init builds two structures at import time:
  - `core`: a dict describing the core startup module.
  - `startupList`: a list of dicts describing every additional *_startup.py
    file, excluding the core file and `template_startup.py`.

These tests cover both the real on-disk state and a controlled fake
directory loaded by reloading the module with a patched os.listdir.
"""

import importlib
import os

import startup


# ---------------------------------------------------------------------------
# Tests against the real on-disk startup directory
# ---------------------------------------------------------------------------

def test_core_dict_is_built_from_gtools_startup_file():
    assert startup.core == {
        "fileName": "gTools_startup.py",
        "importName": "gTools_startup",
        "toolName": "gTools",
    }


def test_ignore_list_contains_core_and_template():
    assert "gTools_startup.py" in startup.ignoreList
    assert "template_startup.py" in startup.ignoreList


def test_real_startup_list_excludes_ignored_files():
    # The repo currently ships only the core + template startups, so the
    # real startupList should be empty. If a future *_startup.py is added,
    # it must appear here (and not template/core).
    names = [entry["fileName"] for entry in startup.startupList]
    assert "template_startup.py" not in names
    assert "gTools_startup.py" not in names


# ---------------------------------------------------------------------------
# Tests with a fabricated startup directory (monkeypatched os.listdir)
# ---------------------------------------------------------------------------

def _reload_startup_with_listdir(monkeypatch, listing):
    monkeypatch.setattr(os, "listdir", lambda d: listing)
    return importlib.reload(startup)


def test_extra_startup_files_are_discovered(monkeypatch):
    reloaded = _reload_startup_with_listdir(
        monkeypatch,
        [
            "gTools_startup.py",
            "template_startup.py",
            "anim_startup.py",
            "rig_startup.py",
        ],
    )
    names = sorted(entry["fileName"] for entry in reloaded.startupList)
    assert names == ["anim_startup.py", "rig_startup.py"]


def test_each_startup_entry_has_three_keys(monkeypatch):
    reloaded = _reload_startup_with_listdir(
        monkeypatch,
        ["gTools_startup.py", "template_startup.py", "anim_startup.py"],
    )
    entry = reloaded.startupList[0]
    assert entry == {
        "fileName": "anim_startup.py",
        "importName": "anim_startup",
        "toolName": "anim",
    }


def test_non_startup_files_are_skipped(monkeypatch):
    reloaded = _reload_startup_with_listdir(
        monkeypatch,
        [
            "gTools_startup.py",
            "template_startup.py",
            "README.md",
            "helper.py",
            "anim_startup.py",
        ],
    )
    names = [entry["fileName"] for entry in reloaded.startupList]
    assert names == ["anim_startup.py"]


def test_listdir_failure_yields_empty_startup_list(monkeypatch):
    def _boom(_):
        raise OSError("no such directory")

    monkeypatch.setattr(os, "listdir", _boom)
    reloaded = importlib.reload(startup)
    assert reloaded.startupList == []


def teardown_module(module):
    # Restore the real on-disk state for any later tests that import startup.
    importlib.reload(startup)
