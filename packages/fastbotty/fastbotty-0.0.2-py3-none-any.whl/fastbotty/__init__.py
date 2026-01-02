"""FastBotty - Multi-platform Bot Framework"""

from fastbotty.__version__ import __version__
from fastbotty.core.interfaces import IFormatter, IPlugin
from fastbotty.server.app import create_app

__all__ = ["__version__", "create_app", "IFormatter", "IPlugin"]
