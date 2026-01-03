import re
from typing import List

from loguru import logger

logger.disable(__name__)


pattern_version = re.compile(
    r"\D*(?P<version>(?:(\d+)|)(?:\.(\d+)|)(?:\.(\d+)|)(?:\.(\d+)|))\D*"
)


def get_version_as_number(version: str, m: int = 10000) -> int:
    result = 0

    match = pattern_version.match(version)
    if match is not None:
        a = match.group(2)
        a = "0" if a is None else a

        b = match.group(3)
        b = "0" if b is None else b

        c = match.group(4)
        c = "0" if c is None else c

        d = match.group(5)
        d = "0" if d is None else d

        result = int(a) * m**3 + int(b) * m**2 + int(c) * m + int(d)

    return result


def get_version_as_parts(version: str) -> List[str]:
    result = []
    match = pattern_version.match(version)

    if match is not None:
        a = match.group(2)

        if a is not None:
            result.append(a)

        b = match.group(3)

        if b is not None:
            result.append(b)

        c = match.group(4)

        if c is not None:
            result.append(c)

        d = match.group(5)

        if d is not None:
            result.append(d)

    return result


def get_version_as_number_2(
    version: str, m: int = 10000, ranks: int | None = None
) -> int:
    result = 0

    try:
        parts = [int(x) for x in version.split(".")]

        if ranks is not None:
            # Нужно дополнить нулями  # todo Улучшить комментарий
            if len(parts) < ranks:
                for i in range(ranks - len(parts)):
                    parts.append(0)
            elif len(parts) > ranks:
                raise AttributeError("Ranks is Lesser Than Parts Number")  # todo

        parts.reverse()

        result = sum(x * (m**i) for i, x in enumerate(parts))
    except ValueError:
        pass

    return result
