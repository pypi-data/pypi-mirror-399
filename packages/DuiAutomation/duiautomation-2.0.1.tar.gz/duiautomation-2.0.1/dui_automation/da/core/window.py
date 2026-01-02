from functools import wraps

from dui_automation.da.common.configurator import Configurator
from dui_automation.da.common.decorator import poll
from dui_automation.da.core.exception import WindowNotFoundError
from dui_automation.da.core.hwnd import HWND, Owner
from dui_automation.da.mixins.watcher_manager import WatcherManagerReadOnlyMixin
from dui_automation.da.mixins.rpc.window import WindowRPCScriptMixin
from dui_automation.da.mixins.rpc.window_action import WindowActionRPCScriptMixin


def window():
    """
    Decorator for getting window.

    Returns:
        Window -- window.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, class_name, window_name):
            if self.in_watcher_context:
                # We are already in watcher context:
                # so we don't need to run watchers,
                # and we don't need to find control via poll.
                window_hwnd = func(self, class_name, window_name)
            else:
                wait_for_window_time_out = Configurator.WAIT_FOR_WINDOW_TIMEOUT
                wait_for_window_poll = Configurator.WAIT_FOR_WINDOW_POLL
                exception = WindowNotFoundError(class_name if class_name else window_name)
                callback = self.run_watchers

                window_hwnd = poll(
                    timeout=wait_for_window_time_out,
                    interval=wait_for_window_poll,
                    exception=exception,
                    callback=callback,
                )(func)(self, class_name, window_name)

            if window_hwnd:
                owner = Owner(driver=self)
                return Window(window_hwnd, self.script, owner)
            else:
                return None

        return wrapper

    return decorator


class Window(HWND, WatcherManagerReadOnlyMixin, WindowRPCScriptMixin, WindowActionRPCScriptMixin):

    def __init__(self, hwnd, script, owner: Owner):
        super().__init__(hwnd, script, owner)

    def __str__(self):
        return f"<Window hwnd={self.hwnd}>"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.hwnd == other.hwnd

    def __hash__(self):
        return hash(self.hwnd)
