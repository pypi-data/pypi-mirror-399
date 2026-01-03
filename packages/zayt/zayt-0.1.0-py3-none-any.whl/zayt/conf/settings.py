"""
The processing of settings occur as follows:

1. Get main settings values
2. Recursively merge values with settings from profiles, in the order of declaration
"""

import copy
import importlib.util
import os
from collections.abc import Mapping
from copy import deepcopy
from pathlib import Path
from typing import Any

from zayt.conf.defaults import default_settings

__all__ = (
    "Settings",
    "SettingsError",
    "get_settings",
    "get_settings_meta",
    "get_settings_for_profile",
)

SETTINGS_DIR_ENV = "ZAYT_SETTINGS_DIR"
SETTINGS_FILE_ENV = "ZAYT_SETTINGS_FILE"

DEFAULT_SETTINGS_DIR = str(Path("configuration"))
DEFAULT_SETTINGS_FILE = "settings.py"
SETTINGS_KEY = "settings"

ZAYT_PROFILE_ENV = "ZAYT_PROFILE"


class Settings(Mapping[str, Any]):
    def __init__(self, data: dict):
        self._original_data = copy.deepcopy(data)
        self.__data = data

        for key, value in data.items():
            if isinstance(value, dict):
                self.__data[key] = Settings(value)

    def __getattr__(self, item: str):
        try:
            return self.__data[item]
        except KeyError:
            # pylint: disable=raise-missing-from
            raise AttributeError(item)

    def __len__(self) -> int:
        return len(self.__data)

    def __iter__(self):
        return iter(self.__data)

    def __contains__(self, key: str):
        return key in self.__data

    def __getitem__(self, key: str):
        return self.__data[key]

    def __copy__(self):
        return Settings(copy.copy(self._original_data))

    def __deepcopy__(self, memodict):
        data = copy.deepcopy(self._original_data, memodict)
        return Settings(data)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Settings):
            return self._original_data == other._original_data
        if isinstance(other, Mapping):
            return self._original_data == other

        return False

    def __str__(self):
        return str(self.__data)

    def __repr__(self):
        return repr(self.__data)


class SettingsError(Exception):
    def __init__(self, path: Path):
        super().__init__(f"cannot load settings from {path}")
        self.path = path


def get_settings() -> Settings:
    """Get settings from files and environment"""
    return get_settings_meta()[0]


def get_settings_meta() -> tuple[Settings, list[tuple[Path, str | None, bool]]]:
    """Get settings from files and environment with metadata

    Metadata contains the files used to load settings from and if the file exists or not
    """
    # get default settings
    settings = deepcopy(default_settings)
    settings_files = []

    # merge with main settings file (settings.yaml)
    profile_settings, profile_settings_file = get_settings_for_profile()
    _merge_recursive(settings, profile_settings)
    settings_files.append(profile_settings_file)

    # merge with profile settings files (settings_$ZAYT_PROFILE.yaml)
    if active_profile_list := os.getenv(ZAYT_PROFILE_ENV):
        for active_profile in active_profile_list.split(","):
            active_profile = active_profile.strip()
            profile_settings, profile_settings_file = get_settings_for_profile(
                active_profile
            )
            _merge_recursive(settings, profile_settings)
            settings_files.append(profile_settings_file)

    return Settings(settings), settings_files


def get_settings_for_profile(
    profile: str = None,
) -> tuple[dict, tuple[Path, str | None, bool]]:
    settings_file = os.getenv(SETTINGS_FILE_ENV, DEFAULT_SETTINGS_FILE)
    settings_dir_path = Path(os.getenv(SETTINGS_DIR_ENV, DEFAULT_SETTINGS_DIR))
    settings_file_path = settings_dir_path / settings_file

    if profile:
        settings_file_path = settings_file_path.with_stem(
            f"{settings_file_path.stem}_{profile}"
        )

    settings_file_path = settings_file_path.absolute()

    try:
        spec = importlib.util.spec_from_file_location(
            "settings" if not profile else f"settings_{profile}",
            settings_file_path,
        )
        settings_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(settings_module)

        result = getattr(settings_module, SETTINGS_KEY, {})
        if not isinstance(result, dict):
            raise TypeError("invalid settings object type")
        return result, (settings_file_path, profile, True)
    except FileNotFoundError:
        return {}, (settings_file_path, profile, False)
    except TypeError as err:
        raise SettingsError(settings_file_path) from err
    except Exception as err:
        raise SettingsError(settings_file_path) from err


def _merge_recursive(destination: dict, source: dict):
    for key in source:
        if key in destination and all(
            isinstance(arg[key], dict) for arg in (destination, source)
        ):
            _merge_recursive(destination[key], source[key])
        else:
            destination[key] = deepcopy(source[key])
