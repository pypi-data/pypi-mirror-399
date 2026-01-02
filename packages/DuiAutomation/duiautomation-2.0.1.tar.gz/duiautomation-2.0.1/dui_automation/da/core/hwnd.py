class Owner:
    def __init__(self, driver=None, window=None):
        self._driver = driver
        self._window = window

    @property
    def driver(self):
        return self._driver

    @driver.setter
    def driver(self, value):
        self._driver = value

    @property
    def window(self):
        return self._window

    @window.setter
    def window(self, value):
        self._window = value


class HWND:

    def __init__(self, hwnd, script, owner: Owner):
        self.hwnd = hwnd
        self.script = script
        self.owner = owner
