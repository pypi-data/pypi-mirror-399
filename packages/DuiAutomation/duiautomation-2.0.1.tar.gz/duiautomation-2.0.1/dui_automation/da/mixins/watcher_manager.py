from collections import OrderedDict

from dui_automation.da.core.watcher import Watcher
from dui_automation.da.core.exception import WatcherRegisterError, WatcherRemoveError, WatcherRegisterInnerError, \
    WatcherRemoveInnerError


class WatcherAttribute:
    """Watcher attribute class.

    To make sure that the `Watcher` will not be cycled called between `Driver` and `Window`,
    the watcher attribute should be shared in all `Watcher`s.

    The `in_watcher_context` make sure that the methods in `Watcher` will not trigger `Watcher` again.
    """
    # It will be shared by all `Driver` or `Window` instances.
    in_watcher_context = False
    watcher_triggers = {}
    watchers = OrderedDict()


class WatcherManagerReadOnlyMixin:
    """Mixin class for watching for changes in the UI.
    Read only version, means you can not register or remove watcher.

    This mixin class provides methods for watching for changes in the UI.
    It will be triggered when the:
    1. `Window` object can not be found.
    2. `Control` object can not be found.
    3. `Window` object is not enable when operating on it (like: `click`, `set_text`).
    """
    watcher_attribute = WatcherAttribute

    def owner_driver_id(self):
        return id(
            self if self.__class__.__name__ == "FridaDriver" else (
                getattr(getattr(self, "owner", None), "driver", None) if getattr(self, "owner", None) else None
            )
        )

    def _add_this_driver_to_watchers(self):
        """
        Add this driver to watchers.
        """
        if self.watcher_attribute.watchers.get(self.owner_driver_id(), None) is None:
            self.watcher_attribute.watchers[self.owner_driver_id()] = OrderedDict()

    def _add_this_driver_to_watcher_triggers(self):
        """
        Add this driver to watchers triggers.
        """
        if self.watcher_attribute.watcher_triggers.get(self.owner_driver_id(), None) is None:
            self.watcher_attribute.watcher_triggers[self.owner_driver_id()] = []

    @property
    def _watchers_of_this_driver(self):
        """
        Get watchers in this driver.

        Returns:
            dict: watchers id in this driver.
        """
        # We use driver_id as key, to avoid the same watcher name in different driver.
        self._add_this_driver_to_watchers()
        return self.watcher_attribute.watchers.get(self.owner_driver_id())

    @property
    def _watcher_triggers_of_this_driver(self):
        """
        Get watcher triggers in this driver.

        Returns:
            list: watcher triggers in this driver.
        """
        # We use self.driver_id() as key, to avoid the same watcher name in different driver.
        self._add_this_driver_to_watcher_triggers()
        return self.watcher_attribute.watcher_triggers.get(self.owner_driver_id())

    @property
    def in_watcher_context(self):
        """
        If we are in watcher context, we should not run watchers again.

        Returns:
            bool: True if we are in watcher context, otherwise False.
        """
        return self.watcher_attribute.in_watcher_context

    @property
    def watcher_triggers(self):
        """
        Get watcher triggers.

        Returns:
            list: watchers triggers.
        """
        return self._watcher_triggers_of_this_driver

    def run_watchers(self):
        """
        Run watchers.
        """

        if self.watcher_attribute.in_watcher_context:
            # We are already in watcher context, skip run watchers.
            # it will never run here (we deal it in  decorator "da.control.control()"),
            # just for readability.
            pass
        else:
            # Run watchers in current driver.
            driver_id = self.owner_driver_id()
            if driver_id is not None:
                for name, watcher in self._watchers_of_this_driver.items():
                    self.watcher_attribute.in_watcher_context = True

                    if watcher.check_for_condition():
                        self.set_watcher_triggers(name)

                    self.watcher_attribute.in_watcher_context = False

    def has_watcher_triggered(self, name: str) -> bool:
        """
        Check if watcher has triggered.

        Arguments:
            name {str} -- watcher name.

        Returns:
            bool -- True if watcher has triggered, otherwise False.
        """
        return name in self._watcher_triggers_of_this_driver

    def has_any_watcher_triggered(self) -> bool:
        """
        Check if any watcher has triggered.

        Returns:
            bool -- True if any watcher has triggered, otherwise False.
        """
        return len(self._watcher_triggers_of_this_driver) > 0

    def set_watcher_triggers(self, name: str):
        """
        Set watcher triggers.

        Arguments:
            name {str} -- watcher name.
        """
        if not self.has_watcher_triggered(name):
            self._watcher_triggers_of_this_driver.append(name)


class WatcherManagerMixin(WatcherManagerReadOnlyMixin):
    """Mixin class for watching for changes in the UI.
    Full version, means you can register or remove watcher.

    This mixin class provides methods for watching for changes in the UI.
    It will be triggered when the:
    1. `Window` object can not be found.
    2. `Control` object can not be found.
    3. `Window` object is not enable when operating on it (like: `click`, `set_text`).
    """

    def __del__(self):
        """
        Delete driver-watcher context.
        """
        self.clean_self_watcher()

    def close(self):
        self.clean_self_watcher()

    def register_watcher(self, watcher: Watcher, name: str = None):
        """
        Register a watcher.

        Arguments:
            watcher {Watcher} -- watcher to register.

        Keyword Arguments:
            name {str} -- watcher name. (default: {None})

        Raises:
            WatcherRegisterInnerError: if we are in watcher context.
            WatcherRegisterError: if watcher name is None or watcher name is already registered.
        """
        if self.watcher_attribute.in_watcher_context:
            raise WatcherRegisterInnerError(name)

        if name is None:
            name = watcher.__class__.__name__

        if name in self._watchers_of_this_driver:
            raise WatcherRegisterError(name)

        self._watchers_of_this_driver.update({name: watcher})

    def remove_watcher(self, name: str):
        """
        Remove a watcher.

        Arguments:
            name {str} -- watcher name.

        Raises:
            WatcherRemoveError: if watcher name is not registered, or we are in watcher context.
        """
        if self.watcher_attribute.in_watcher_context:
            raise WatcherRemoveInnerError(name)

        if name not in self._watchers_of_this_driver:
            raise WatcherRemoveError(name)
        self._watchers_of_this_driver.pop(name)

    def reset_watcher_triggers(self):
        """
        Reset watchers triggers.
        """
        self.watcher_attribute.watcher_triggers = {}

    def reset_watchers(self):
        """
        Reset all watchers.
        """
        self.watcher_attribute.watchers = OrderedDict()

    def reset_self_watchers(self):
        """
        Delete self watcher of this driver.
        """
        if self._watchers_of_this_driver:
            del self.watcher_attribute.watchers[self.owner_driver_id()]

    def reset_self_watcher_triggers(self):
        """
        Delete watcher triggers of this driver.
        """
        if self._watcher_triggers_of_this_driver:
            del self.watcher_attribute.watcher_triggers[self.owner_driver_id()]

    def clean_watcher(self):
        """
        Clean all watchers.
        """
        self.reset_watcher_triggers()
        self.reset_watchers()

    def clean_self_watcher(self):
        """
        Clean self watcher.
        """
        self.reset_self_watcher_triggers()
        self.reset_self_watchers()
