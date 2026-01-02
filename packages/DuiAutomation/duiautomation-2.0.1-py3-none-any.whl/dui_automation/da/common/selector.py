from dui_automation.da.common.by import By


class Selector:

    def __init__(self, by, value, instance: int = 0):
        self._by = by
        self._value = value
        self._instance = instance

    @property
    def by(self):
        return self._by

    @by.setter
    def by(self, value):
        if value not in By:
            raise ValueError(f"Invalid by: {value}")
        self._by = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if self.by == By.ID and not isinstance(value, int):
            raise ValueError(f"Invalid value for ID: {value}, must be int")

        if not isinstance(value, str):
            raise ValueError(f"Invalid value: {value}， must be str")
        self._value = value

    @property
    def instance(self):
        return self._instance

    @instance.setter
    def instance(self, value):
        if not isinstance(value, int):
            raise ValueError(f"Invalid instance: {value}， must be int")
        self._instance = value
