from dui_automation.da.common.configurator import Configurator
from dui_automation.da.mixins.rpc.driver import DriverRPCScriptMixin
from dui_automation.da.mixins.uia.window import DAControl
from dui_automation.da.mixins.watcher_manager import WatcherManagerMixin
from dui_automation.hook.da_frida import DAFrida, print_message


class Driver(WatcherManagerMixin): ...


class FridaDriver(Driver, DriverRPCScriptMixin):

    def __init__(self):
        super().__init__()
        self.frida = DAFrida(on_message=print_message)

    def __getattribute__(self, item):
        if item == "script":
            return self.frida.script
        return super().__getattribute__(item)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def attach(self, target_process):
        self.frida.attach(target_process)

    def spawn(self, target_process):
        self.frida.spawn(target_process)

    def close(self):
        super().close()
        self.frida.close()

    @property
    def config(self):
        return Configurator


class UiaDriver(Driver, DAControl):
    """Driver that uses uiautomation backend through DAUia adapter.
    Keeps same public interface as FridaDriver so existing code can switch drivers
    without changing method names.
    """

    # def find_window_hwnd(self):
    #     from dui_automation.hook.da_uia import window
    #     return window()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def attach(self, target_process):
        # uiautomation does not attach to a process; keep method for compatibility
        pass

    def spawn(self, target_process):
        # uiautomation does not spawn processes; keep method for compatibility
        pass

    def close(self):
        super().close()
        try:
            self.uia.close()
        except Exception:
            pass

    @property
    def config(self):
        return Configurator


def on_message(message, data):
    print(message)
