import itertools
import platform
import time
import types
from typing import Any, Dict, Iterable, List, Optional

from ...collectors.performance import PerformanceMonitor
from ...config import config
from ...investigation_manager import (
    safe_get_cpu_usage,
)
from ...logging import user_logger
from ...native import (
    RawInvestigation,
    get_investigation,
    set_investigation,
)
from ...schemas.investigation import (
    ErrorRecord,
    InvestigationExceptionInfo,
    MachineMetrics,
    SystemInfo,
)
from ...user_logs import UsersLogs
from ...user_options import is_user_failure_enabled
from ..limited_logger import limited_logger, user_limited_logger

total_investigations: int = 0
investigation_dedup: Dict[str, Dict[str, int]] = (
    dict()
)  # investigation_dedup[flow_id][dedup_key] = count


def open_investigation() -> Optional[RawInvestigation]:
    if not config.enable_investigation:
        return None

    raw_investigation = RawInvestigation(round(time.time() * 1000))
    set_investigation(raw_investigation)
    return raw_investigation


def get_total_investigations() -> int:
    return total_investigations


def increase_total_investigations() -> None:
    global total_investigations
    # That's not thread safe, but it's ok since this number is not really a hard limit. One off is not a big deal.
    total_investigations += 1


def get_investigation_dedup() -> Dict[str, Dict[str, int]]:
    return investigation_dedup


def reset_max_investigations() -> None:
    global total_investigations
    total_investigations = 0


def reset_investigation_dedup() -> None:
    global investigation_dedup
    investigation_dedup = dict()


def minimize_object_with_defaults(
    obj: Any,
) -> Any:
    return minimize_object(
        obj,
        config.investigation_max_object_depth,
        config.investigation_max_string_length,
        config.investigation_max_array_length,
        config.investigation_max_dict_length,
    )


def minimize_object(
    obj: Any,
    max_depth: int,
    max_string_length: int,
    max_array_length: int,
    max_dict_length: int,
) -> Any:
    try:
        if obj is None or isinstance(obj, (int, float, bool, complex)):
            return obj

        if isinstance(obj, str):
            return obj[:max_string_length]

        if max_depth < 0:
            return None

        if isinstance(obj, dict):
            return {
                minimize_object(
                    key,
                    max_depth - 1,
                    max_string_length,
                    max_array_length,
                    max_dict_length,
                ): minimize_object(
                    value,
                    max_depth - 1,
                    max_string_length,
                    max_array_length,
                    max_dict_length,
                )
                for key, value in itertools.islice(obj.items(), max_dict_length)
            }

        if isinstance(obj, types.GeneratorType):
            return None

        # Both dict and generator are iterable which we don't want to slice with `itertools.islice` since:
        # 1. Itertating through dict will return just the keys and not the values
        # 2. Iterating through generator will change it internal state
        if isinstance(obj, Iterable):
            return [
                minimize_object(
                    item,
                    max_depth - 1,
                    max_string_length,
                    max_array_length,
                    max_dict_length,
                )
                for item in itertools.islice(obj, max_array_length)
            ]

    except Exception:
        pass

    # Drop anythig else including functions, Classes, etc
    return None


def minimize_exception_info_in_place(
    exception_info: InvestigationExceptionInfo,
) -> InvestigationExceptionInfo:
    exception_info.message = minimize_object_with_defaults(exception_info.message)
    return exception_info


def get_error_records_from_investigation(
    raw_investigation: RawInvestigation,
) -> List[ErrorRecord]:
    error_records = {}

    for exception in raw_investigation.exceptions.values():
        error_type = exception.name
        function_id = None
        if exception.execution_flow and len(exception.execution_flow) > 0:
            function_id = exception.execution_flow[0][
                0
            ]  # first function in the execution flow

        if function_id:
            key = f"{error_type}-{function_id}"
            if key not in error_records:
                error_records[key] = ErrorRecord(error_type, function_id)

    return list(error_records.values())


def get_investigation_deduping_key_for_errors(
    error_records: List[ErrorRecord],
    status: str,
) -> str:
    parts = [f"{er.error_type}-{er.function_id}" for er in error_records]
    parts.append(status)

    return "|".join(parts)


def get_pod_name() -> Optional[str]:
    try:
        return platform.node()
    except Exception:
        return None


def get_node_name() -> Optional[str]:
    try:
        with open("/etc/machine-id", "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return None


def get_system_info() -> SystemInfo:
    return SystemInfo(
        pod_name=get_pod_name(),
        node_name=get_node_name(),
    )


def get_machine_metrics() -> Optional[MachineMetrics]:
    try:
        return MachineMetrics(
            cpu=safe_get_cpu_usage(),
            memory=PerformanceMonitor.get_memory_usage(),
            threads_count=PerformanceMonitor.get_thread_count(),
        )
    except Exception:
        limited_logger.log("Error getting machine metrics", exc_info=True)
        return None


def set_user_failure(error: str, **kwargs: Any) -> None:
    if not config.enable_investigation:
        return

    if not is_user_failure_enabled():
        limited_logger.log("User failure is not enabled")
        user_limited_logger.log(
            UsersLogs.SET_ERROR_CALLED_WITHOUT_ENABLE_USER_FAILURE[1]
        )
        return

    if not isinstance(error, str):
        # The user can pass to this function any object and we don't really protected by the type
        limited_logger.log("User defined error is not a string")
        user_limited_logger.log(UsersLogs.SET_ERROR_IS_NOT_A_STRING[1])
        return

    raw_investigation = get_investigation()

    if raw_investigation is None:
        limited_logger.log("No investigation when setting user defined error")
        user_limited_logger.log(UsersLogs.SET_ERROR_CALLED_NOT_IN_FLOW[1])
        return

    raw_investigation.user_defined_error = error
    if kwargs:
        set_user_context(**kwargs)


_did_logged_from_validate_value = False


def _validate_value(
    value: Any,
    key: str,
    is_list_item: bool = False,
) -> bool:
    global _did_logged_from_validate_value
    key_string = f"item in list '{key}'" if is_list_item else f"Key: '{key}'"

    if isinstance(value, str) and len(value) > config.max_context_str_length:
        limited_logger.log("User context value is too long")
        if not _did_logged_from_validate_value:
            user_logger.log(*UsersLogs.SET_CONTEXT_VALUE_IS_TOO_LONG(key_string))
            _did_logged_from_validate_value = True
        return False

    if not isinstance(value, (int, float, bool, str, type(None))):
        limited_logger.log("User context value is not a primitive")
        if not _did_logged_from_validate_value:
            user_logger.log(
                *UsersLogs.SET_CONTEXT_VALUE_IS_NOT_PRIMITIVE(
                    key_string + "Type: " + str(type(value))
                )
            )
            _did_logged_from_validate_value = True
        return False

    return True


def _validate_context(context: Dict[str, Any]) -> Dict[str, Any]:
    try:
        validated_context: Dict[str, Any] = {}

        for key in context:
            try:
                if len(validated_context) >= config.max_context_keys:
                    limited_logger.log("User context has too many keys")
                    user_limited_logger.log(UsersLogs.SET_CONTEXT_MAX_KEYS_EXCEEDED[1])
                    break

                if not isinstance(key, str):
                    limited_logger.log("User context key is not a string")
                    user_limited_logger.log(UsersLogs.SET_CONTEXT_KEY_IS_NOT_STRING[1])
                    continue

                if len(key) > config.max_context_key_length:
                    limited_logger.log("User context key is too long")
                    user_limited_logger.log(UsersLogs.SET_CONTEXT_KEY_TOO_LONG[1])
                    continue

                if isinstance(context[key], list):
                    if len(context[key]) == 0:
                        limited_logger.log("User context array is empty")
                        user_limited_logger.log(UsersLogs.SET_CONTEXT_EMPTY_ARRAY[1])
                        # We should allow set context of empty array

                    validated_array: List[Any] = []
                    for item in context[key]:
                        if len(validated_array) >= config.max_context_array_length:
                            limited_logger.log("User context array has too many items")
                            user_limited_logger.log(
                                UsersLogs.SET_CONTEXT_ARRAY_TOO_LONG[1]
                            )
                            break

                        if not _validate_value(item, key, True):
                            continue

                        validated_array.append(item)

                    if len(validated_array) == 0:
                        limited_logger.log("User context array all items are invalid")
                        user_limited_logger.log(
                            UsersLogs.SET_CONTEXT_ARRAY_ALL_ITEMS_INVALID[1]
                        )
                        # We should allow set context of empty array

                    validated_context[key] = validated_array
                    continue

                if _validate_value(context[key], key, False):
                    validated_context[key] = context[key]
            except Exception:
                limited_logger.log(
                    "Failed to validate context value", data={"key": key}, exc_info=True
                )
                user_limited_logger.log(UsersLogs.SET_CONTEXT_FAILED_TO_VALIDATE[1])
                continue

        return validated_context

    except Exception:
        limited_logger.log("Failed to validate context", exc_info=True)
        user_limited_logger.log(UsersLogs.SET_CONTEXT_FAILED_TO_VALIDATE[1])
        return {}


def set_user_context(**kwargs: Any) -> None:
    try:
        if not config.enable_investigation:
            return

        raw_investigation = get_investigation()

        if raw_investigation is None:
            limited_logger.log("set user context called not in flow")
            user_limited_logger.log(UsersLogs.SET_ERROR_CALLED_NOT_IN_FLOW[1])
            return

        validated_context = _validate_context(kwargs)
        raw_investigation.user_context.update(validated_context)
    except Exception:
        limited_logger.log("Failed to set user context", exc_info=True)
        user_limited_logger.log(UsersLogs.SET_CONTEXT_FAILED[1])
        return
