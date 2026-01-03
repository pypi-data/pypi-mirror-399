from pathlib import Path

import pytest

from cjk_commons.settings import OrderedDictMergeException, get_settings, merge
from cjk_commons.zip import extract_from_zip, write_to_zip


def test_get_settings_1():
    with pytest.raises(Exception) as exc:
        get_settings(app_name="bla", app_author="bla")

        assert e == "Settings file does not exist"


def test_get_settings_2():
    with pytest.raises(Exception) as exc:
        get_settings(Path("bla.yaml"))

        assert e == "Argument 'app_name' does not exist"


def test_get_settings_3():
    assert isinstance(get_settings(Path("tests/data/settings.yaml")), dict)


def test_merge_1():
    a = {"a": 1}
    b = {"a": 1}

    assert isinstance(merge(a, b), dict)


def test_merge_2():
    a = {"a": 1}
    b = {"a": 2}

    with pytest.raises(OrderedDictMergeException):
        merge(a, b)


def test_merge_3():
    a = {"b": {"a", 1}}
    b = {"b": {"b", 2}}
    c = merge(a, b)

    assert isinstance(c, dict)


def test_extract_from_zip(tmpdir):
    temp_dir_path = Path(tmpdir)
    extract_from_zip(Path("tests/data/test.zip"), temp_dir_path)

    assert Path(temp_dir_path, "test.txt").is_file()


def test_write_to_zip_1(tmpdir):
    temp_dir_path = Path(tmpdir)
    write_to_zip(Path(temp_dir_path, "test.zip"), Path("tests/data/test.txt"))

    assert Path(temp_dir_path, "test.zip").is_file()


def test_write_to_zip_2(tmpdir):
    temp_dir_path = Path(tmpdir)
    write_to_zip(Path(temp_dir_path, "test.zip"), Path("tests/data/test"))

    assert Path(temp_dir_path, "test.zip").is_file()
