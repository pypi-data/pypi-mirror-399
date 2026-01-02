import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union

from .logging import user_logger
from .user_logs import UsersLogs


# This is actually the HookConfig but I didn't want to extern the term "Hook" as for the user this is the only config
@dataclass
class RegisterConfig:
    """Class for configuring Hud instrumentation"""

    include_modules: List[str] = field(default_factory=list)
    max_mapped_functions: int = 50 * 1000
    min_pod_memory_mb: int = 250
    max_file_size_bytes: int = 2 * 1024 * 1024
    init_timeout: int = 30
    verbose: bool = False
    enable_user_failure: bool = True


_register_config = None  # type: Optional[RegisterConfig]


def set_register_config(register_config: RegisterConfig) -> None:
    global _register_config
    _register_config = register_config


def get_register_config() -> Optional[RegisterConfig]:
    return _register_config


def is_user_failure_enabled() -> bool:
    if _register_config is None:
        return True

    return _register_config.enable_user_failure


class InitConfig:
    def __init__(
        self,
        key: Optional[str],
        service: Optional[str],
        tags: Optional[Union[Dict[str, str], str]],
        is_main_process: bool,
    ):
        key = self._get_key(key, is_main_process)
        service = self._get_service(service, is_main_process)
        tags = self._get_tags(tags, is_main_process)

        if key is None or service is None or tags is None:
            raise Exception("User options are not valid")

        self.key = key
        self.service = service
        self.tags = tags

    def _get_key(self, key: Optional[str], is_main_process: bool) -> Optional[str]:
        key = key or os.environ.get("HUD_KEY", None)
        if not key:
            if is_main_process:
                user_logger.log(*UsersLogs.HUD_KEY_NOT_SET)
            return None
        if not (isinstance(key, str) and key != ""):
            if is_main_process:
                user_logger.log(*UsersLogs.HUD_KEY_INVALID)
            return None
        return key

    def _get_service(
        self, service: Optional[str], is_main_process: bool
    ) -> Optional[str]:
        service = service or os.environ.get("HUD_SERVICE", None)
        if not service:
            if is_main_process:
                user_logger.log(*UsersLogs.HUD_SERVICE_NOT_SET)
            return None
        if not (isinstance(service, str) and service != ""):
            if is_main_process:
                user_logger.log(*UsersLogs.HUD_SERVICE_INVALID)
            return None
        return service

    def _get_tags(
        self, tags: Optional[Union[Dict[str, str], str]], is_main_process: bool
    ) -> Optional[Dict[str, str]]:
        try:
            tags = tags or os.environ.get("HUD_TAGS", "{}")
            if isinstance(tags, str):
                tags = json.loads(tags)
            if not (
                isinstance(tags, dict)
                and all(
                    isinstance(k, str) and isinstance(v, str) for k, v in tags.items()
                )
            ):
                if is_main_process:
                    user_logger.log(*UsersLogs.HUD_TAGS_INVALID_TYPE)
                return {}

            if any("." in key for key in tags.keys()):
                if is_main_process:
                    user_logger.log(*UsersLogs.HUD_TAGS_WITH_DOTS)
                tags = {key.replace(".", "_"): value for key, value in tags.items()}
            return tags
        except Exception:
            if is_main_process:
                user_logger.log(*UsersLogs.HUD_TAGS_INVALID_JSON)
        return {}


_user_options = None  # type: Optional[InitConfig]


def init_user_options(
    key: Optional[str],
    service: Optional[str],
    tags: Optional[Union[Dict[str, str], str]],
    is_main_process: bool,
) -> InitConfig:
    global _user_options
    if _user_options:
        return _user_options

    _user_options = InitConfig(key, service, tags, is_main_process)
    return _user_options


def get_user_options() -> InitConfig:
    if not _user_options:
        raise Exception("User options are not set")
    return _user_options
