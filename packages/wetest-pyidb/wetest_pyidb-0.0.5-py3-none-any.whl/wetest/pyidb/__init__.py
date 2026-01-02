from ._log import PyidbLogger
from .idb import Idb

# 创建全局实例
pyidb_logger = PyidbLogger(__package__)


__all__ = ["Idb", "pyidb_logger"]
