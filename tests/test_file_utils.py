"""
Tests for gTools/core/utils/file_utils.py

These exercise the Utilities class with real files written to pytest's
tmp_path. They also document several existing defects so that any future
fix produces a visible test-failure signal:

  * `Utilities.checkOrMakeFileDirectory` is declared without `self`, so
    calling it on an instance raises TypeError.
  * `Utilities.getFiles` calls `cmds.error(...)` for invalid args, but
    `cmds` is never imported into this module, so the validation paths
    raise NameError instead of the intended Maya error.
"""

import os

import pytest

from core.utils.file_utils import Utilities


# ---------------------------------------------------------------------------
# makeTuple
# ---------------------------------------------------------------------------

class TestMakeTuple:
    def setup_method(self):
        self.u = Utilities()

    def test_scalars_become_a_tuple(self):
        assert set(self.u.makeTuple("a", "b", "c")) == {"a", "b", "c"}

    def test_lists_are_flattened(self):
        assert set(self.u.makeTuple(["a", "b"], "c")) == {"a", "b", "c"}

    def test_tuples_are_flattened(self):
        assert set(self.u.makeTuple(("a", "b"), "c")) == {"a", "b", "c"}

    def test_mixed_inputs_are_flattened(self):
        result = self.u.makeTuple("a", ["b", "c"], ("d",))
        assert set(result) == {"a", "b", "c", "d"}

    def test_result_is_a_tuple(self):
        assert isinstance(self.u.makeTuple("a"), tuple)

    def test_duplicates_are_dropped(self):
        # Current behaviour: makeTuple builds a set internally, so duplicates
        # are silently removed. Pinning this so a future change is intentional.
        assert len(self.u.makeTuple("a", "a", ["a"])) == 1

    def test_empty_input_returns_empty_tuple(self):
        assert self.u.makeTuple() == ()


# ---------------------------------------------------------------------------
# getFiles
# ---------------------------------------------------------------------------

@pytest.fixture
def populated_dir(tmp_path):
    (tmp_path / "rig_v01.ma").write_text("")
    (tmp_path / "rig_v02.mb").write_text("")
    (tmp_path / "anim_v01.ma").write_text("")
    (tmp_path / "anim_v01.fbx").write_text("")
    (tmp_path / "notes.txt").write_text("")
    return tmp_path


class TestGetFiles:
    def setup_method(self):
        self.u = Utilities()

    def test_returns_all_files_when_no_filter(self, populated_dir):
        result = self.u.getFiles(str(populated_dir))
        assert len(result) == 5
        assert all(os.path.isabs(p) for p in result)

    def test_filters_by_single_extension(self, populated_dir):
        result = self.u.getFiles(str(populated_dir), ext=".fbx")
        assert [os.path.basename(p) for p in result] == ["anim_v01.fbx"]

    def test_filters_by_extension_list(self, populated_dir):
        result = self.u.getFiles(str(populated_dir), ext=[".ma", ".mb"])
        assert sorted(os.path.basename(p) for p in result) == [
            "anim_v01.ma",
            "rig_v01.ma",
            "rig_v02.mb",
        ]

    def test_filters_by_prefix(self, populated_dir):
        result = self.u.getFiles(str(populated_dir), prefix="rig_")
        assert sorted(os.path.basename(p) for p in result) == [
            "rig_v01.ma",
            "rig_v02.mb",
        ]

    def test_filters_by_suffix(self, populated_dir):
        result = self.u.getFiles(str(populated_dir), suffix="_v01")
        assert sorted(os.path.basename(p) for p in result) == [
            "anim_v01.fbx",
            "anim_v01.ma",
            "rig_v01.ma",
        ]

    def test_accepts_list_of_directories(self, tmp_path):
        d1 = tmp_path / "a"
        d2 = tmp_path / "b"
        d1.mkdir()
        d2.mkdir()
        (d1 / "x.ma").write_text("")
        (d2 / "y.ma").write_text("")
        result = self.u.getFiles([str(d1), str(d2)], ext=".ma")
        assert sorted(os.path.basename(p) for p in result) == ["x.ma", "y.ma"]

    def test_empty_directory_returns_empty_list(self, tmp_path):
        assert self.u.getFiles(str(tmp_path)) == []

    def test_nonexistent_directory_raises(self, tmp_path):
        missing = str(tmp_path / "does_not_exist")
        with pytest.raises(FileNotFoundError):
            self.u.getFiles(missing)

    def test_invalid_directory_type_raises_typeerror(self):
        with pytest.raises(TypeError, match="directory"):
            self.u.getFiles(12345)

    def test_invalid_ext_type_raises_typeerror(self, tmp_path):
        with pytest.raises(TypeError, match="ext"):
            self.u.getFiles(str(tmp_path), ext=12345)

    def test_invalid_prefix_type_raises_typeerror(self, tmp_path):
        with pytest.raises(TypeError, match="prefix"):
            self.u.getFiles(str(tmp_path), prefix=12345)

    def test_invalid_suffix_type_raises_typeerror(self, tmp_path):
        with pytest.raises(TypeError, match="suffix"):
            self.u.getFiles(str(tmp_path), suffix=12345)


# ---------------------------------------------------------------------------
# getMayaFiles / getFbxFiles
# ---------------------------------------------------------------------------

class TestGetMayaFiles:
    def test_returns_only_ma_and_mb(self, populated_dir):
        u = Utilities()
        result = u.getMayaFiles(str(populated_dir))
        assert sorted(os.path.basename(p) for p in result) == [
            "anim_v01.ma",
            "rig_v01.ma",
            "rig_v02.mb",
        ]


class TestGetFbxFiles:
    def test_returns_only_fbx(self, populated_dir):
        u = Utilities()
        result = u.getFbxFiles(str(populated_dir))
        assert [os.path.basename(p) for p in result] == ["anim_v01.fbx"]


# ---------------------------------------------------------------------------
# checkOrMakeFileDirectory
# ---------------------------------------------------------------------------

class TestCheckOrMakeFileDirectory:
    def setup_method(self):
        self.u = Utilities()

    def test_creates_missing_parent_directory(self, tmp_path):
        target = tmp_path / "new" / "deep" / "file.txt"
        result = self.u.checkOrMakeFileDirectory(str(target))
        assert os.path.isdir(str(tmp_path / "new" / "deep"))
        assert result == str(tmp_path / "new" / "deep")

    def test_returns_existing_parent_without_error(self, tmp_path):
        existing = tmp_path / "already_here"
        existing.mkdir()
        target = existing / "file.txt"
        result = self.u.checkOrMakeFileDirectory(str(target))
        assert result == str(existing)

