import logging
import time
from typing import List, Optional, Union

import uiautomation as uia

from dui_automation.da.common.by import By
from dui_automation.da.common.selector import Selector
from dui_automation.da.mixins.uia.window import DAControl
from dui_automation.da.mixins.watcher_manager import WatcherManagerMixin


class DAUIa(WatcherManagerMixin):
    def __init__(
        self, class_name: Optional[str] = None, window_name: Optional[str] = None
    ) -> None:
        super().__init__()
        self._WINDOW_CLASS = class_name
        self._WINDOW_NAME = window_name
        self._window_control = None

    @property
    def window(self) -> uia.Control:
        """查找窗口"""
        # if not self._WINDOW_CLASS and not self._WINDOW_NAME:
        #     raise TypeError("`class_name` and `window_name` cannot be both None.") # 有些控件的第一层不是windows类
        self._window_control = uia.Control(
            searchDepth=1, ClassName=self._WINDOW_CLASS, Name=self._WINDOW_NAME
        )
        return self._window_control


    def find_window_hwnd(
        self, class_name: str = None, window_name: str = None
    ) -> Optional[DAControl]:
        """
        查找窗口句柄
        :param class_name: 窗口类名
        :param window_name: 窗口名称
        :return: DAControl 或者 None
        """
        if not class_name and not window_name:
            raise TypeError("`class_name` and `window_name` cannot be both None.")
        if self.in_watcher_context:
            ctrl = uia.WindowControl(
                searchDepth=1, ClassName=class_name, Name=window_name
            )
            return (
                DAControl(ctrl)
                if ctrl and ctrl.Exists() and not ctrl.IsOffscreen
                else None
            )
        ctrl = uia.WindowControl(searchDepth=2, ClassName=class_name, Name=window_name)
        if ctrl and ctrl.Exists() and not ctrl.IsOffscreen:
            return DAControl(ctrl)
        try:
            self.run_watchers()
        except Exception:
            pass
        return None

    def find_control(self, selector, **kwargs) -> DAControl:
        """适配旧 driver 的 find_control 方法"""
        return self.find_ui_control(selector, **kwargs)

    def find_control_by_id(self, control_id: int, index=1) -> DAControl:
        """通过控件ID查找元素"""
        control = uia.Control(
            searchFromControl=self.window,
            AutomationId=str(control_id),
            foundIndex=index,
        )
        return DAControl(control)

    def find_control_by_name(self, name: str, index=1) -> DAControl:
        """通过控件名称查找元素"""
        control = uia.Control(
            searchFromControl=self.window, Name=name, foundIndex=index
        )
        return DAControl(control)

    def find_control_by_class_name(self, class_name: str, index=1) -> DAControl:
        """通过控件类名查找元素"""
        control = uia.Control(
            searchFromControl=self.window, ClassName=class_name, foundIndex=index
        )
        return DAControl(control)

    @classmethod
    def find_control_by_point(cls, point: [int, int]) -> uia.Control:
        """通过坐标查找元素"""
        x, y = point
        return uia.ControlFromPoint(x, y)

    def find_control_by_reg_name(self, name_regex: str, index=1) -> DAControl:
        """通过控件名称正则查找元素"""
        control = uia.Control(
            searchFromControl=self.window, NameRegex=name_regex, foundIndex=index
        )
        return DAControl(control)

    def find_ui_control(self, selector: Union[dict, Selector], index=1) -> DAControl:
        """查找元素，现在返回 DAControl 对象"""
        control = None
        if isinstance(selector, dict):
            for k, v in selector.items():
                if k.upper() == "ID":
                    control = self.find_control_by_id(v, index)
                elif k.upper() == "NAME":
                    control = self.find_control_by_name(v, index)
                elif k.upper() == "CLASS_NAME":
                    control = self.find_control_by_class_name(v, index)
                elif k.upper() == "POINT":
                    control = self.find_control_by_point(v)
                elif k.upper() == "NAME_CONTAINS":
                    control = self.find_control_by_reg_name(v, index)
                else:
                    raise NotImplementedError(
                        f"Selector by {k} not implemented.,only support ID,NAME,CLASS_NAME,POINT"
                    )
        elif isinstance(selector, Selector):
            if selector.by == By.ID:
                control = self.find_control_by_id(selector.value, index)
            elif selector.by == By.NAME:
                control = self.find_control_by_name(selector.value, index)
            elif selector.by == By.CLASS:
                control = self.find_control_by_class_name(selector.value, index)
            else:
                raise NotImplementedError(
                    f"Selector by {selector.by} not implemented.,only support ID,NAME,CLASS"
                )
        else:
            raise TypeError("selector must be dict or Selector")
        return control

    def find_subcontrols(
        self,
        by: Union[str, Selector],
        value: str,
        parent: Optional[DAControl] = None,
        **kwargs,
    ) -> List[DAControl]:
        """
        【递归】查找一个父控件下的所有符合条件的【后代控件】。
        :param by: 定位策略，使用 By 类中定义的常量 (例如 By.NAME)。
        :param value: 要匹配的属性值 (例如 "确定")。
        :param parent: 可选的父控件（DAControl 类型）。如果为 None，则从主窗口开始查找。
        :param kwargs: 其他可选的筛选条件，例如 IsEnabled=True。
        :return: 一个包含所有匹配的 DAControl 对象的扁平列表。
        """
        # 1. 组合所有筛选条件，这部分和之前一样
        if isinstance(by, By):
            by = by.value
            value += "Control" if not value.endswith("Control") else value
        if isinstance(by, str):
            attr_map = {
                "ID": "AutomationId",
                "NAME": "Name",
                "CLASS_NAME": "ClassName",
                "CONTROL_TYPE": "ControlTypeName",
            }
            by = attr_map.get(by.upper(), by)
        search_criteria = {by: value}
        search_criteria.update(kwargs)

        logging.info(f"==> 正在【递归】查找后代元素，筛选条件: {search_criteria}")
        # 2. 确定搜索的根节点
        search_root = self.window
        if parent:
            if isinstance(parent, DAControl):
                search_root = parent._control
            else:
                logging.warning(
                    "find_subcontrols 的 parent 参数期望是 DAControl 类型。"
                )
                search_root = parent

        # 3. 健壮性检查
        if not search_root or not search_root.Exists():
            logging.warning(
                f"父控件不存在或无效，无法查找子元素。Parent: {search_root}"
            )
            return []
        # 4. 核心递归逻辑
        matched_controls: List[DAControl] = []

        def _recursive_search(current_node: uia.Control):
            """
            一个内部辅助函数，用于执行深度优先搜索。
            """
            try:
                # 遍历当前节点的所有直接子节点
                for child in current_node.GetChildren():
                    # 步骤 A: 检查当前子节点是否匹配条件
                    is_match = True
                    for key, val in search_criteria.items():
                        if not hasattr(child, key) or getattr(child, key) != val:
                            is_match = False
                            break

                    if is_match:
                        # 如果匹配，将其封装后添加到最终结果列表中
                        matched_controls.append(DAControl(child))
                    # 步骤 B: 无论当前子节点是否匹配，都继续深入其后代进行搜索
                    _recursive_search(child)

            except Exception:
                # 在遍历动态UI时，节点可能会突然失效，捕获异常以防止整个搜索失败
                pass

        # 5. 从根节点开始启动递归搜索
        _recursive_search(search_root)
        logging.info(
            f"<== 递归查找完成，共找到 {len(matched_controls)} 个匹配的后代元素。"
        )
        return matched_controls

    def find_parent_control(self, selector) -> Optional[DAControl]:
        """查找父元素"""
        control = self.find_ui_control(selector)
        if control:
            parent = control.GetParentControl()
            return DAControl(parent)
        return None

    def wait_for_visible(
        self,
        control: Union[DAControl, Selector],
        timeout: int = 10,
        interval: float = 0.5,
    ) -> bool:
        """等待元素可见"""
        if isinstance(control, Selector):
            control = self.find_ui_control(control)
        current_time = int(time.time())
        while current_time + timeout >= int(time.time()):
            if control.visible:
                return True
            time.sleep(interval)
        return False

    def wait_for_control_clickable(
        self,
        control: Union[DAControl, Selector, dict],
        timeout: int = 10,
        interval: float = 0.5,
    ) -> bool:
        """等待元素可点击"""
        if isinstance(control, (Selector, dict)):
            control = self.find_ui_control(control)
        current_time = int(time.time())
        while current_time + timeout >= int(time.time()):
            *point, clickable = control.GetClickablePoint()
            if clickable:
                return True
            time.sleep(interval)
        return False

    def find_control_and_click(self, selector, simulate_move: bool = False) -> bool:
        """查找元素并点击"""
        control = self.find_ui_control(selector)
        if control.Exists():
            control.Click(simulateMove=simulate_move)
            return True
        raise Exception(f"Control {selector} is offscreen.")

    def find_control_and_set_text(self, selector, text):
        """查找元素并设置文本"""
        control = self.find_ui_control(selector)
        if control:
            control.SendKeys(text)
            return True
        return False

    def find_text(self, selector):
        """查找元素并获取文本"""
        control = self.find_ui_control(selector)
        if control:
            return control.Name
        return ""

    def window_size(self):
        """获取窗口大小"""
        rect = self.window.BoundingRectangle
        width = rect.right - rect.left
        height = rect.bottom - rect.top
        return width, height

    def find_controls(
        self, selector: Union[dict, Selector], max_index: int = 1000
    ) -> list[DAControl]:
        """查找符合条件的所有元素"""
        if not isinstance(selector, (dict, Selector)):
            raise TypeError("selector must be dict or Selector")
        index = 1
        controls = []
        while index <= max_index:
            try:
                control = self.find_ui_control(selector, index)
            except Exception:
                # 查找过程异常，停止继续查找
                break
            if not control:
                break
            try:
                exists = control.Exists()
            except LookupError:
                # 控件无法通过搜索属性定位，跳出循环
                break
            except Exception:
                continue  # 其他异常，继续尝试下一个索引
            if exists:
                controls.append(control)
                index += 1
                continue
            else:
                break

        return controls

    def press_key(self, key: str):
        """按下键盘按键"""
        self.window.SendKey(uia.SpecialKeyNames[key.upper()])


def window_control(class_name: Optional[str] = None, window_name: Optional[str] = None):
    return DAUIa(class_name=class_name, window_name=window_name)
