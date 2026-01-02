import logging
from typing import List, Tuple


class UsersLogs:
    HUD_SERVICE_NOT_SET = (
        logging.ERROR,
        "Can't load Hud. \
Please set service name. For more information visit https://docs.hud.io/docs/py-sdk-ie. E0001",
    )
    HUD_SERVICE_INVALID = (
        logging.ERROR,
        "Can't load Hud. \
Please set a valid service name. For more information visit https://docs.hud.io/docs/py-sdk-ie. E0002",
    )
    HUD_KEY_NOT_SET = (
        logging.ERROR,
        "Can't load Hud. \
Please set API key. For more information visit https://docs.hud.io/docs/py-sdk-ie. E0003",
    )
    HUD_KEY_INVALID = (
        logging.ERROR,
        "Can't load Hud. \
Please set a valid API key. For more information visit https://docs.hud.io/docs/py-sdk-ie. E0004",
    )
    HUD_TAGS_INVALID_TYPE = (
        logging.WARN,
        "HUD_TAGS should be of type Dict[str, str], Hud will run without tags. \
Please set valid tags in env var HUD_TAGS. For more information visit https://docs.hud.io/docs/py-sdk-ie. E0005",
    )
    HUD_TAGS_WITH_DOTS = (
        logging.WARN,
        "HUD_TAGS keys can't contain dots, they have been replaced with underscores. For more information visit https://docs.hud.io/docs/py-sdk-ie. E0006",
    )
    HUD_TAGS_INVALID_JSON = (
        logging.WARN,
        "HUD_TAGS is not a valid json, defaulting to empty tags. \
Please set valid textual tags in env var HUD_TAGS. For more information visit https://docs.hud.io/docs/py-sdk-ie. E0007",
    )
    HUD_INITIALIZED_SUCCESSFULLY = (
        logging.INFO,
        "Initialized successfully",
    )
    HUD_RUN_EXPORTER_FAILED = (
        logging.ERROR,
        "SDK has initiated a graceful shutdown. Your application remains unaffected. E0008",
    )
    HUD_FAILED_TO_CONNECT_TO_MANAGER = (
        logging.ERROR,
        "SDK has initiated a graceful shutdown. Your application remains unaffected. E0009",
    )
    HUD_EXCEPTION_IN_WORKER = (
        logging.ERROR,
        "SDK has initiated a graceful shutdown. Your application remains unaffected. E0010",
    )
    HUD_EXPORTER_STARTUP_TIMEOUT = (
        logging.ERROR,
        "SDK has initiated a graceful shutdown. Your application remains unaffected. E0011",
    )

    HUD_PYTHON_EXECUTABLE_NOT_FOUND = (
        logging.ERROR,
        "Can't load Hud, Python executable was not found. Please set HUD_PYTHON_BINARY_PATH with the python executable path. For more information visit https://docs.hud.io/docs/py-sdk-ie. E0012",
    )
    HUD_FAILED_TO_COMMUNICATE_WITH_MANAGER = (
        logging.ERROR,
        "SDK has initiated a graceful shutdown. Your application remains unaffected. E0013",
    )
    HUD_NO_MANAGER = (
        logging.ERROR,
        "SDK has initiated a graceful shutdown. Your application remains unaffected. E0014",
    )
    HUD_FAILED_TO_REGISTER_PROCESSES = (
        logging.ERROR,
        "SDK has initiated a graceful shutdown. Your application remains unaffected. E0015",
    )
    HUD_FAILED_TO_OPEN_SHARED_MEMORIES = (
        logging.ERROR,
        "SDK has initiated a graceful shutdown. Your application remains unaffected. E0016",
    )
    HUD_FAILED_TO_REGISTER_TASKS = (
        logging.ERROR,
        "SDK has initiated a graceful shutdown. Your application remains unaffected. E0017",
    )
    HUD_THROTTLED = (
        logging.WARN,
        "SDK initialized successfully in idle mode.",
    )
    HUD_FIRST_DECL_COLLECTED = (
        logging.INFO,
        "First source mapping collected successfully",
    )
    HUD_FIRST_METRICS_COLLECTED = (
        logging.INFO,
        "First metrics collected successfully",
    )
    HUD_HAPPY_FLOW_COMPLETED = (
        logging.INFO,
        "Your service is sending data successfully",
    )
    HUD_INIT_TIMEOUT = (
        logging.ERROR,
        "SDK imported but not initialized. Please ensure to call 'init_session()' to initialize the SDK. E0018",
    )
    HUD_INIT_GENERAL_ERROR = (
        logging.ERROR,
        "Can't load Hud due to a general error, please contact support. E0019",
    )

    """
    Just for docs purposes, not used in the code.
    The logs are written explicitly in the hud_entrypoint.py file.
    In case you want to change them, please edit it both here and in the hud_entrypoint.py files.
    HUD_ENTRYPOINT_COMMAND_NOT_FOUND = (
        logging.ERROR,
        "Command executable not found.",
    )
    """
    """
    Just for docs purposes, not used in the code.
    The logs are written explicitly in the empty sdk in __init__ and sitecustomize.py file.
    In case you want to change them, please edit it both here and in the __init__ and sitecustomize.py files.
    HUD_NOT_SUPPORTED_PLATFORM = (
        logging.ERROR,
        "Hud does not support this platform yet. The SDK has initiated a graceful shutdown. Your application remains unaffected. See the compatibility matrix for details: https://docs.hud.io/docs/hud-sdk-compatibility-matrix-for-python"
    )
    """

    @staticmethod
    def FILE_TOO_LARGE_TO_MONITOR(path: str, file_size: int) -> Tuple[int, str]:
        return (
            logging.WARNING,
            f"File is too large to be monitored, skipping. Path: {path}. File size: {file_size} bytes. E0020",
        )

    @staticmethod
    def MAX_INSTRUMENTED_FUNCTIONS_REACHED(
        max_mapped_functions: int,
    ) -> Tuple[int, str]:
        return (
            logging.ERROR,
            f"SDK limit of {max_mapped_functions} instrumented functions exceeded. Hud will provide partial data. Your application remains unaffected. E0021",
        )

    @staticmethod
    def POD_MEMORY_TOO_LOW(min_pod_memory_mb: int) -> Tuple[int, str]:
        return (
            logging.ERROR,
            f"Insufficient memory available. Minimum required:({min_pod_memory_mb}MB). SDK has initiated a graceful shutdown. Your application remains unaffected. E0022",
        )

    @staticmethod
    def PROCESSES_LIMIT_REACHED(max_processes: int) -> Tuple[int, str]:
        return (
            logging.WARN,
            f"SDK limit of {max_processes} processes exceeded. Hud will provide partial data. Your application remains unaffected. E0023",
        )

    GIL_NOT_ENABLED = (
        logging.ERROR,
        "Hud is not supported without GIL. Please enable GIL. Your application remains unaffected. E0024",
    )
    JIT_ENABLED = (
        logging.ERROR,
        "Hud is not supported with JIT. Please disable JIT. Your application remains unaffected. E0025",
    )

    REGISTER_NOT_CALLED = (
        logging.ERROR,
        "Please call 'register()' before 'init_session()'. Your application remains unaffected. E0026",
    )

    @staticmethod
    def CONFIG_PATH_NOT_FOUND(config_path: str, cwd: str) -> Tuple[int, str]:
        return (
            logging.ERROR,
            f"Config file not found: {config_path}, cwd: {cwd}. E0027",
        )

    @staticmethod
    def CONFIG_PATH_NOT_A_PY_FILE(config_path: str) -> Tuple[int, str]:
        return (
            logging.ERROR,
            f"Config file is not a Python file: {config_path}. E0028",
        )

    @staticmethod
    def FAILED_LOADING_CONFIG(config_path: str, error: Exception) -> Tuple[int, str]:
        return (
            logging.ERROR,
            f"Failed to load config file: {config_path}, error: {error}. E0029",
        )

    CONFIG_FILE_DONT_EXPORT_CONFIG = (
        logging.ERROR,
        "Config file does not export config variable. E0030",
    )

    CONFIG_VAR_IS_NOT_HUD_CONFIG = (
        logging.ERROR,
        "Config variable is not a RegisterConfig object. E0031",
    )

    HUD_DISABLED_BY_VAR = (
        logging.ERROR,
        "Hud is disabled by HUD_ENABLE environment variable. Your application remains unaffected.",
    )

    @staticmethod
    def PRELOADED_FRAMEWORKS(frameworks: List[str]) -> Tuple[int, str]:
        frameworksString = ", ".join(frameworks)
        return (
            logging.WARN,
            f"The framework(s): {frameworksString} was imported before register(). This means Hud might track partial framework invocations. Please move register() call to an earlier location. Your application continues normally, but with partial Hud data. E0032",
        )

    @staticmethod
    def UNINSTRUMENTED_FILES_LOG(
        amount_of_uninstrumented_files: int,
    ) -> Tuple[int, str]:
        return (
            logging.WARN,
            f"{amount_of_uninstrumented_files} of your code files were imported before register(). This means Hud won't track all of your functions. Please move register() call to an earlier location. To view the list of files use register({{verbose: true}}). Your application continues normally, but with partial Hud data. E0033",
        )

    @staticmethod
    def FILES_IMPORTED_BEFORE_REGISTER(files: List[str]) -> Tuple[int, str]:
        files_string = "\n".join([f"\t{i+1}. {file}" for i, file in enumerate(files)])
        return (
            logging.INFO,
            f"Files imported before register:\n{files_string}\n",
        )

    NO_INVOCATION_COLLECTED = (
        logging.WARN,
        "Code mapped successfully, but no function activity was tracked. Make sure your service is running and actively handling requests. E0034",
    )

    DECL_COLLECTED_BUT_NO_INVOCATION_COLLECTED = (
        logging.WARN,
        "Code mapped successfully, but no function activity was tracked. Make sure your service is running and actively handling requests. E0035",
    )

    NO_DECLS_AND_NO_INVOCATIONS_COLLECTED = (
        logging.WARN,
        "No code has been mapped so far. This probably means register() was called too late - after your code was already loaded. Move it to the top of your entry file to enable proper mapping. Your application continues normally without Hud data. E0036",
    )

    SET_ERROR_CALLED_NOT_IN_FLOW = (
        logging.WARN,
        "Called to hud_sdk.set_failure() isn't supported outside of a flow.",
    )

    SET_ERROR_CALLED_WITHOUT_ENABLE_USER_FAILURE = (
        logging.WARN,
        "Called to hud_sdk.set_failure() isn't supported without enable_user_failure set to True.",
    )

    @staticmethod
    def SET_CONTEXT_VALUE_IS_TOO_LONG(key_string: str) -> Tuple[int, str]:
        return (
            logging.WARN,
            f"Value exceeds the 256-character limit. Entry was skipped. Shorten the value to 256 characters or fewer. {key_string} E0037",
        )

    @staticmethod
    def SET_CONTEXT_VALUE_IS_NOT_PRIMITIVE(key_string: str) -> Tuple[int, str]:
        return (
            logging.WARN,
            f"Value must be a primitive or an array of primitives. Entry was skipped. Use a string, number, boolean, or an array of these types. {key_string} E0038",
        )

    SET_CONTEXT_MAX_KEYS_EXCEEDED = (
        logging.WARN,
        "A maximum of 20 context keys is allowed. Additional keys were ignored. Pass fewer than 20 keys to setContext(). E0039",
    )
    SET_CONTEXT_KEY_IS_NOT_STRING = (
        logging.WARN,
        "Context key must be a string. This entry was skipped. Only string keys are supported in setContext(). E0040",
    )
    SET_CONTEXT_KEY_TOO_LONG = (
        logging.WARN,
        "Context key exceeds the 64-character limit and was skipped. Shorten the key to 64 characters or fewer. E0041",
    )
    SET_CONTEXT_EMPTY_ARRAY = (
        logging.WARN,
        "Context key is an empty array and was skipped. Use a non-empty array. E0042",
    )
    SET_CONTEXT_ARRAY_TOO_LONG = (
        logging.WARN,
        "A maximum of 20 items is allowed in array. Additional items were ignored. Trim the array to 20 items or fewer. E0043",
    )
    SET_CONTEXT_ARRAY_ALL_ITEMS_INVALID = (
        logging.WARN,
        "Context key is invalid. All items in the array are unsupported. Entry was skipped. Use an array containing only strings, numbers, or booleans. E0044",
    )
    SET_CONTEXT_FAILED_TO_VALIDATE = (
        logging.WARN,
        "Failed to validate context. E0045",
    )
    SET_CONTEXT_FAILED = (
        logging.WARN,
        "Failed to set context. E0046",
    )
