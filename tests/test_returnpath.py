"""
Tests for gTools/setup/returnpath.py

`getpath()` is tiny but load-bearing: userSetup.py uses its return value as
the path it appends to sys.path. If this regresses, the entire bootloader
breaks.
"""

import os

import returnpath


def test_getpath_returns_grandparent_of_returnpath_file():
    expected = os.path.dirname(os.path.dirname(os.path.abspath(returnpath.__file__)))
    assert os.path.abspath(returnpath.getpath()) == expected


def test_getpath_points_at_gtools_root():
    # By convention the grandparent dir is the gTools/ module root, which
    # should contain the gTools.mod file.
    root = returnpath.getpath()
    assert os.path.isfile(os.path.join(root, "gTools.mod"))


def test_getpath_is_stable_across_cwd_changes(tmp_path, monkeypatch):
    before = returnpath.getpath()
    monkeypatch.chdir(tmp_path)
    after = returnpath.getpath()
    assert before == after
