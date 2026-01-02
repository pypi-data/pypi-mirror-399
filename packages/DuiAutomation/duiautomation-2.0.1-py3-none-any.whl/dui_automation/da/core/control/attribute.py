import typing
from abc import abstractmethod, ABC

from dui_automation.da.core.exception import ControlNoSuchAttributeError, ControlAttributeInvalidError


class AttributeAccessor(ABC):
    """
    Attribute accessor for control.
    """

    def __init__(
            self,
            readonly: bool = True,
            allowed_none: bool = True
    ):
        self.readonly = readonly
        self.allowed_none = allowed_none

    def __set_name__(self, owner, name):
        self.attribute_name = name

    def __get__(self, instance, owner=None):
        value = instance.get(self.attribute_name)
        if self.allowed_none and value is None:
            return value
        else:
            value = self.validate(value)
            return value

    def __set__(self, instance, value):
        if self.readonly:
            raise AttributeError(f"Attribute {self.attribute_name} is read-only")

    @abstractmethod
    def validate(self, value):
        pass

    def _validate_type(self, value, required_type):
        if value is None:
            raise ControlNoSuchAttributeError(self.attribute_name, value)

        if not isinstance(value, required_type):
            raise ControlAttributeInvalidError(self.attribute_name, value, required_type)
        return value


class IntAttributeAccessor(AttributeAccessor):
    def validate(self, value):
        return self._validate_type(value, int)


class StrAttributeAccessor(AttributeAccessor):
    def validate(self, value):
        return self._validate_type(value, str)


class ListAttributeAccessor(AttributeAccessor):
    def validate(self, value):
        return self._validate_type(value, list)


class BoolAttributeAccessor(AttributeAccessor):
    def validate(self, value):
        if value in [0, 1]:
            value = value == 1      # Turn 0, 1 to bool
        return self._validate_type(value, bool)
