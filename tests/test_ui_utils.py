"""
Tests for gTools/core/utils/ui_utils.py

gTools assumes PySide is always present because vanilla Maya (the core
dependency) bundles it, so ui_utils.py imports the PySide2 stack and builds
MAYAWINDOW unconditionally at import time. The PySide2/pyside2uic/shiboken2
and MQtUtil stand-ins live in conftest.py; these tests run against those.

Coverage focus:
  * Module imports cleanly on Python 3 — pins the cStringIO/long/exec-X-in-Y
    syntax fixes so a regression to Py2 idioms fails fast.
  * MAYAWINDOW is built at import time from wrapInstance(MQtUtil...).
  * loadUiType parses .ui XML, exec()s the compileUi output, and resolves
    the form class + base widget class from the module namespace.
"""

import pytest

from core.utils import ui_utils


# ---------------------------------------------------------------------------
# Module-level
# ---------------------------------------------------------------------------

def test_module_imports_on_py3():
    # If any Py2-only idiom regresses (`exec X in Y`, `long(...)`, cStringIO)
    # this import itself raises a SyntaxError or NameError.
    import core.utils.ui_utils  # noqa: F401


def test_mayawindow_is_built_from_wrapinstance():
    # conftest's wrapInstance stub returns a ("WRAPPED", ptr, base) tuple;
    # MAYAWINDOW must be the result of wrapping the MQtUtil pointer, not None.
    assert ui_utils.MAYAWINDOW is not None
    assert ui_utils.MAYAWINDOW[0] == "WRAPPED"


def test_pyside_bindings_are_imported():
    assert callable(ui_utils.compileUi)
    assert callable(ui_utils.wrapInstance)


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
    def test_returns_form_class_and_base_class(self, tmp_path):
        # Uses the conftest compileUi stub (emits Ui_<class>) and the
        # conftest QMainWindow resolved from the module namespace.
        ui_path = tmp_path / "MyWindow.ui"
        _write_ui_file(ui_path, form_class="MyWindow", widget_class="QMainWindow")

        form_class, base_class = ui_utils.loadUiType(str(ui_path))

        assert form_class.__name__ == "Ui_MyWindow"
        assert hasattr(form_class, "setupUi")
        assert base_class is ui_utils.QMainWindow

    def test_resolves_widget_class_from_xml(self, tmp_path):
        ui_path = tmp_path / "Panel.ui"
        _write_ui_file(ui_path, form_class="Panel", widget_class="QWidget")

        _, base_class = ui_utils.loadUiType(str(ui_path))
        assert base_class is ui_utils.QWidget

    def test_raises_when_form_class_missing_from_compiled_output(
        self, tmp_path, monkeypatch
    ):
        ui_path = tmp_path / "MyWindow.ui"
        _write_ui_file(ui_path)
        # compileUi emits a class whose name doesn't match the .ui <class>,
        # so the frame['Ui_MyWindow'] lookup raises KeyError.
        monkeypatch.setattr(
            ui_utils,
            "compileUi",
            lambda src, out, indent=0: out.write("class Ui_WrongName:\n    pass\n"),
        )
        with pytest.raises(KeyError):
            ui_utils.loadUiType(str(ui_path))

    def test_raises_when_widget_class_not_in_module_namespace(self, tmp_path):
        ui_path = tmp_path / "MyWindow.ui"
        _write_ui_file(ui_path, widget_class="NoSuchQClass")
        # eval('NoSuchQClass') against the module globals → NameError.
        with pytest.raises(NameError):
            ui_utils.loadUiType(str(ui_path))
