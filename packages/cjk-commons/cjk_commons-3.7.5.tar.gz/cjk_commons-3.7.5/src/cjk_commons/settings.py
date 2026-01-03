from pathlib import Path
from typing import Any

import yaml
import yodl
from appdirs import site_data_dir, user_data_dir
from loguru import logger


def get_attribute(
    kwargs: dict,
    kwargs_key: str,
    settings: dict | None = None,
    settings_key: str | None = None,
    default: Any = None,
    type_: type = str,
    allow_none: bool = False,
) -> Any:
    """Получить атрибут"""

    result = None
    type__ = type_

    if default is not None:
        type__ = type(default)

    if kwargs_key in kwargs:
        result = kwargs[kwargs_key]

        if not isinstance(result, type__) and default is not None:
            raise TypeError(f"{kwargs_key}" if kwargs_key else None)

    if settings is not None and settings_key is not None:
        if settings_key in settings:
            result = settings[settings_key]

            if not isinstance(result, type__) and default is not None:
                raise TypeError(f"{settings_key}" if settings_key else None)

    if result is None:
        result = default

    if result is None and not allow_none:
        raise AttributeError(f"{settings_key}")

    return result


def get_path_attribute(
    kwargs: dict,
    kwargs_key: str,
    settings: dict | None = None,
    settings_key: str | None = None,
    default_path: Path | None = None,
    is_dir: bool = True,
    check_if_exists: bool = True,
    create_dir: bool = True,
    create_parents: bool = True,
) -> Path:
    """Получить Path-атрибут"""

    result = None

    if kwargs_key in kwargs:
        result = kwargs[kwargs_key]

        if not isinstance(result, Path):
            raise TypeError(f"{kwargs_key}" if kwargs_key else None)

    elif settings is not None and settings_key is not None:
        if settings_key in settings:
            result_str = settings[settings_key]

            if not isinstance(result_str, str):
                raise TypeError(f"{settings_key}" if settings_key else None)

            result = Path(result_str)

            if not isinstance(result, Path):
                raise TypeError(f"{settings_key}" if settings_key else None)

    if result is None and isinstance(default_path, Path):
        result = default_path

    if result is None:
        raise AttributeError(f"{settings_key}")

    if result.exists():
        if not is_dir and result.is_dir():
            raise FileExistsError(
                f"{kwargs_key} Not A File" if kwargs_key else None, result
            )

        elif is_dir and result.is_file():
            raise NotADirectoryError(f"{kwargs_key}" if kwargs_key else None, result)
    else:
        if check_if_exists:
            raise FileExistsError(f"{kwargs_key}" if kwargs_key else None, result)

        if is_dir and create_dir:
            result.mkdir(parents=create_parents)

    return result


class SettingsError(Exception):
    """Settings Error"""


def get_settings(file_path=Path("settings.yaml"), **kwargs) -> dict:
    """Получить настройки"""

    if not file_path.is_file():
        app_name = get_attribute(kwargs, "app_name", allow_none=True)
        app_author = get_attribute(kwargs, "app_author", allow_none=True)
        file_path = Path(
            user_data_dir(app_name, app_author, roaming=True), file_path.name
        )

        if not file_path.is_file():
            file_path = Path(site_data_dir(app_name, app_author), file_path.name)
    if file_path.is_file():
        with file_path.open(encoding="utf-8") as settings_file:
            settings = yaml.load(settings_file, yodl.OrderedDictYAMLLoader)

        if settings is None:
            settings = {}
    else:
        settings = {}

    return settings


class OrderedDictMergeException(Exception):
    """Ordered Dict Merge Exception"""


def merge(a: dict, b: dict, path=None) -> dict:
    """Слить словари"""

    if path is None:
        path = []

    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass
            else:
                raise OrderedDictMergeException(
                    f'Conflict at \'{".".join(path + [str(key)])}\''
                )
        else:
            a[key] = b[key]

    return a


logger.disable(__name__)
