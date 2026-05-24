"""
Tests for gTools/install.py

`install.py` is the Maya drag-and-drop installer. It computes a target
.mod file under the user's Maya modules dir and writes a substituted
version of the bundled gTools.mod. The whole `onMayaDroppedPythonFile`
body is wrapped in a bare `except:` (install.py:81), so failures only
surface as a critical confirmDialog — these tests pin both the happy
path and that failure-dialog contract.
"""

import importlib
import os
import stat
import sys

import pytest


@pytest.fixture
def install_module():
    """Import install fresh so module-level constants are clean."""
    sys.modules.pop("install", None)
    import install
    return importlib.reload(install)


@pytest.fixture
def install_env(tmp_path, install_module, monkeypatch):
    """
    Wire install.py to a sandboxed source + target directory containing a
    fake gTools.mod with the template placeholder.
    """
    src = tmp_path / "src"
    src.mkdir()
    (src / "gTools.mod").write_text(
        "+ gTools 1.0 [REPLACE_WITH_TOOLS_DIR]\nscripts: setup\n"
    )
    target_dir = tmp_path / "maya_modules"
    monkeypatch.setattr(install_module, "INSTALL_SOURCE", str(src))
    monkeypatch.setattr(install_module, "MAYA_MODULES_PATH", str(target_dir))
    return install_module, src, target_dir


class TestCheckOrMakeFileDirectory:
    def test_creates_missing_parent_chain(self, install_module, tmp_path):
        target = tmp_path / "new" / "deep" / "file.mod"
        result = install_module.checkOrMakeFileDirectory(str(target))
        assert os.path.isdir(str(tmp_path / "new" / "deep"))
        assert result == str(tmp_path / "new" / "deep")

    def test_existing_parent_is_left_alone(self, install_module, tmp_path):
        existing = tmp_path / "exists"
        existing.mkdir()
        target = existing / "file.mod"
        result = install_module.checkOrMakeFileDirectory(str(target))
        assert result == str(existing)
        assert os.path.isdir(str(existing))


class TestOnMayaDroppedPythonFile:
    def test_writes_target_mod_file(self, install_env):
        install_module, _, target_dir = install_env
        install_module.onMayaDroppedPythonFile()
        assert (target_dir / "gTools.mod").is_file()

    def test_substitutes_install_source_path(self, install_env):
        install_module, src, target_dir = install_env
        install_module.onMayaDroppedPythonFile()
        contents = (target_dir / "gTools.mod").read_text()
        assert "[REPLACE_WITH_TOOLS_DIR]" not in contents
        assert str(src) in contents

    def test_preserves_non_template_lines(self, install_env):
        install_module, _, target_dir = install_env
        install_module.onMayaDroppedPythonFile()
        contents = (target_dir / "gTools.mod").read_text()
        assert "scripts: setup" in contents

    def test_creates_modules_dir_when_missing(self, install_env):
        install_module, _, target_dir = install_env
        assert not target_dir.exists()
        install_module.onMayaDroppedPythonFile()
        assert target_dir.is_dir()

    def test_overwrites_read_only_target(self, install_env):
        install_module, src, target_dir = install_env
        target_dir.mkdir()
        target = target_dir / "gTools.mod"
        target.write_text("STALE CONTENT")
        os.chmod(str(target), stat.S_IREAD)
        try:
            install_module.onMayaDroppedPythonFile()
            contents = target.read_text()
            assert "STALE CONTENT" not in contents
            assert str(src) in contents
        finally:
            # Ensure tmp cleanup can remove the file.
            if target.exists():
                os.chmod(str(target), stat.S_IWRITE | stat.S_IREAD)

    def test_shows_success_dialog(self, install_env, monkeypatch):
        install_module, _, _ = install_env
        captured = []
        monkeypatch.setattr(
            install_module.cmds,
            "confirmDialog",
            lambda **kw: captured.append(kw),
        )
        install_module.onMayaDroppedPythonFile()
        assert captured, "expected confirmDialog to be called"
        assert all(kw.get("icon") != "critical" for kw in captured)
        assert any("Successfully" in kw.get("message", "") for kw in captured)


class TestOnMayaDroppedPythonFileFailureHandling:
    def test_missing_source_mod_surfaces_critical_dialog(
        self, install_module, tmp_path, monkeypatch
    ):
        # No gTools.mod placed at INSTALL_SOURCE; the open() will raise and
        # the bare except in onMayaDroppedPythonFile should convert it to a
        # critical confirmDialog. Pinning the swallow-and-dialog behaviour.
        src = tmp_path / "src"
        src.mkdir()
        target_dir = tmp_path / "maya_modules"
        monkeypatch.setattr(install_module, "INSTALL_SOURCE", str(src))
        monkeypatch.setattr(install_module, "MAYA_MODULES_PATH", str(target_dir))
        captured = []
        monkeypatch.setattr(
            install_module.cmds,
            "confirmDialog",
            lambda **kw: captured.append(kw),
        )

        install_module.onMayaDroppedPythonFile()

        assert captured, "expected confirmDialog to be called"
        assert any(kw.get("icon") == "critical" for kw in captured)
