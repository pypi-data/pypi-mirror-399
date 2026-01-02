from .hook import deprecated_set_hook as set_hook
from .hook import register
from .instrumentation.investigation.investigation_utils import (
    set_user_context as set_context,
)
from .instrumentation.investigation.investigation_utils import (
    set_user_failure as set_failure,
)
from .load import load_hud
from .user_options import RegisterConfig
from .version import version as __version__
from .worker.worker import depericated_init as init
from .worker.worker import init_session

load_hud()

del load_hud

__all__ = [
    "__version__",
    "register",
    "init_session",
    "RegisterConfig",
    "init",
    "set_hook",
    "set_failure",
    "set_context",
]
