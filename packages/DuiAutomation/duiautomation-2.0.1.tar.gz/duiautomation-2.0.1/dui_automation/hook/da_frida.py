
import frida
import os

from typing import Callable

from dui_automation.hook.messages import print_message


class DAFrida:

    def __init__(
            self,
            js_script: str = os.path.join(
                os.path.abspath(__file__),
                "../../scripts/duilib.js"
            ),
            on_message: Callable = None
    ):
        with open(js_script, "r", encoding="utf-8") as f:
            self.js = f.read()
        self.on_message = on_message
        self.script = None

    def attach(self, target_process):
        session = frida.attach(target_process)
        if not self.script:
            self.script = session.create_script(self.js)

        if self.on_message:
            self.script.on("message", self.on_message)

        self.script.load()

    def spawn(self, target_exec_path):
        pid = frida.spawn(target_exec_path)
        frida.resume(pid)
        self.attach(pid)

    def close(self):
        if self.script and not self.script.is_destroyed:
            self.script.unload()


if __name__ == '__main__':
    daf = DAFrida(on_message=print_message)
    daf.attach("QiYou.exe")
