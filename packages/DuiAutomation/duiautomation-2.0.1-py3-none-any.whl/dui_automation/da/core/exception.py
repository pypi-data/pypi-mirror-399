from dui_automation.da.common.selector import Selector


class WindowNotFoundError(Exception):
    """
    Exception raised when a window is not found
    """

    def __init__(self, window_name):
        self.window_name = window_name

    def __str__(self):
        return f"Window {self.window_name} not found!"


class ControlNotFoundError(Exception):
    """
    Exception raised when a control is not found
    """

    def __init__(self, func, *args, **kwargs):
        self.locate_name = func.__name__.split("by_")[-1].upper()
        self.control_locate_condition = ""
        if args:
            for arg in args:
                if isinstance(arg, Selector):
                    self.control_locate_condition += f"{arg.by.name}={arg.value}, instance={arg.instance}"
                    break
            else:
                # args[-1] is `verbose`
                self.control_locate_condition += ", ".join([str(arg) for arg in args[:-1]])
        if kwargs:
            for k, v in kwargs.items():
                if isinstance(v, Selector):
                    self.control_locate_condition += f"{v.by.name}={v.value}, instance={v.instance}"
                    break
            else:
                if self.control_locate_condition:
                    self.control_locate_condition += ", "
                self.control_locate_condition += ", ".join(
                    [f"{k}={v}" for k, v in kwargs.items()]
                )

    def __str__(self):
        return (
            f'Control {self.locate_name}: "{self.control_locate_condition}" not found!'
        )


class ControlNotAccessibleError(Exception):
    """
    Exception raised when a control is not found
    """

    def __init__(self, control, action):
        self.control = control
        self.action = action

        self.print_control_info = f"NAME: {self.control.name}" if self.control.name else (
            F"TEXT: {self.control.text}" if self.control.text else self.control.id
        )

    def __str__(self):
        return f'Control "{self.print_control_info}" is not accessible, do `{self.action}` failed!'


class WatcherOperateError(Exception):
    """
    Exception raised when a watcher operate error
    """

    def __init__(self, watcher_name):
        self.watcher_name = watcher_name


class WatcherRegisterError(WatcherOperateError):
    """
    Exception raised when a watcher condition error
    """

    def __str__(self):
        return f"Watcher {self.watcher_name} has already exist!"


class WatcherRemoveError(WatcherOperateError):
    """
    Exception raised when a watcher condition error
    """

    def __str__(self):
        return f"Watcher {self.watcher_name} not found!"


class WatcherRegisterInnerError(WatcherOperateError):
    """
    Exception raised when a watcher condition error
    """

    def __str__(self):
        return f"Cannot register new watcher {self.watcher_name} from within another!"


class WatcherRemoveInnerError(WatcherOperateError):
    """
    Exception raised when a watcher condition error
    """

    def __str__(self):
        return f"Cannot remove watcher {self.watcher_name} from within another!"


class UnrecognizableControlDataError(Exception):
    """
    Exception raised when a control is not found
    """

    def __init__(self, control_data):
        self.control_data = control_data

    def __str__(self):
        return f"Unrecognizable control data: [{self.control_data}]"


class WindowDisabledError(Exception):
    """
    Exception raised when a control is not found
    """

    def __init__(self, control, action):
        self.control = control
        self.action = action

    def __str__(self):
        return f"<Window ID={self.control.hwnd}> is disabled, do `{self.action}` on `{self.control}` failed!"


class ControlNoSuchAttributeError(Exception):
    """
    Exception raised when a control has no such attribute
    """

    def __init__(self, attribute_name, value):
        self.attribute_name = attribute_name
        self.value = value

    def __str__(self):
        return f"Control has no attribute `{self.attribute_name}`. " \
               f"Pls check the Control type!"


class ControlAttributeInvalidError(Exception):
    """
    Exception raised when a control has no such attribute
    """

    def __init__(self, attribute_name, value, required_type):
        self.attribute_name = attribute_name
        self.value = value
        self.required_type = required_type

    def __str__(self):
        return f"Control attribute `{self.attribute_name}` is invalid, " \
               f"value: {self.value}, must be {self.required_type.__name__}!"


class ControlMethodCallError(Exception):
    """
    Exception raised when a control method call error
    """

    def __init__(self, method_name, control):
        self.method_name = method_name
        self.control = control

    def __str__(self):
        return f"`Control` method `{self.method_name}` call error, " \
               f"value: {self.control}!"


class ControlMethodCallTypeError(Exception):
    """
    Exception raised when a control method call timeout
    """

    def __init__(self, method_name: str, required_type: str):
        self.method_name = method_name
        self.required_type = required_type

    def __str__(self):
        return f"Control method `{self.method_name}` should be called with `{self.required_type}`"