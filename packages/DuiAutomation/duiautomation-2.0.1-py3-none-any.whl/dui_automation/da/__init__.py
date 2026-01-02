from .core.driver import FridaDriver, UiaDriver
from .core.window import Window
from .core.control import Control
from .core.watcher import Watcher


# Set UiaDriver as default and keep compatibility
DefaultDriver = UiaDriver
FridaDriver = UiaDriver
