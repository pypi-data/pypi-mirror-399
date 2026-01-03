import re
from pathlib import Path

import pytest

from commons_1c.platform_ import get_last_1c_exe_file_fullpath
from commons_1c.version import (
    get_version_as_number,
    get_version_as_number_2,
    get_version_as_parts,
)


def test_get_version_as_number():
    assert get_version_as_number("") == 0
    assert get_version_as_number("foo") == 0
    assert get_version_as_number("1") == 1000000000000
    assert get_version_as_number("1.1") == 1000100000000
    assert get_version_as_number("1.1.1") == 1000100010000
    assert get_version_as_number("1.1.1.1") == 1000100010001


def test_get_version_as_parts():
    assert get_version_as_parts("") == []
    assert get_version_as_parts("foo") == []
    assert get_version_as_parts("1") == ["1"]
    assert get_version_as_parts("1.1") == ["1", "1"]
    assert get_version_as_parts("1.1.1") == ["1", "1", "1"]
    assert get_version_as_parts("1.1.1.1") == ["1", "1", "1", "1"]


def test_get_version_as_number_2():
    assert get_version_as_number_2("") == 0
    assert get_version_as_number_2("foo") == 0

    assert get_version_as_number_2("1") == 1
    assert get_version_as_number_2("1", ranks=3) == 100000000
    assert get_version_as_number_2("1", ranks=4) == 1000000000000

    assert get_version_as_number_2("1.1") == 10001
    assert get_version_as_number_2("1.1", ranks=3) == 100010000
    assert get_version_as_number_2("1.1", ranks=4) == 1000100000000

    assert get_version_as_number_2("1.1.1") == 100010001
    assert get_version_as_number_2("1.1.1", ranks=3) == 100010001
    assert get_version_as_number_2("1.1.1", ranks=4) == 1000100010000

    assert get_version_as_number_2("1.1.1.1") == 1000100010001

    with pytest.raises(AttributeError, match="Ranks is Lesser Than Parts Number"):
        assert get_version_as_number_2("1.1.1.1", ranks=3) == 1000100010001

    assert get_version_as_number_2("1.1.1.1", ranks=4) == 1000100010001


def test_get_last_1c_exe_file_path_1():
    file_path = get_last_1c_exe_file_fullpath()

    assert isinstance(file_path, Path)
    assert re.match(
        r"(?i)c:\\Program Files\\1cv8\\\d+\.\d+\.\d+\.\d+\\bin\\1cv8\.exe",
        str(file_path),
    )


def test_get_last_1c_exe_file_path_2() -> None:
    with pytest.raises(Exception) as exc:
        get_last_1c_exe_file_fullpath(config_file="bla.cfg")

        assert re.match(r"1CEStart.cfg file does not exist", str(e))
