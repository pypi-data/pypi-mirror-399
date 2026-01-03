from pathlib import Path

from appdirs import site_data_dir
from cjk_commons.settings import get_path_attribute
from loguru import logger

from commons_1c.version import get_version_as_number

logger.disable(__name__)


def get_last_exe_file_fullpath(file_name: str, **kwargs) -> Path | None:
    """Получить путь к exe-файлу из последней установленной платформы 1С

    Args:
        - file_name (str) -- Имя файла

    Raises:
        - FileExistsError -- Возникает, если файл не существует

    Returns:
        - Path -- Путь к exe-файлу
    """

    result = None

    config_file_path = get_path_attribute(
        kwargs,
        "config_file_path",
        default_path=Path(site_data_dir("1CEStart", "1C"), "1CEStart.cfg"),
        is_dir=False,
        check_if_exists=False,
    )

    if config_file_path.is_file():
        installed_location_paths = []

        with config_file_path.open(encoding="utf-16") as config_file:
            for line in config_file.readlines():
                key_and_value = line.split("=")
                if key_and_value[0] == "InstalledLocation":
                    value = "=".join(key_and_value[1:])
                    installed_location_paths.append(Path(value.rstrip("\n")))

        platform_versions = []

        for installed_location_path in installed_location_paths:
            if installed_location_path.is_dir():
                # todo
                for version_dir_path in installed_location_path.rglob("*"):
                    version_as_number = get_version_as_number(version_dir_path.name)
                    if version_as_number:
                        exe_file_path = Path(version_dir_path, "bin", file_name)
                        if exe_file_path.is_file():
                            platform_versions.append((version_as_number, exe_file_path))

        platform_versions_reversed = sorted(
            platform_versions, key=lambda x: x[0], reverse=True
        )

        if platform_versions_reversed:
            result = platform_versions_reversed[0][1]
    else:
        raise FileExistsError("1CEStart.cfg file does not exist")

    return result


def get_last_1c_exe_file_fullpath(**kwargs) -> Path | None:
    return get_last_exe_file_fullpath("1cv8.exe", **kwargs)


def get_last_ibcmd_exe_file_fullpath(**kwargs) -> Path | None:
    return get_last_exe_file_fullpath("ibcmd.exe", **kwargs)


def get_last_rac_exe_file_fullpath(**kwargs) -> Path | None:
    return get_last_exe_file_fullpath("rac.exe", **kwargs)
