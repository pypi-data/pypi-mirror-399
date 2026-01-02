# -*- coding:utf-8 -*-
# @FileName  :window.py
# @Time      :2025/10/10 20:01
# @Author    :wangfei

import uiautomation as uia


class DAControl:
    def __init__(self, uia_control: uia.Control):
        self._control = uia_control

    def __getattr__(self, name):
        """
        代理底层 uia.Control 的属性/方法。
        使用 object.__getattribute__ 安全获取 _control，避免因间接代理带来的递归调用。
        对双下划线系统属性直接抛出 AttributeError，避免干扰 Python 内部行为。
        """
        # 禁止代理魔法方法，交给 Python 本身处理
        if name.startswith("__") and name.endswith("__"):
            raise AttributeError(name)

        try:
            control = object.__getattribute__(self, "_control")
        except AttributeError:
            raise AttributeError(f"'DAControl' has no attribute '{name}'")

        if control is None:
            raise AttributeError(
                f"'DAControl' has no attribute '{name}' because internal control is None."
            )

        try:
            return getattr(control, name)
        except AttributeError:
            raise AttributeError(f"Underlying control has no attribute '{name}'")
        except Exception as e:
            # 其它底层异常不应导致无限递归，包装成 AttributeError
            raise AttributeError(f"Error getting attribute '{name}': {e}")

    def __bool__(self) -> bool:
        """
        定义对象的布尔值，使得 `if control:` 这样的判断能正确工作。
        只有当控件有效且在屏幕上时才为 True。
        """
        try:
            # 确保控件存在且在屏幕上可见
            return (
                self._control
                and self._control.Exists()
                and not self._control.IsOffscreen
            )
        except Exception:
            return False

    def __str__(self):
        if self._control:
            return f"DAControl(Name='{self._control.Name}', ClassName='{self._control.ClassName}', AutomationId='{self._control.AutomationId}', ControlType='{self.control_type}'), Rect={self._control.BoundingRectangle}"
        return "DAControl(None)"

    @property
    def clickable(self) -> bool:
        """判断控件是否可点击"""
        if self._control:
            return self._control.IsEnabled
        return False

    @property
    def name(self):
        if self._control:
            return self._control.Name
        return ""

    @property
    def text(self) -> str:
        if self._control:
            return self._control.Name
        return ""

    @property
    def visible(self) -> int:
        """判断控件可见 0 不可见 1 可见"""
        if self._control and self._control.Exists() and not self._control.IsOffscreen:
            return 1
        return 0

    @property
    def exist(self) -> bool:
        """判断控件可见"""
        return bool(self.visible)

    @property
    def selected(self):
        """判断控件是否被选中"""
        if self._control:
            return int(
                self._control.GetPattern(uia.PatternId.SelectionItemPattern).IsSelected
            )
        return 0

    @property
    def parent(self):
        """获取父控件"""
        if self._control:
            parent = self._control.GetParentControl()
            return DAControl(parent)
        return None

    def click(self):
        if self._control:
            self._control.Click(simulateMove=False)

    def double_click(self):
        if self._control:
            self._control.DoubleClick(simulateMove=False)

    def right_click(self):
        if self._control:
            self._control.RightClick(simulateMove=False)

    def middle_click(self):
        if self._control:
            self._control.MiddleClick(simulateMove=False)

    def mouse_wheel(
        self, direction: str = "down", wait_time: int = 1, wheel_count: int = 1
    ):
        """滚动鼠标滚轮
        Args:
            direction (str, optional): 滚动方向. Defaults to "down".
            wait_time (int, optional): 等待时间. Defaults to 1.
            wheel_count (int, optional): 滚动次数. Defaults to 1.
        """
        if self._control:
            if direction == "down":
                self._control.WheelDown(waitTime=wait_time, wheelTimes=wheel_count)
            elif direction == "up":
                self._control.WheelUp(waitTime=wait_time, wheelTimes=wheel_count)
            else:
                raise ValueError(f"Invalid direction: {direction}, must be 'down' or 'up'")

    def set_text(self, text: str):
        """写入文本"""
        if self._control:
            # 1. 保存当前剪贴板内容
            original_clipboard = uia.GetClipboardText()
            # 2. 设置剪贴板为要输入的内容
            uia.SetClipboardText(text)
            self.click()
            self._control.SendKeys("{Ctrl}a", waitTime=0.1)
            self._control.SendKeys("{Delete}", waitTime=0.1)  # 删除
            # 3. 模拟粘贴
            self._control.SendKeys("{Ctrl}v", waitTime=0.2)
            # 4. 恢复原始剪贴板内容
            uia.SetClipboardText(original_clipboard)

    @property
    def hwnd(self):
        """获取窗口句柄"""
        if self._control:
            return self._control.NativeWindowHandle
        return None

    @property
    def control_type(self):
        """获取控件类型"""
        if self._control:
            return self._control.ControlTypeName
        return ""

    def refresh(self):
        """刷新控件引用"""
        if self._control:
            self._control.Refind()

    def press_key(self, key: str):
        """按下键盘按键"""
        if self._control:
            self._control.SendKey(uia.SpecialKeyNames[key.upper()])

    @property
    def child_controls(self) -> list["DAControl"]:
        """获取子控件列表"""
        if self._control:
            children = self._control.GetChildren()
            return [DAControl(child) for child in children]
        return []

    def click_xy(self, x, y):
        """点击控件中心点"""
        if self._control:
            self._control.Click(x=x, y=y, simulateMove=False)

    def set_visible(self, visible: bool):
        """设置控件可见性"""
        if self._control:
            if visible:
                self._control.Show()
            else:
                self._control.Hide()

    def hover(self):
        """将鼠标悬停在控件上"""
        if self._control:
            self._control.MoveCursorToMyCenter(simulateMove=False)


    def position(self):
        """获取控件位置"""
        if self._control:
            return self._control.GetPosition()
        return None



if __name__ == "__main__":
    # # time.sleep(2)
    #
    # da = DAUIa(class_name="QeeYouMainWindow")
    # c = da.find_control({"CLASS_NAME":"QiYou Recharge Window"})
    # print(c)
    # c = da.find_control({"NAME":"奇游浏览器窗口"})
    # print(c)
    import uiautomation

    from dui_automation.hook.da_uia import DAUIa

    node_window = DAUIa(class_name="QeeYouMainWindow")
    # node_list =DAUIa(uiautomation.Control(searchFromControl=node_window,AutomationId="game_node_info_list").GetChildren())
    # for node in node_list:
    #     print(node.ControlTypeName)
    #
    # node_a = uiautomation.Control(searchFromControl=node_window, Name="重庆-东京-P101430") # 推荐节点
    # print(node_a)
    # print(node_list[2])
    a = node_window.find_control({"id": "gamelayout"})
    a.mouse_wheel(wheel_count=2, direction="up")

    # print(windows.IsOffscreen)
    # print(p_a)
    # win = da.window()
    # elements = da.find_ui_control({"ID": "search_pc_game_option"})
    # print(elements.GetPropertyValue(49402))
    # da.window().SendKey("Enter")
    # size = da.window_size()
    # print(size)
    # for el in elements:
    #     print(el.Name)
    # elements.MoveCursorToMyCenter()
    # a = elements.GetChildren()
    # for _  in a:
    #     print(_.Name)
    # print("win:", win)
    # print(da.find_text({"ID":"qt_chat_content_wnd.mainStackedWidget.mainChat.widget.splitter.widgetRichEditWnd.drich_edit.verticalContentWidget.widget_input_wnd.textEditWidget.textEdit"}))
