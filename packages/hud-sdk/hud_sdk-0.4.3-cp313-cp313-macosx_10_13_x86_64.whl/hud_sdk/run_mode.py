import contextlib
import os
import sys
import sysconfig
from dataclasses import dataclass
from enum import IntEnum
from typing import Optional, Tuple, Union

from ._internal import worker_queue
from .logging import internal_logger, send_logs_handler
from .native import (
    get_and_swap_aggregations,
    get_hud_running_mode,
    set_hud_running_mode,
)
from .user_logs import UsersLogs
from .user_options import RegisterConfig
from .utils import dump_logs_sync
from .workload_metadata.kubernetes_workload_metadata import get_memory_limit

should_check_env_var = False


# HudRunningMode enum is also declared in native.h
# Any changes to HudRunningMode enum should be reflected in native.h as well.
class HudRunningMode(IntEnum):
    DISABLED = 0
    ENABLED = 1


@dataclass
class ShouldRunHudResult:
    should_run: bool
    reason: Optional[Tuple[int, str]] = None


def set_should_check_env_var(new_value: bool) -> None:
    global should_check_env_var
    should_check_env_var = new_value


def get_hud_enable() -> Union[str, None]:
    return os.environ.get("HUD_ENABLE", None)


def valid_hud_enable(hud_env_var: Optional[str]) -> bool:
    return isinstance(hud_env_var, str) and (
        hud_env_var.lower() == "true" or hud_env_var == "1"
    )


def is_hud_disabled_by_var() -> bool:
    hud_env_var = get_hud_enable()
    return hud_env_var == "false"


def is_hud_enabled_by_var() -> bool:
    return valid_hud_enable(get_hud_enable())


def is_gil_enabled() -> bool:
    try:
        return sys._is_gil_enabled()  # type: ignore
    except Exception:
        return True


def is_jit_enabled() -> bool:
    try:
        return "_Py_JIT" in sysconfig.get_config_var("PY_CORE_CFLAGS")
    except Exception:
        return False


def is_enough_ram(user_config: RegisterConfig) -> bool:
    try:
        memory_limit = get_memory_limit()
        if memory_limit is None or memory_limit.pod_memory_limit_bytes is None:
            return True

        return (
            memory_limit.pod_memory_limit_bytes
            >= user_config.min_pod_memory_mb * 1024 * 1024
        )
    except Exception:
        return True


def should_run_hud(user_config: RegisterConfig) -> ShouldRunHudResult:
    if is_hud_disabled_by_var():
        return ShouldRunHudResult(
            should_run=False, reason=UsersLogs.HUD_DISABLED_BY_VAR
        )

    if should_check_env_var and not is_hud_enabled_by_var():
        return ShouldRunHudResult(should_run=False)

    if get_hud_running_mode() == HudRunningMode.DISABLED:
        return ShouldRunHudResult(should_run=False)

    if not is_gil_enabled():
        internal_logger.info("GIL is not enabled")
        return ShouldRunHudResult(should_run=False, reason=UsersLogs.GIL_NOT_ENABLED)

    if is_jit_enabled():
        internal_logger.info("JIT is enabled")
        return ShouldRunHudResult(should_run=False, reason=UsersLogs.JIT_ENABLED)

    if not is_enough_ram(user_config):
        internal_logger.info("Not enough memory")
        return ShouldRunHudResult(
            should_run=False,
            reason=UsersLogs.POD_MEMORY_TOO_LOW(user_config.min_pod_memory_mb),
        )

    return ShouldRunHudResult(should_run=True)


def disable_hud(
    should_dump_logs: bool,
    should_clear: bool = True,
    session_id: Optional[str] = None,
) -> None:
    internal_logger.info(
        "Disabling HUD"
    )  # It will print to the console if HUD_DEBUG is set
    set_hud_running_mode(HudRunningMode.DISABLED)

    if should_dump_logs:
        with contextlib.suppress(Exception):
            dump_logs_sync(session_id)

    if should_clear:
        clear_hud()


def clear_hud() -> None:
    worker_queue.clear()

    get_and_swap_aggregations().clear()
    # we have two dictionaries swapping
    get_and_swap_aggregations().clear()

    send_logs_handler.get_and_clear_logs()


def enable_hud() -> None:
    set_hud_running_mode(HudRunningMode.ENABLED)
