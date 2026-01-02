from . import register
from .worker.worker import depericated_init as init

register()

__all__ = ["init"]
