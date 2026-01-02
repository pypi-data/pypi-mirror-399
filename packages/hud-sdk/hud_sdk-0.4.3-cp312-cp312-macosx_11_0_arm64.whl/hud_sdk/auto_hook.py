from .hook import deprecated_set_hook
from .worker.worker import depericated_init as init

deprecated_set_hook()

__all__ = ["init"]
