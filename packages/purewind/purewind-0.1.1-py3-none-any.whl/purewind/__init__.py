# purewind/__init__.py

# expose the public factory so users can simply write ``from purewind import createWindow``
from .purewind import createWindow  # noqa: F401

# also expose the Window class if you want direct access
from .purewind import Window        # noqa: F401

__all__ = ["createWindow", "Window"]
__version__ = "0.1.1"