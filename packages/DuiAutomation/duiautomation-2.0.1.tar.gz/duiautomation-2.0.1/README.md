# DuiAutomation

### 介绍
基于Frida框架的Windows DuiLib的自动化框架。主要原理是通过frida实现注入，dump界面树，分析元素状态，提供元素操作。


### 安装教程

    pip install DuiAutomation -i https://pypi.qiyou.cn/simple

### Quick Start

----

#### 0x0 注意事项

***请注意以admin权限启动脚本或编译器***

***请注意以admin权限启动脚本或编译器***

***请注意以admin权限启动脚本或编译器***

----

#### 0x1 查找窗口

```python
from dui_automation.da import FridaDriver

dr = FridaDriver()
dr.attach("xxxx.exe")               # 附加程序
window = dr.find_window_hwnd(class_name="QeeYouMainWindow")      # 获取窗口句柄
```

#### 0x2 查找控件

```python
btn_control = window.find_control_by_name("xxxx_button")
```

#### 0x3 点击控件
```python
btn_control.click()
```

#### 0x4 设置文本
```python
from dui_automation.da import FridaDriver

dr = FridaDriver()
dr.spawn("<file_path_to_exe>")      # 启动注入程序
window = dr.find_window_hwnd(class_name="QeeYouMainWindow")      # 获取窗口句柄
edit_control = window.find_control_by_text("xxxxx")
edit_control.set_text("xxxxx")
```

----

### 基础组件

#### Driver(FridaDriver)
承载frida程序注入的驱动，支持两种模式 *`spawn`* 和 *`attach`*.
1. *`spawn`* : 在程序启动时注入，时机更早，hook更全面。
2. *`attach`* : 在程序运行时附加注入，更灵活。

#### Window
包含句柄的 *`单例`* 窗口对象，承载着操作、查找该窗口内元素的能力。


#### Control
Duilib中的控件，具有管理属性、状态的能力。

#### Watcher
监听器，当 *`Control`* 查找失败时触发并执行相应操作，并在一定时间范围(`Configurator`中定义)内轮询查找对应 *`Control`*。

#### <span id="configurator">Configurator</span>
定义 *`Window`* 和 *`Control`* 的轮询时间和查询间隔。
1. *`WAIT_FOR_CONTROL_POLL`* : 查询 *`Control`* 的轮询间隔时间。默认为1s。
2. *`WAIT_FOR_CONTROL_TIMEOUT`* : 查询 *`Control`* 的轮询超时时间。默认为10s。
3. *`WAIT_FOR_CONTROL_POLL`* : 查询 *`Window`* 的轮询间隔时间。默认为1s。
4. *`WAIT_FOR_WINDOW_TIMEOUT`* : 查询 *`Window`* 的轮询超时时间。默认为3s。
5. *`WAIT_FOR_WINDOW_ENABLE_POLL`* : 查询 *`Window`* 是否可用的轮询间隔时间。默认为1s。
6. *`WAIT_FOR_WINDOW_ENABLE_TIMEOUT`* : 查询 *`Window`* 是否可用的轮询超时时间。默认为10s。
----
### 常用API简述

#### 0x0 FridaDriver
1. *`spawn`* : 在程序启动时注入，时机更早，hook更全面。
2. *`attach`* : 在程序运行时附加注入，更灵活。
3. *`close`* : 关闭driver并清理注入环境。（注意，不会关闭客户端）
4. *`config`* : 全局配置，详见[Configurator](#configurator)。
----
#### 0x1 Window

*查找控件，原生函数*
1. *`find_root_control`* : 查找根节点控件。可选参数 `verbose` 控制是否冗余遍历，`True` 表示遍历所有根节点。默认为 `False`。
2. *`find_control_by_id`* : 由id查找控件。
3. *`find_control_by_name_native`* : 由name查找控件。原生函数，查找效率将更高。
4. *`find_control_by_point_native`* : 由point（位置）查找控件，参数为`x`，`y`坐标。原生函数，查找效率将更高。
5. *`find_subcontrol_by_name_native`* : 由父控件id和name查找子控件。原生函数，查找效率将更高。
6. *`find_subcontrol_by_class_native`* : 由父控件id和class查找子控件。原生函数，查找效率将更高。
7. *`find_subcontrol_by_point_native`* : 由父控件id和point（位置）查找子控件。原生函数，查找效率将更高。
8. *`find_subcontrols_by_class_native`* : 由父控件id和class查找所有子控件。原生函数，查找效率将更高。

> 注：优先使用原生函数定位，查找效率将大幅提升。


*查找控件，其他函数*
1. *`find_controls_by_jsonpath`* : 由`jsonpath`查找所有满足条件的控件。
2. *`find_control_by_jsonpath`* : 由`jsonpath`查找单个控件。参数`instance`决定查找的实例编号。
3. *`find_control_by_name`* : 由`name`查找单个控件。参数`instance`决定查找的实例编号。
4. *`find_control_by_text`* : 由`text`查找单个控件。参数`instance`决定查找的实例编号。
5. *`find_control_by_class`* : 由`class`查找单个控件。参数`instance`决定查找的实例编号。
6. *`find_control_by_tip`* : 由`tip`查找单个控件。参数`instance`决定查找的实例编号。
7. *`find_controls`* : 接收一个`Selector`或`By`&`value`的组合，返回满足条件的所有控件。
8. *`find_control`* : 接收一个`Selector`或`By`&`value`的组合，返回满足条件的单个控件。参数`instance`决定查找的实例编号。
9. *`dump`* : 以冗余模式dump所有当前窗口控件详细信息。

*查找子控件*
1. *`find_subcontrols_by_jsonpath`* : 由父控件id和`jsonpath`查找所有满足条件的控件。
2. *`find_subcontrol_by_jsonpath`* : 由父控件id和`jsonpath`查找满足条件的单个控件。参数`instance`决定查找的实例编号。
3. *`find_subcontrol_by_name`* : 由父控件id和`name`查找满足条件的单个控件。参数`instance`决定查找的实例编号。
4. *`find_subcontrol_by_text`* : 由父控件id和`text`查找满足条件的单个控件。参数`instance`决定查找的实例编号。
5. *`find_subcontrol_by_class`* : 由父控件id和`class`查找满足条件的单个控件。参数`instance`决定查找的实例编号。
6. *`find_subcontrols`* : 接收一个`Selector`或`By`&`value`的组合，从父控件开始查找，返回满足条件的所有控件。
7. *`find_subcontrol`* : 接收一个`Selector`或`By`&`value`的组合，从父控件开始查找，返回满足条件的单个控件。参数`instance`决定查找的实例编号。
8. *`exist`* : 接收一个`Selector`或`By`&`value`的组合，判断控件是否存在。（单次查找不触发轮询和`Watcher`）
9. *`wait_for_exist`* : 接收一个`Selector`或`By`&`value`的组合，在一定时间内查找控件，在控件查找失败后触发轮询和`Watcher`。

----

*Watcher*
1. *`register_watcher`* : 注册一个 `Watcher` ，详见[下方](#watcher_demo)示例。
2. *`remove_watcher`* : 删除一个 `Watcher` 。
3. *`run_watchers`* : 强制运行所有 `Watcher` 。
4. *`has_watcher_triggered`* : 检查某个 `Watcher` 是否被触发。
5. *`has_any_watcher_triggered`* : 是否有任何 `Watcher` 被触发。返回触发个数。

<span id="configurator">使用`Watcher`监听程序</span>

*一个最简单的watcher*
```python
from dui_automation.da import FridaDriver
from dui_automation.da import Watcher

class SampleWatcher(Watcher):

    def check_for_condition(self) -> bool:
        print("in sample watcher")
        return True

dr = FridaDriver()
dr.attach("xxxx.exe")                                               # 附加程序
some_window = dr.find_window_hwnd(class_name="SomeWindow")          # 获取窗口
sample_watcher = SampleWatcher()                                    # 定义watcher
dr.register_watcher(sample_watcher)

# 触发
some_window.find_control_by_name("some_control_can_not_be_found")
```
> 这将在`control`（名为*some_control_can_not_be_found*）未查找到时触发`watcher`，
> 并执行`watcher`中的`check_for_condition`函数，打印"*in sample watcher*"。

*当一个`controlA`被另一个`controlB`遮挡时，使用watcher关闭`controlB`*
```python
from dui_automation.da import FridaDriver
from dui_automation.da import Watcher
from dui_automation.da import Window

class CloseCtlBWatcher(Watcher):
    def __init__(self, window: Window):
        self.window = window

    def check_for_condition(self) -> bool:
        print("in close ctrlB watcher")
        self.window.find_control_by_name("control_B").click()
        return True

dr = FridaDriver()
dr.attach("xxxx.exe")                       # 附加程序
some_window = dr.find_window_hwnd(class_name="SomeWindow")         # 获取窗口句柄
    
close_ctrlB_watcher = CloseCtlBWatcher(some_window)

dr.register_watcher(close_ctrlB_watcher)

# 触发：此时`control_A`被`control_B`遮挡，无法定位。
control_A = some_window.find_control_by_name("control_A")
# 处理完`watcher`后，会再次回到主流程中并继续执行。
control_A.click()
```
>这将在`control_A`未查找成功时触发`watcher`，整个流程会是：
> `controlA`查找失败 -> 触发`watcher` -> `watcher`中查找`controlB` -> 关闭`controlB` -> 再次查找`controlA` -> 查找成功 -> 点击`control`A

`watcher`类中的逻辑无限制，你可以在其中操作`window`/`control`，或者请求一个接口、发送一个消息。但需要注意：
**在`watcher`中查找`control`和`window`，不再触发`watcher`，也无法在`watcher`中注册`watcher`**，
这也很好理解，否则`watcher`可能在不恰当的使用中触发死循环。

*在`window`查找失败时，触发`watcher`：`WindowA`被`WindowB`遮挡无法定位及操作，使用`watcher`关闭`WindowB`*
```python
from dui_automation.da import Watcher
from dui_automation.da import FridaDriver

class CloseWinBWatcher(Watcher):
    def __init__(self, driver: FridaDriver):
        self.driver = driver

    def check_for_condition(self) -> bool:
        print("in close WinB watcher")
        window_B = self.driver.find_window_hwnd("WindowB")
        if window_B:
            window_B.find_control_by_name("close_button").click()
        return True

dr = FridaDriver()
dr.attach("xxxx.exe")                       # 附加程序
    
close_winB_watcher = CloseWinBWatcher(dr)

dr.register_watcher(close_winB_watcher)

# 触发：此时`window_A`被`window_B`遮挡，无法定位。
window_A = dr.find_window_hwnd(class_name="WindowA")         # 获取窗口句柄
```

*在对`control`执行操作（如`click`/`set_text`）操作前，会对`window`是否`enabled`判断。如果为否（被另一个窗口遮挡）将触发`watcher`*
*下面是一个简单例子*
```python
from dui_automation.da import Watcher
from dui_automation.da import FridaDriver

class CloseWinBWatcher(Watcher):
    def __init__(self, driver: FridaDriver):
        self.driver = driver

    def check_for_condition(self) -> bool:
        print("in close WinB watcher")
        window_B = self.driver.find_window_hwnd("WindowB")
        if window_B:
            window_B.find_control_by_name("close_button").click()
        return True

dr = FridaDriver()
dr.attach("xxxx.exe")                       # 附加程序
    
close_winB_watcher = CloseWinBWatcher(dr)

dr.register_watcher(close_winB_watcher)

window_A = dr.find_window_hwnd(class_name="WindowA")         # 获取窗口句柄，此时`window_A`被`window_B`遮挡，但窗口存在。
control = window_A.find_control_by_name("control_A")

# 触发：此时`window_A`被`window_B`遮挡。
# `window_A`可以查找元素但`enabled`为`False`，`click`时将触发`watcher`。
control.click()
```

*`watcher`的清理:*
1. *`reset_self_watchers`* : 清理当前`driver`中的`watcher`。
2. *`reset_self_watcher_triggers`* : 清理当前`driver`中的`watcher`触发状态。
3. *`clean_watcher`* : 清理所有`driver`中的`watcher`和触发状态。
4. *`clean_self_watcher`* : 清理当前`driver`中的`watcher`和触发状态。
5. 使用`driver`中的*`close`*清理：`driver.clode()`，清理当前`driver`中的`watcher`和`watcher`触发状态。同时也将清理`driver`中注入的脚本。

*使用上下文管理自动清理`watcher`*
```python
from dui_automation.da import Watcher
from dui_automation.da import FridaDriver

class CloseWinBWatcher(Watcher):
    def __init__(self, driver: FridaDriver):
        self.driver = driver

    def check_for_condition(self) -> bool:
        print("in close WinB watcher")
        window_B = self.driver.find_window_hwnd("WindowB")
        if window_B:
            window_B.find_control_by_name("close_button").click()
        return True
    

with FridaDriver() as dr:
    dr.attach("QiYou.exe")
    watcher = CloseWinBWatcher(dr)
    dr.register_watcher(watcher)
    wind = dr.find_window_hwnd("QeeYouMainWindow", "奇游电竞加速器")

# 这将在`with`结束时自动清理当前`driver`中的`watcher`和`watcher`触发状态。同时也将清理`driver`中注入的脚本。
```

*手动清理*
```python
from dui_automation.da import Watcher
from dui_automation.da import FridaDriver

class CloseWinBWatcher(Watcher):
    def __init__(self, driver: FridaDriver):
        self.driver = driver

    def check_for_condition(self) -> bool:
        print("in close WinB watcher")
        window_B = self.driver.find_window_hwnd("WindowB")
        if window_B:
            window_B.find_control_by_name("close_button").click()
        return True
    

dr = FridaDriver()
dr.attach("QiYou.exe")
watcher = CloseWinBWatcher(dr)
dr.register_watcher(watcher)
wind = dr.find_window_hwnd("QeeYouMainWindow", "奇游电竞加速器")
dr.close()      # 这将清理当前`driver`中的`watcher`和`watcher`触发状态。同时也将清理`driver`中注入的脚本。
```

*动态管理watcher的清理（意味着不与`driver`的清理绑定）*
```python
from dui_automation.da import Watcher
from dui_automation.da import FridaDriver

class CloseWinBWatcher(Watcher):
    def __init__(self, driver: FridaDriver):
        self.driver = driver

    def check_for_condition(self) -> bool:
        print("in close WinB watcher")
        window_B = self.driver.find_window_hwnd("WindowB")
        if window_B:
            window_B.find_control_by_name("close_button").click()
        return True
    

dr = FridaDriver()
dr.attach("QiYou.exe")
watcher = CloseWinBWatcher(dr)
dr.register_watcher(watcher)
dr.clean_self_watcher()     # 这将清理当前`driver`中的`watcher`和`watcher`触发状态。
# dr.clean_watcher()          # 这将清理所有`driver`中的`watcher`和`watcher`触发状态。
```

> 综上，使用`watcher`的注意事项如下：
> 1. 注意区分触发时机：
>    1. `window`查找失败时触发。
>    2. `control`查找失败时触发。
>    3. `control`操作前，判断`window`是否`enabled`，否则触发`watcher`。
>    4. `control`操作前，判断`control`是否可访问（通过坐标查找元素，如果与该元素不一致，则判断为不可访问），否则触发`watcher`。
> 2. `watcher`只可在`driver`中管理，在`window`和`control`中可读。
> 3. `watcher`的工作流程：`window`查找失败/`control`查找失败/执行操作前`window`不可用（`enabled`为`False`） -> 触发`watcher` -> 执行`check_for_condition`函数 -> 回到主流程中继续执行。
> 4. `watcher`在查找失败时触发，触发后会在指定时间（`Configurator`中的`WAIT_FOR_WINDOW_TIMEOUT`/`WAIT_FOR_CONTROL_TIMEOUT`/`WAIT_FOR_WINDOW_ENABLE_POLL`）
> 内轮询执行，直到超时或`window`/`control`查找成功。
> 5. `watcher`中可以操作`window`/`control`，但不可以再次触发或注册`watcher`。
> 6. `watcher`可以同时注册多个，在`driver`和`window`层级中注册的`watcher`将会共享。意味着他们将同时执行，也会在`remove`时同时清理。
> 7. 不同`driver`中的`watcher`不会共享，。

----

#### 0x2 Control

1. *`set_visible`* : 设置控件可见。
2. *`set_focus`* : 设置控件聚焦。
3. *`set_enable`* : 设置控件可用。
4. *`click`* : 点击控件。关键字参数`on_main_thread`控制是否在主线程运行程序，某些情况下程序通过Windows消息通知进行交互，需要在主线程操作。默认为`True`。
5. *`set_text`* : 设置控件文本。关键字参数`on_main_thread`控制是否在主线程运行程序，某些情况下程序通过Windows消息通知进行交互，需要在主线程操作。默认为`True`。

----
#### 0x3 By 和 Selector

`By`
```python
from dui_automation.da import FridaDriver
from dui_automation.da.common.by import By


dr = FridaDriver()
dr.attach("xxxx.exe")                       # 附加程序
some_window = dr.find_window_hwnd(class_name="QeeYouMainWindow") 
some_window.find_controls(By.JSONPATH, "$..childs[?(@.text=='vpn IP')]")
```

**原生`By`**
1. *`NAT_ID`* : 由id查找控件。
2. *`NAT_NAME`* : 由name查找控件。
3. *`NAT_CLASS`* : 由class查找控件。
4. *`NAT_POINT`* : 由point（位置）查找控件，参数为`x`，`y`坐标。

*关于`By`中`Native`定位方式的特殊情况：*
1. 在`find_control`中仅支持`NAT_ID`,`NAT_NAME`,`NAT_POINT`。
2. 在`find_controls`中不支持`Native`定位方式，及`NAT_`开头的`By`。
3. 在`find_subcontrol`中仅支持`NAT_NAME`,`NAT_CLASS`,`NAT_POINT`。
4. 在`find_subcontrols`中仅支持`NAT_CLASS`。

> Tips：在`find_subcontrol`和`find_subcontrols`中使用`NAT_CLASS`是调用的不同的原生API。

**非原生`By`**
1. *`ID`* : 由id查找控件。
2. *`JSONPATH`* : 由`jsonpath`查找控件。
3. *`TEXT`* : 由`text`查找控件。
4. *`CLASS`* : 由`class`查找控件。
5. *`TIP`* : 由`tip`查找控件。
6. *`NAME`* : 由`name`查找控件。
7. *`HINT`* : 由`hint`查找控件。

> **非原生By（及不以`NAT_`开头的`By`）在以上定位方法中均支持。**


`Selector`
```python
from dui_automation.da import FridaDriver
from dui_automation.da.common.by import By
from dui_automation.da.common.selector import Selector


dr = FridaDriver()
dr.attach("xxxx.exe")                       # 附加程序
some_window = dr.find_window_hwnd(class_name="QeeYouMainWindow") 

selector = Selector(By.TEXT, "vpn IP")
some_window.wait_for_exist(selector)
```

> 注：在PO模式中，`Selector`将起到关键作用。

### 更多[API](http://cbstest.qeeyou.cn/DuiAutomation/index.html)

### 更新日志
- 0.1.6：新增`hint`属性和定位方式。
- 0.2.0：
  - 去除`window`单例限制。
  - 修复`set_enabled` Bug。
  - 新增`control`父控件属性：`parent`。
  - 修复`click`异常：旧版`click`改为`active`，新增`click`，按相对坐标点击。
  - 新增`window`和`control`坐标点击操作：`click_xy`。
  - 统一`window` RPC调用方式。
  - 一些Bug修复。
- 0.2.1：
  - 修复`find_subcontrol`返回值不是`Control`的Bug。
  - 新增`driver`层级`watcher`，用于处理`window`查找失败的情况。
- 0.2.2：
  - `driver`的`watcher`和`window`的`watcher`将共享，不再区分`watcher`类型。
  - 去除`watcher`基类初始化限制。
- 0.2.3：
  - 添加`watcher`触发时机：在对`control`执行操作前，判断`window`是否`enabled`，否则触发`watcher`。
  - 优化`watcher`管理流程：仅在`driver`中管理`watcher`，`window`和`control`可对`watcher`属性进行访问。
- 0.3.0:
  - 优化`selector`调用方式
  - 优化`watcher`
    - 为避免`driver`之间的`watcher`管理混乱，`driver`中注册的`watcher`现在相互独立，执行时只执行当前`driver`中的`watcher`。
    - 在`driver` `close`时，清理`watcher`。
    - 添加清理`watcher`方法：
      - `reset_self_watchers`清理当前`driver`中的`watcher`。
      - `reset_self_watcher_triggers`清理当前`driver`中的`watcher`触发状态。
      - `clean_watcher`清理所有`driver`中的`watcher`和触发状态。
      - `clean_self_watcher`清理当前`driver`中的`watcher`和触发状态。
- 0.3.1：
  - 新增`Selector`中`instance`属性
  - 优化所有*find control api*逻辑
- 0.3.2
  - 新增`watcher`触发条件：对`control`执行操作，但`control`不可访问时触发。
  - 优化`watcher`逻辑。
  - 优化`control`逻辑。
- 0.3.4
  - 修复定位逻辑。
- 0.3.5
  - 支持`IListUI`控件定位、属性获取。
- 0.3.6
  - 添加ListItemUI `Control`属性`index`（位于list中的第几个）、`selected`（在list中是否被选中）。
  - 添加IListOwner和TabLayout `Control`属性`selected_index`（被选中的列表项索引）。
  - 修复当`Control`没有子节点，`child_controls`的引用问题。
  - 添加`Control`方法`refresh`，用于刷新属性。
- 0.3.7
  - 增加键盘操作
    - window.press_key(Keycode.ENTER)  # 按下空格键（ENTER，BACKSPACE）
    - window.press_enter()  # 按下回车键
  - 增加鼠标操作
    - window.mouse_wheel(-100)  # 向下滚动100
    - window.mouse_wheel(100)  # 向上滚动100
    - window.mouse_wheel(-100, 400, 400)  # 在(400, 400)位置向下滚动100（400,400可以通过control.x,control.y获得）
    - control.hover()  # 鼠标移动到control的位置
- 0.3.8
  - 增加等待元素不可见方法wait_for_invisible
    - window.wait_for_invisible(control)
  - 增加等待元素可见方法wait_for_visible
    - window.wait_for_visible(control)
  - 增加判断元素是否可见方法is_visible（可见返回True，不可见返回False）
    - window.is_visible(control)
- 0.3.9
  - 添加`control`属性`bk_image`和`fore_image`，用于获取控件背景图和前景图。
