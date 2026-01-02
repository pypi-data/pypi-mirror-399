import logging
import time
from functools import wraps
from typing import Callable

from dui_automation.da.common.configurator import Configurator
from dui_automation.da.core.exception import WindowDisabledError, ControlNotAccessibleError
from dui_automation.hook.rpc import RPCScript


def singleton(cls):
    """
    Decorator to make a class singleton
    :param cls:
    :return:
    """
    instance = {}

    def wrapper(*args, **kwargs):
        if cls not in instance:
            instance[cls] = cls(*args, **kwargs)
        return instance[cls]

    return wrapper


def poll(timeout: int, interval: int, exception: Exception = None, callback: Callable = None):
    """
    During the specified "timeout" and "interval", polling the function, and return the result if it is not None
    else run the "callback", finally if timeout raise an "exception".
    :param timeout:超时时间
    :param interval: 重试间隔
    :param exception: 超时后抛出的异常
    :param callback: 每次重试的回调函数
    :return:
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            while time.time() - start_time < timeout:
                result = func(*args, **kwargs)
                if result:
                    return result
                else:
                    if callback:
                        callback()
                time.sleep(interval)
            if exception:
                raise exception
            return None

        return wrapper

    return decorator


def undecorated_control(func):
    """Undecorate an "control" decorator"""
    def wrapper(*args, **kwargs):
        if hasattr(func, "func"):
            return func.func.__wrapped__(
                func.func.__self__,
                hwnd=func.func.__self__.hwnd,
                *args, **kwargs
            )
        else:
            # find_controls_by_jsonpath
            return func.__wrapped__(
                func.__self__,
                *args, **kwargs
            )

    return wrapper


def mixins_call_with_auto_params(func):
    """
    Decorator for calling mixin methods with auto params.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        rpc_scripts = self.rpc_scripts
        func_name = func.__name__
        method_info = rpc_scripts.get(func.__name__, None)

        if method_info:
            new_args = []

            if method_info.get("need_hwnd"):
                new_args.append(self.hwnd)

            if method_info.get("need_control_id"):
                new_args.append(self.id)

            # `self.__class__.__bases__[2].__base__` is a subclass of `RPCScript` in `dui_automation.hook.rpc`.
            for clazz in self.__class__.__bases__:
                if issubclass(clazz, RPCScript):
                    rpc_clazz = clazz.__base__
                    break
            else:
                raise RuntimeError(f"{self.__class__.__name__} has no base class RPCScriptMixin.")
            return getattr(rpc_clazz, func_name)(self, *new_args, *args, **kwargs)
        else:
            raise RuntimeError(f"{self.__class__.__name__} has no method {func_name}.")

    return wrapper


def check_window_enabled(func):
    """
    Decorator for checking window enabled.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.is_window_enabled():
            if self.in_watcher_context:
                # We are already in watcher context:
                # and the window is disabled,
                # we do nothing.
                return False
            else:
                wait_for_control_timeout = Configurator.WAIT_FOR_WINDOW_ENABLE_TIMEOUT
                wait_for_control_poll = Configurator.WAIT_FOR_WINDOW_ENABLE_POLL
                exception = WindowDisabledError(control=self, action=func.__name__)
                callback = self.run_watchers

                poll(
                    timeout=wait_for_control_timeout,
                    interval=wait_for_control_poll,
                    exception=exception,
                    callback=callback,
                )(self.is_window_enabled)()

                return func(self, *args, **kwargs)

        else:
            return func(self, *args, **kwargs)

    return wrapper


def check_control_is_accessible(func):
    """
    Decorator for checking control is accessible via `find_control_by_point_native`.

    if the control is not accessible, we need to trigger to run watchers.
    """

    def _control_is_accessible(self):
        window = self.owner.window
        recheck_control = window.find_control_by_point_native(
            self.control_data["x"] + self.control_data["width"] // 2,
            self.control_data["y"] + self.control_data["height"] // 2
        )
        return recheck_control.id == self.id

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not _control_is_accessible(self):
            if self.in_watcher_context:
                # We are already in watcher context:
                # and the control is not the same,
                # we do nothing.
                return False
            else:
                wait_for_control_timeout = Configurator.WAIT_FOR_CONTROL_ACCESSIBLE_TIMEOUT
                wait_for_control_poll = Configurator.WAIT_FOR_CONTROL_ACCESSIBLE_POLL
                exception = ControlNotAccessibleError(control=self, action=func.__name__)
                callback = self.run_watchers

                poll(
                    timeout=wait_for_control_timeout,
                    interval=wait_for_control_poll,
                    exception=exception,
                    callback=callback,
                )(_control_is_accessible)(self)

                return func(self, *args, **kwargs)

        else:
            return func(self, *args, **kwargs)

    return wrapper


def warning_msg(msg: str):
    """
    Decorator for warning message.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logging.getLogger().warning(msg)
            return func(*args, **kwargs)

        return wrapper
    return decorator
