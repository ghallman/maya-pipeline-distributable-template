"""
Tests for gTools/core/utils/ui_utils.py

These exercise the post-Py3-port surface area of the UI utilities:

  * Module imports cleanly on Python 3 — pins the cStringIO/long/exec-X-in-Y
    syntax fixes so a regression to Py2 idioms fails fast.
  * `MAYAWINDOW` falls back to None when Maya's MQtUtil isn't available
    (i.e. when running outside Maya), so that other modules can still
    import this one in CI.
  * `loadUiType` parses .ui XML, exec()s the compileUi output, and resolves
    the form class + base widget class. compileUi is stubbed so we don't
    require pyside2uic at test time.
"""

import pytest


# ---------------------------------------------------------------------------
# Module-level
# ---------------------------------------------------------------------------

def test_module_imports_on_py3():
    # If any Py2-only idiom regresses (`exec X in Y`, `long(...)`, cStringIO)
    # this import itself raises a SyntaxError or NameError.
    from core.utils import ui_utils  # noqa: F401


def test_mayawindow_falls_back_to_none_without_maya():
    from core.utils import ui_utils
    # conftest stubs maya.OpenMayaUI as an empty module, so MQtUtil is missing
    # and the module-level try/except should set MAYAWINDOW to None instead
    # of crashing the import.
    assert ui_utils.MAYAWINDOW is None


def test_compileui_and_wrapinstance_are_none_without_pyside():
    from core.utils import ui_utils
    # In CI we don't have PySide installed; the import fallback should leave
    # both bindings at None so the module remains importable.
    assert ui_utils.compileUi is None
    assert ui_utils.wrapInstance is None


# ---------------------------------------------------------------------------
# loadUiType
# ---------------------------------------------------------------------------

def _write_ui_file(path, form_class="MyWindow", widget_class="QMainWindow"):
    path.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<ui version="4.0">\n'
        f' <class>{form_class}</class>\n'
        f' <widget class="{widget_class}" name="{form_class}">\n'
        ' </widget>\n'
        '</ui>\n'
    )


class TestLoadUiType:
    def test_returns_form_class_and_base_class(self, tmp_path, monkeypatch):
        from core.utils import ui_utils

        ui_path = tmp_path / "MyWindow.ui"
        _write_ui_file(ui_path, form_class="MyWindow", widget_class="QMainWindow")

        def fake_compile(src, out, indent=0):
            out.write("class Ui_MyWindow:\n    def setupUi(self, w):\n        pass\n")

        monkeypatch.setattr(ui_utils, "compileUi", fake_compile)

        class FakeQMainWindow:
            pass

        monkeypatch.setattr(ui_utils, "QMainWindow", FakeQMainWindow, raising=False)

        form_class, base_class = ui_utils.loadUiType(str(ui_path))

        assert form_class.__name__ == "Ui_MyWindow"
        assert hasattr(form_class, "setupUi")
        assert base_class is FakeQMainWindow

    def test_resolves_widget_class_from_xml(self, tmp_path, monkeypatch):
        from core.utils import ui_utils

        ui_path = tmp_path / "Panel.ui"
        _write_ui_file(ui_path, form_class="Panel", widget_class="QWidget")

        monkeypatch.setattr(
            ui_utils,
            "compileUi",
            lambda src, out, indent=0: out.write("class Ui_Panel:\n    pass\n"),
        )

        class FakeQWidget:
            pass

        monkeypatch.setattr(ui_utils, "QWidget", FakeQWidget, raising=False)

        _, base_class = ui_utils.loadUiType(str(ui_path))
        assert base_class is FakeQWidget

    def test_raises_when_form_class_missing_from_compiled_output(
        self, tmp_path, monkeypatch
    ):
        from core.utils import ui_utils

        ui_path = tmp_path / "MyWindow.ui"
        _write_ui_file(ui_path)
        monkeypatch.setattr(
            ui_utils,
            "compileUi",
            lambda src, out, indent=0: out.write("class Ui_WrongName:\n    pass\n"),
        )
        monkeypatch.setattr(
            ui_utils, "QMainWindow", type("FakeQ", (), {}), raising=False
        )

        with pytest.raises(KeyError):
            ui_utils.loadUiType(str(ui_path))

    def test_raises_when_widget_class_not_in_module_namespace(
        self, tmp_path, monkeypatch
    ):
        from core.utils import ui_utils

        ui_path = tmp_path / "MyWindow.ui"
        _write_ui_file(ui_path, widget_class="NoSuchQClass")
        monkeypatch.setattr(
            ui_utils,
            "compileUi",
            lambda src, out, indent=0: out.write("class Ui_MyWindow:\n    pass\n"),
        )

        # eval('NoSuchQClass') in the module's globals → NameError.
        with pytest.raises(NameError):
            ui_utils.loadUiType(str(ui_path))

    def test_fails_when_compileui_is_unavailable(self, tmp_path):
        from core.utils import ui_utils

        ui_path = tmp_path / "x.ui"
        _write_ui_file(ui_path)
        # In CI compileUi is None; calling loadUiType without stubbing it
        # surfaces as TypeError. Pins the "PySide missing" failure mode.
        assert ui_utils.compileUi is None
        with pytest.raises(TypeError):
            ui_utils.loadUiType(str(ui_path))
