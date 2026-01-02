from dui_automation.hook.rpc import DriverRPCScript
from dui_automation.da.core.window import window, Window


class DriverRPCScriptMixin(DriverRPCScript):

    def find_window_hwnd(self, class_name: str = None, window_name: str = None) -> Window:
        """
        Find window by class name and window name.

        Arguments:
            class_name {str} -- class name.

        Keyword Arguments:
            window_name {str} -- window name. (default: {None})

        Returns:
            Window -- window.

        Raises:
            TypeError -- if class_name and window_name are both None.
        """
        if not class_name and not window_name:
            raise TypeError("`class_name` and `window_name` cannot be both None.")
        return window()(getattr(DriverRPCScript, "find_window_hwnd"))(self, class_name, window_name)
