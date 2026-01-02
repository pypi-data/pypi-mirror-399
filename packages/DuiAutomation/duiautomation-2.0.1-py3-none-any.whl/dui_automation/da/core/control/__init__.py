import json
from functools import wraps
from typing import Union, List

from dui_automation.da.common.configurator import Configurator
from dui_automation.da.common.decorator import poll
from dui_automation.da.core.control.attribute import (
    IntAttributeAccessor,
    StrAttributeAccessor,
    ListAttributeAccessor,
    BoolAttributeAccessor
)
from dui_automation.da.core.exception import (
    ControlNotFoundError,
    UnrecognizableControlDataError,
)
from dui_automation.da.core.hwnd import HWND, Owner
from dui_automation.da.mixins.rpc.control import ControlRPCScriptMixin
from dui_automation.da.mixins.watcher_manager import WatcherManagerReadOnlyMixin


def recursive_jsonobject_to_control(control_hwnd, control_script, owner: Owner, jsonobject):
    """Convert a list of json objects to a list of Control recursively"""
    if isinstance(jsonobject, dict):
        return Control(control_hwnd, control_script, owner, jsonobject)
    elif isinstance(jsonobject, list):
        return [
            recursive_jsonobject_to_control(control_hwnd, control_script, owner, elem)
            for elem in jsonobject
        ]
    else:
        raise UnrecognizableControlDataError(jsonobject)


def control():
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.in_watcher_context:
                # We are already in watcher context:
                # so we don't need to run watchers,
                # and we don't need to find control via poll.
                control_data = func(self, *args, **kwargs)
            else:
                wait_for_control_timeout = Configurator.WAIT_FOR_CONTROL_TIMEOUT
                wait_for_control_poll = Configurator.WAIT_FOR_CONTROL_POLL
                exception = ControlNotFoundError(func, *args, **kwargs)
                callback = self.run_watchers

                control_data = poll(
                    timeout=wait_for_control_timeout,
                    interval=wait_for_control_poll,
                    exception=exception,
                    callback=callback,
                )(func)(self, *args, **kwargs)

            if control_data:
                if isinstance(control_data, str):
                    control_data = json.loads(control_data)

                self.owner.window = self

                return recursive_jsonobject_to_control(
                    self.hwnd, self.script, self.owner, control_data
                )
            else:
                return None

        return wrapper

    return decorator


class Control(HWND, WatcherManagerReadOnlyMixin, ControlRPCScriptMixin):

    id: Union[int, None] = IntAttributeAccessor()
    name: Union[str, None] = StrAttributeAccessor()
    class_name: Union[str, None] = StrAttributeAccessor()
    text: Union[str, None] = StrAttributeAccessor()
    pos: Union[List[int], None] = ListAttributeAccessor()
    width: Union[int, None] = IntAttributeAccessor()
    height: Union[int, None] = IntAttributeAccessor()
    x: Union[int, None] = IntAttributeAccessor()
    y: Union[int, None] = IntAttributeAccessor()
    padding: Union[List[int], None] = ListAttributeAccessor()
    tooltip: Union[str, None] = StrAttributeAccessor()
    tooltip_width: Union[int, None] = IntAttributeAccessor()
    visible: Union[bool, None] = BoolAttributeAccessor()
    enabled: Union[bool, None] = BoolAttributeAccessor()
    focused: Union[bool, None] = BoolAttributeAccessor()
    scroll_step_size: Union[int, None] = IntAttributeAccessor()
    bk_image: Union[str, None] = StrAttributeAccessor()
    fore_image: Union[str, None] = StrAttributeAccessor()
    # ContainerUI
    child_count: Union[int, None] = IntAttributeAccessor()
    child_controls: Union[List["Control"], None] = ListAttributeAccessor()
    # ListItemUI
    index: Union[int] = IntAttributeAccessor(allowed_none=False)
    selected: Union[bool] = BoolAttributeAccessor(allowed_none=False)
    # IListOwner or TabLayout
    selected_index: Union[int] = IntAttributeAccessor(allowed_none=False)

    js_attribute_map = {
        "id": "id",
        "name": "name",
        "class_name": "class",
        "text": "text",
        "pos": "pos",
        "width": "width",
        "height": "height",
        "x": "x",
        "y": "y",
        "padding": "padding",
        "tooltip": "toolTip",
        "tooltip_width": "toolTipWidth",
        "visible": "visible",
        "enabled": "enabled",
        "focused": "focused",
        "scroll_step_size": "scrollStepSize",
        "bk_image": "bkImage",
        "fore_image": "foreImage",
        # ContainerUI
        "child_count": "childCount",
        "child_controls": "childControls",
        # ListItemUI
        "index": "index",
        "selected": "isSelected",
        # IListOwner or TabLayout
        "selected_index": "selectedIndex",
    }

    # 新增：UIA 备用字段（用于回退查找）
    UIA_ALTERNATE_KEYS = {
        "id": ["automationId", "AutomationId", "id"],
        "name": ["name", "Name"],
        "class_name": ["controlType", "ClassName", "class"],
        "text": ["text", "Name", "name"],
        "pos": ["pos", "boundingRectangle"],
        "width": ["width"],
        "height": ["height"],
        "x": ["x"],
        "y": ["y"],
        "padding": ["padding"],
        "tooltip": ["toolTip", "HelpText", "helpText"],
        "tooltip_width": ["toolTipWidth"],
        "visible": ["visible", "isOffscreen", "IsOffscreen"],
        "enabled": ["enabled", "IsEnabled"],
        "focused": ["focused", "HasKeyboardFocus"],
        "scroll_step_size": ["scrollStepSize"],
        "bk_image": ["bkImage"],
        "fore_image": ["foreImage"],
        "child_count": ["childCount", "children", "Children"],
        "child_controls": ["childControls", "children", "Children"],
        "index": ["index"],
        "selected": ["isSelected", "IsSelected"],
        "selected_index": ["selectedIndex"],
    }

    def __init__(self, hwnd, script, owner: Owner, control_data: dict):
        super().__init__(hwnd, script, owner)
        self._control_data = control_data
        # 检测 control_data 是否更像 UIAutomation（用于可能的特定处理或调试）
        self._is_uia = any(k.lower() in ("automationid", "controltype", "helptext") for k in control_data.keys())

    # 新增：从 control_data 中解析逻辑属性的值（带回退候选及特殊逻辑）
    def _get_value_from_data(self, attr: str, default=None):
        # 首先尝试类级 js_attribute_map 中的主键
        primary_key = self.js_attribute_map.get(attr)
        candidates = []
        if primary_key:
            candidates.append(primary_key)
        # 然后尝试 UIA 备用键
        candidates.extend(self.UIA_ALTERNATE_KEYS.get(attr, []))
        for key in candidates:
            if key in self._control_data:
                val = self._control_data[key]
                # 特殊字段处理：UIA 的 isOffscreen 表示不可见，需取反
                if attr == "visible" and key.lower() == "isoffscreen":
                    try:
                        return not bool(val)
                    except Exception:
                        return default
                return val
        return default

    def __str__(self):
        return f"<CONTROL ID={self.id}>"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self._control_data == other.control_data

    def __getitem__(self, item):
        return self.get(item)

    @property
    def control_data(self) -> dict:
        return self._control_data

    @control_data.setter
    def control_data(self, value: dict):
        self._control_data = value

    def get(self, item, default=None):
        if item == "child_controls":
            _child_controls = []
            # 先尝试常规 key
            child_key = self.js_attribute_map.get("child_controls", "childControls")
            # 允许 UIA 或其他实现的备用 keys
            possible_keys = [child_key] + self.UIA_ALTERNATE_KEYS.get("child_controls", [])
            found = None
            for k in possible_keys:
                if self._control_data.get(k) is not None:
                    found = self._control_data.get(k)
                    break

            if found:
                for ctrl in found:
                    if isinstance(ctrl, dict):
                        _child_controls.append(Control(self.hwnd, self.script, self.owner, ctrl))
                    elif isinstance(ctrl, int):
                        _child_controls.append(self.owner.window.find_control_by_id(ctrl))
                    else:
                        raise UnrecognizableControlDataError(ctrl)
            return _child_controls
        else:
            # 使用回退解析函数，从 control_data 中返回首个匹配字段值
            return self._get_value_from_data(item, default)

    @property
    def parent(self):
        """
        Get parent control.
        """
        return Control(
            self.hwnd,
            self.script,
            self.owner,
            self.get_parent()
        )

    def refresh(self):
        """
        Refresh control.
        """
        self.control_data = self.owner.window.find_control_by_id(self.id).control_data
