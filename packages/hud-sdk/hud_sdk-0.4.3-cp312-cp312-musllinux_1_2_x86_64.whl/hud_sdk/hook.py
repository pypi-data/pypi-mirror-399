import ast
import importlib
import os
import random
import re
import sys
import time
import traceback
import types
from functools import wraps
from importlib.machinery import ModuleSpec, SourceFileLoader
from site import ENABLE_USER_SITE, getsitepackages, getusersitepackages
from threading import Timer
from types import CodeType
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Mapping,
    Optional,
    Sequence,
    Set,
    TypeVar,
    Union,
    cast,
)
from zlib import crc32

from ._internal import worker_queue
from .collectors.modules import get_pre_init_loaded_modules
from .config import config
from .declarations import Declaration, FileToParse
from .exception_handler import install_exception_handler
from .forkable import register_fork_callbacks
from .instrumentation import (
    instrument_frameworks,
)
from .investigation_manager import init_performance_monitor
from .load import get_global_importing_module
from .logging import internal_logger, user_logger
from .run_mode import disable_hud, set_should_check_env_var, should_run_hud
from .user_logs import UsersLogs
from .user_options import RegisterConfig, set_register_config
from .utils import calculate_uuid

FunctionDef = TypeVar("FunctionDef", ast.FunctionDef, ast.AsyncFunctionDef)


def get_sitepackages() -> List[str]:
    sitepackages: List[str] = [
        *getsitepackages(),  # All site packages directories (venv and system if each applicable)
    ]

    if random.__spec__.origin is not None:
        sitepackages.append(
            os.path.dirname(random.__spec__.origin)
        )  # Python standard library directory

    if __spec__.origin is not None:
        sitepackages.append(
            os.path.dirname(__spec__.origin)
        )  # The directory of the hud_sdk package

    if ENABLE_USER_SITE:
        sitepackages.append(getusersitepackages())

    return sitepackages


def is_path_in_sitepackage(path: str, sitepackages_paths: List[str]) -> bool:
    """
    Check if the given path is in a sitepackage.
    """
    abs_path = os.path.abspath(path)
    for sitepackage_folder in sitepackages_paths:
        if abs_path.startswith(sitepackage_folder + os.path.sep):
            return True

    return False


class ASTTransformer(ast.NodeTransformer):
    def __init__(self, path: str, code: bytes, file_hash: int) -> None:
        self.path = path
        self.file_hash = file_hash
        self.compiler_flags = 0
        self.instrumented_functions = 0

    @staticmethod
    def get_and_remove_docstring(
        node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
    ) -> Optional[ast.stmt]:
        """
        If the first expression in the function is a literal string (docstring), remove it and return it
        """

        AstStrType = ast.Constant if sys.version_info >= (3, 8) else ast.Str

        if not node.body:
            return None
        if (
            isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, AstStrType)
            and (
                isinstance(node.body[0].value.value, str)  # type: ignore[attr-defined]
                if sys.version_info >= (3, 8)
                else isinstance(node.body[0].value.s, str)  # type: ignore[attr-defined]
            )
        ):
            return node.body.pop(0)
        return None

    @staticmethod
    def get_with_location_from_node(node: FunctionDef) -> Dict[str, int]:
        if len(node.body) == 0:
            return {
                "lineno": node.lineno,
                "col_offset": node.col_offset,
                "end_lineno": getattr(node, "end_lineno", node.lineno),
                "end_col_offset": getattr(node, "end_col_offset", node.col_offset),
            }

        return {
            "lineno": node.body[0].lineno,
            "col_offset": node.body[0].col_offset,
            "end_lineno": getattr(node.body[0], "end_lineno", node.body[0].lineno),
            "end_col_offset": getattr(
                node.body[0], "end_col_offset", node.body[0].col_offset
            ),
        }

    def get_with_stmt(self, function_id: str, node: FunctionDef) -> ast.With:
        locations = self.get_with_location_from_node(node)

        args = [
            ast.Constant(value=function_id, kind=None, **locations)
        ]  # type: List[ast.expr]
        return ast.With(
            items=[
                ast.withitem(
                    context_expr=ast.Call(
                        func=ast.Name(id="HudMonitor", ctx=ast.Load(), **locations),
                        args=args,
                        keywords=[],
                        **locations,
                    ),
                )
            ],
            body=[],
            type_comment=None,
            **locations,
        )

    def _visit_generic_FunctionDef(self, node: FunctionDef) -> FunctionDef:
        self.instrumented_functions += 1
        function_id = calculate_uuid(
            "|".join(
                (
                    node.name,
                    self.path,
                    str(Declaration.get_lineno(node)),
                    str(self.file_hash),
                )
            )
        )

        docstring = self.get_and_remove_docstring(node)

        with_stmt = self.get_with_stmt(str(function_id), node)
        with_stmt.body = node.body

        if not with_stmt.body:
            with_stmt.body = [ast.Pass(**self.get_with_location_from_node(node))]

        if docstring is not None:
            node.body = [docstring, with_stmt]
        else:
            node.body = [with_stmt]

        self.generic_visit(node)
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        return self._visit_generic_FunctionDef(node)

    def visit_AsyncFunctionDef(
        self, node: ast.AsyncFunctionDef
    ) -> ast.AsyncFunctionDef:
        return self._visit_generic_FunctionDef(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Optional[ast.ImportFrom]:
        # When passing an AST to the `compile` function, the `__future__` imports are not parsed
        # and the compiler flags are not set. This is a workaround to set the compiler flags,
        # and removing the invalid imports.
        if node.module == "__future__":
            import __future__

            for name in node.names:
                feature = getattr(__future__, name.name)
                self.compiler_flags |= feature.compiler_flag
            return None

        self.generic_visit(node)
        return node


def create_plain_module_checker(module: str) -> Callable[[str], bool]:
    def checker(fullname: str) -> bool:
        if fullname == module:
            return True

        if fullname.startswith("{}.".format(module)):
            return True

        return False

    return checker


def create_wildcard_module_checker(module: str) -> Callable[[str], bool]:
    escaped_module = module.replace("*", r".*?")
    base_search_regex = re.compile(f"^{escaped_module}$")
    dot_search_regex = re.compile(f"^{escaped_module}\\.")

    def checker(fullname: str) -> bool:
        if base_search_regex.match(fullname) is not None:
            return True

        if dot_search_regex.match(fullname) is not None:
            return True

        return False

    return checker


def create_module_to_trace_checkers(
    modules_to_trace: Set[str],
) -> List[Callable[[str], bool]]:
    # Python package name allowed characters: https://stackoverflow.com/questions/75697725/i-want-to-use-special-characters-for-naming-my-module-in-pypi
    checkers = []
    for module in modules_to_trace:
        if "*" in module:
            checkers.append(create_wildcard_module_checker(module))
        else:
            checkers.append(create_plain_module_checker(module))

    return checkers


def should_wrap_module(
    fullname: str,
    checkers: List[Callable[[str], bool]],
    negative_checkers: List[Callable[[str], bool]],
) -> bool:
    for checker in checkers:
        if checker(fullname):
            for nchecker in negative_checkers:
                if nchecker(fullname):
                    return False
            return True
    return False


def hud_pathify(path: str) -> str:
    if config.use_hud_pyc and path.endswith(".py"):
        return path.replace(".py", ".hud.py")
    return path


def hud_unpathify(path: str) -> str:
    if config.use_hud_pyc and path.endswith(".hud.py"):
        return path.replace(".hud.py", ".py")
    return path


total_instrumented_functions = 0


class MySourceLoader(SourceFileLoader):
    _max_mapped_functions = 0
    _max_file_size_bytes = 0

    def __init__(
        self,
        fullname: str,
        origin: str,
        max_mapped_functions: int,
        max_file_size_bytes: int,
    ) -> None:
        super().__init__(fullname, origin)
        self._max_mapped_functions = max_mapped_functions
        self._max_file_size_bytes = max_file_size_bytes

    def path_stats(self, path: str) -> Mapping[str, Any]:
        if config.use_hud_pyc:
            return super().path_stats(hud_unpathify(path))
        else:
            if not path.endswith(".py"):
                return super().path_stats(path)
            stats = super().path_stats(path)
            # This manipulation allows bytecode caching to work for the edited module, without conflicting with the original module
            stats["mtime"] = time.time() * 2 + random.randint(1, 500)  # type: ignore[index]
            return stats

    def get_filename(self, name: Optional[str] = None) -> str:
        path = super().get_filename(name)
        if config.use_hud_pyc:
            return hud_pathify(path)
        return path

    def get_data(self, path: str) -> bytes:
        return super().get_data(hud_unpathify(path))

    def source_to_code(  # type: ignore[override]
        self, data: bytes, path: str, *, _optimize: int = -1
    ) -> CodeType:
        if path and config.use_hud_pyc:
            path = hud_unpathify(path)
        try:
            transformed_code = _transform_ast_code(
                data,
                path,
                self.name,
                self._max_mapped_functions,
                self._max_file_size_bytes,
                optimize=_optimize,
            )

            if transformed_code is None:
                return super().source_to_code(data, path)

            return transformed_code
        except Exception:
            internal_logger.error(
                "Error while transforming AST on file",
                data={"path": path},
                exc_info=True,
            )
            return super().source_to_code(data, path)


def _hook_compile_bytecode() -> None:
    if not config.use_hud_pyc:
        return
    from importlib import _bootstrap_external

    original_compile_bytecode = _bootstrap_external._compile_bytecode  # type: ignore[attr-defined]

    @wraps(original_compile_bytecode)
    def hud_compile_bytecode(
        data: Any,
        name: Optional[str] = None,
        bytecode_path: Optional[str] = None,
        source_path: Optional[str] = None,
    ) -> Any:
        if source_path and config.use_hud_pyc:
            source_path = hud_unpathify(source_path)
        return original_compile_bytecode(data, name, bytecode_path, source_path)

    _bootstrap_external._compile_bytecode = hud_compile_bytecode  # type: ignore[attr-defined]


def _transform_ast_code(
    source_bytes: bytes,
    path: str,
    module_name: str,
    max_mapped_functions: int,
    max_file_size_bytes: int,
    optimize: int = -1,
) -> Optional[CodeType]:
    try:
        if len(source_bytes) > max_file_size_bytes:
            internal_logger.warning(
                "File is too large to be monitored, skipping",
                data={"path": path, "size": len(source_bytes)},
            )
            user_logger.log(
                *UsersLogs.FILE_TOO_LARGE_TO_MONITOR(path, len(source_bytes))
            )
            return None

        internal_logger.debug("Monitoring file: {}".format(path))

        tree = cast(
            ast.Module,
            compile(
                source_bytes,
                path,
                "exec",
                flags=ast.PyCF_ONLY_AST,
                dont_inherit=True,
                optimize=optimize,
            ),
        )

        file_hash = crc32(source_bytes)
        transformer = ASTTransformer(path, source_bytes, file_hash)
        worker_queue.append(FileToParse(path, module_name, file_hash))
        tree = transformer.visit(tree)

        tree.body = [
            *ast.parse("from hud_sdk.native import Monitor as HudMonitor\n").body,
            *tree.body,
        ]

        global total_instrumented_functions  # this limit is per process and not per service
        total_instrumented_functions += transformer.instrumented_functions
        if total_instrumented_functions > max_mapped_functions:
            user_logger.log(
                *UsersLogs.MAX_INSTRUMENTED_FUNCTIONS_REACHED(max_mapped_functions)
            )
            disable_hud(True)
            return None

        return cast(
            CodeType,
            compile(
                tree,
                path,
                "exec",
                flags=transformer.compiler_flags,
                dont_inherit=True,
                optimize=optimize,
            ),
        )
    except Exception:
        internal_logger.error(
            "Error while transforming AST on file",
            data={"path": path},
            exc_info=True,
        )
        return None


def create_get_spec_if_should_wrap(
    module_checkers: List[Callable[[str], bool]],
    blacklist_checkers: List[Callable[[str], bool]],
    sitepackages_paths: List[str],
) -> Callable[[str], Optional[ModuleSpec]]:
    """
    This function return a function that decide if to wrap a module or not.
    If the function decide to wrap the module, it will return the module spec.
    """

    def get_spec_if_should_wrap(
        fullname: str,
    ) -> Optional[ModuleSpec]:
        try:
            spec = importlib.util.find_spec(fullname)
            if spec is None or not isinstance(spec.loader, SourceFileLoader):
                return None

            if not spec.origin:
                return None

            if not is_path_in_sitepackage(spec.origin, sitepackages_paths):
                return spec

            if should_wrap_module(fullname, module_checkers, blacklist_checkers):
                return spec

            return None
        except Exception:
            return None

    return get_spec_if_should_wrap


class InstrumentingPathFinder(importlib.abc.MetaPathFinder):
    def __init__(
        self,
        get_spec_if_should_wrap: Callable[[str], Optional[ModuleSpec]],
        max_mapped_functions: int,
        max_file_size_bytes: int,
    ) -> None:
        self._get_spec_if_should_wrap = get_spec_if_should_wrap
        self._currently_loading: Set[str] = set()
        self._max_mapped_functions = max_mapped_functions
        self._max_file_size_bytes = max_file_size_bytes

    def find_spec(
        self,
        fullname: str,
        path: Optional[Sequence[str]],
        target: Optional[types.ModuleType] = None,
    ) -> Optional[ModuleSpec]:
        if fullname in self._currently_loading:
            # Prevent infinite recursion in case of circular imports
            return None
        self._currently_loading.add(fullname)
        try:
            spec = self._get_spec_if_should_wrap(fullname)
            if spec is None or spec.origin is None:
                return None

            spec.loader = MySourceLoader(
                fullname,
                spec.origin,
                self._max_mapped_functions,
                self._max_file_size_bytes,
            )
            return spec
        except Exception:
            return None
        finally:
            self._currently_loading.remove(fullname)


register_called = False
register_success = False
_is_dumped_decls = False
_is_dumped_invocations = False

did_init_run: bool = False


def set_init_run(did_run: bool = True) -> None:
    global did_init_run
    did_init_run = did_run


def is_init_run() -> bool:
    return did_init_run


def create_init_timeout(init_timeout: int) -> None:
    """
    This isn't the best implementation, but it's good enough as long we have only single timer.
    In case someone read this comment and want to add another timer we might want to implement our own timer thread instread of creating multiple timer threads.
    """

    def handle_init_timeout() -> None:
        global did_init_run

        if not did_init_run:
            user_logger.log(*UsersLogs.HUD_INIT_TIMEOUT)
            return

        if not get_is_dumped_decls() and not get_is_dumped_invocations():
            user_logger.log(*UsersLogs.NO_DECLS_AND_NO_INVOCATIONS_COLLECTED)
            return

        if get_is_dumped_decls() and not get_is_dumped_invocations():
            user_logger.log(*UsersLogs.DECL_COLLECTED_BUT_NO_INVOCATION_COLLECTED)
            return

    init_timer_thread = Timer(init_timeout, handle_init_timeout)
    init_timer_thread.daemon = True
    init_timer_thread.start()


def log_pre_loaded_modules(
    loaded_modules_set: Set[str], should_wrap: Callable[[str], bool], verbose: bool
) -> None:
    should_instrumented_modules = [
        module for module in loaded_modules_set if should_wrap(module)
    ]

    if len(should_instrumented_modules) > config.uninstrumented_files_log_threshold:
        user_logger.log(
            *UsersLogs.UNINSTRUMENTED_FILES_LOG(
                len(should_instrumented_modules),
            )
        )

        if verbose:
            user_logger.log(
                *UsersLogs.FILES_IMPORTED_BEFORE_REGISTER(should_instrumented_modules)
            )


def log_pre_loaded_frameworks(
    loaded_modules_set: Set[str], supporting_frameworks: Set[str]
) -> None:
    preloaded_frameworks_set = loaded_modules_set.intersection(supporting_frameworks)

    if len(preloaded_frameworks_set) > 0:
        user_logger.log(*UsersLogs.PRELOADED_FRAMEWORKS(list(preloaded_frameworks_set)))


def log_register_location_hints(
    supporting_frameworks: Set[str],
    should_wrap: Callable[[str], bool],
    verbose: bool,
) -> None:
    loaded_modules_set = set(sys.modules.keys())
    try:
        log_pre_loaded_modules(loaded_modules_set, should_wrap, verbose)
    except Exception:
        internal_logger.exception("Error in logRegisterInRightLocation")

    try:
        log_pre_loaded_frameworks(loaded_modules_set, supporting_frameworks)
    except Exception:
        internal_logger.exception("Error in logPreLoadedFrameworks")


def register(user_config: RegisterConfig = RegisterConfig()) -> None:
    try:
        global register_called
        if register_called:
            return

        register_called = True

        internal_logger.set_component("main")
        with internal_logger.stage_context("set_hook"):
            should_run_hud_result = should_run_hud(user_config)
            if not should_run_hud_result.should_run:
                if should_run_hud_result.reason:
                    user_logger.log(*should_run_hud_result.reason)

                return

            start_time = time.time()
            try:
                _set_hook(user_config)
            finally:
                internal_logger.info(
                    "Hook set",
                    data={"duration": time.time() - start_time},
                )

            try:
                init_performance_monitor()
            except Exception:
                internal_logger.error(
                    "Failed to init performance monitor", exc_info=True
                )

            global register_success
            register_success = True

    except Exception:
        internal_logger.critical("Error while setting hook", exc_info=True)


def deprecated_set_hook(*args: Any, **kwargs: Any) -> None:
    set_should_check_env_var(True)
    register(*args, **kwargs)


def _set_hook(user_config: RegisterConfig) -> None:
    if not config.disable_exception_handler:
        install_exception_handler()
    internal_logger.info(
        "Hook stacktrace", data={"stacktrace": traceback.format_stack()}
    )
    worker_queue.append(get_pre_init_loaded_modules())
    _hook_compile_bytecode()

    set_register_config(user_config)

    include_modules_set = set(user_config.include_modules)
    global_importing_module = get_global_importing_module()
    if global_importing_module is not None:
        include_modules_set.add(global_importing_module)

    internal_logger.info(
        "Include modules",
        data={
            "include_modules": user_config.include_modules,
            "global_importing_module": get_global_importing_module(),
        },
    )

    get_spec_if_should_wrap = create_get_spec_if_should_wrap(
        create_module_to_trace_checkers(include_modules_set),
        create_module_to_trace_checkers(config.hud_dependency_blacklist),
        get_sitepackages(),
    )
    sys.meta_path.insert(
        0,
        InstrumentingPathFinder(
            get_spec_if_should_wrap,
            user_config.max_mapped_functions,
            user_config.max_file_size_bytes,
        ),
    )

    register_fork_callbacks()
    frameworks_instrumentor = instrument_frameworks()
    create_init_timeout(user_config.init_timeout)

    log_register_location_hints(
        frameworks_instrumentor.get_supported_frameworks(),
        lambda fullname: get_spec_if_should_wrap(fullname) is not None,
        user_config.verbose,
    )


def is_register_called() -> bool:
    return register_called


def is_register_success() -> bool:
    return register_success


def set_dumped_decls() -> None:
    global _is_dumped_decls
    _is_dumped_decls = True


def set_dumped_invocations() -> None:
    global _is_dumped_invocations
    _is_dumped_invocations = True


def get_is_dumped_decls() -> bool:
    return _is_dumped_decls


def get_is_dumped_invocations() -> bool:
    return _is_dumped_invocations
