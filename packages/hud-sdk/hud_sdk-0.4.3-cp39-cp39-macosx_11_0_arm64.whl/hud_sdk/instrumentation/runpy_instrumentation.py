import os
from functools import wraps
from typing import Any

from ..config import config
from ..hook import _transform_ast_code
from ..logging import internal_logger
from ..user_options import get_register_config
from .base_instrumentation import BaseInstrumentation


class RunpyInstrumentation(BaseInstrumentation):
    def __init__(self) -> None:
        super().__init__("runpy", "python", "0.0.0", None)
        self.did_edit_first_file = False

    def is_enabled(self) -> bool:
        return config.instrument_runpy

    def is_supported(self) -> bool:
        # runpy is always available
        return True

    def _instrument(self) -> None:
        import runpy

        original_get_code_from_file = getattr(runpy, "_get_code_from_file", None)
        if original_get_code_from_file is None:
            return

        user_config = get_register_config()
        if user_config is None:
            internal_logger.warning("RegisterConfig not set, cannot instrument runpy")
            return

        @wraps(original_get_code_from_file)
        def hud_get_code_from_file(*args: Any, **kwargs: Any) -> Any:
            if self.did_edit_first_file:
                return original_get_code_from_file(*args, **kwargs)

            self.did_edit_first_file = True

            if len(args) == 2:
                # Python version < 3.12
                fname = args[1]
                return_fname = True
            else:
                # Python version >= 3.12
                fname = args[0]
                return_fname = False

            code_path = os.path.abspath(fname)

            try:
                import io

                with io.open_code(code_path) as f:
                    source = f.read()

                if isinstance(source, str):
                    source_bytes = source.encode("utf-8")
                else:
                    source_bytes = source

                transformed_code = _transform_ast_code(
                    source_bytes,
                    code_path,
                    "__main__",
                    user_config.max_mapped_functions,
                    user_config.max_file_size_bytes,
                    optimize=-1,
                )

                if transformed_code is not None:
                    if return_fname:
                        return transformed_code, fname
                    else:
                        return transformed_code
            except Exception:
                internal_logger.debug(
                    "Failed to transform code via runpy, using original",
                    data={"path": code_path},
                    exc_info=True,
                )

            return original_get_code_from_file(*args, **kwargs)

        setattr(runpy, "_get_code_from_file", hud_get_code_from_file)
        internal_logger.info("Instrumented runpy._get_code_from_file")
