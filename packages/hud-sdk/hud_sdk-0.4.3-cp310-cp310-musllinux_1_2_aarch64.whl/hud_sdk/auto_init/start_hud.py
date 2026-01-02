import importlib
import os
import sys
from types import ModuleType
from typing import Optional

from hud_sdk import init_session, register
from hud_sdk.logging import user_logger
from hud_sdk.user_logs import UsersLogs
from hud_sdk.user_options import RegisterConfig


def get_user_config(config_path: Optional[str]) -> RegisterConfig:
    default_config = RegisterConfig()

    if config_path is None:
        return default_config

    if not os.path.exists(config_path):
        user_logger.log(*UsersLogs.CONFIG_PATH_NOT_FOUND(config_path, os.getcwd()))
        return default_config

    if not config_path.endswith(".py"):
        user_logger.log(*UsersLogs.CONFIG_PATH_NOT_A_PY_FILE(config_path))
        return default_config

    user_config_module = None
    try:
        user_config_module = import_from_path("_hud_sdk_user_config", config_path)
    except Exception as e:
        user_logger.log(*UsersLogs.FAILED_LOADING_CONFIG(config_path, e))
        return default_config

    user_config = None
    try:
        user_config = user_config_module.config
    except AttributeError:
        user_logger.log(*UsersLogs.CONFIG_FILE_DONT_EXPORT_CONFIG)
        return default_config

    if not isinstance(user_config, RegisterConfig):
        user_logger.log(*UsersLogs.CONFIG_VAR_IS_NOT_HUD_CONFIG)
        return default_config

    return user_config


def import_from_path(module_name: str, file_path: str) -> ModuleType:
    if module_name in sys.modules:
        return sys.modules[module_name]

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        raise ImportError(f"Failed to create spec for {file_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = (
        module  # Adding to cache so if the user have some logic which effect global state in the config file then it won't run twice.
    )
    if spec.loader is None:
        raise ImportError(f"Failed to create loader for {file_path}")

    spec.loader.exec_module(module)
    return module


def is_valid_string(s: Optional[str]) -> bool:
    return s is not None and s != ""


def start_hud() -> None:
    try:
        config_path = os.environ.get("HUD_CONFIG_PATH")
        key = os.environ.get("HUD_KEY")
        service = os.environ.get("HUD_SERVICE")

        register(get_user_config(config_path))

        if is_valid_string(key) or is_valid_string(service):
            # init session later check if the key and service are valid, we just use them as trigger for running init_session
            init_session(key, service)
    except Exception:
        pass
