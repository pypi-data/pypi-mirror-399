# -*- coding:utf-8 -*-
# @FileName  :test_demo.py
# @Time      :2025/10/13 17:22
# @Author    :wangfei
import ctypes
from typing import ClassVar, List

import comtypes
import comtypes.client
import frida
from comtypes import GUID, IUnknown


def attach(target_process, js_script, callback=None):
    session = frida.attach(target_process)
    script = session.create_script(js_script)

    if callback:
        script.on("message", callback)
    script.load()
    script.post({"type": "dump", "payload": 0})


def spawn(target_exec_path, js_script, callback=None):
    pid = frida.spawn(target_exec_path)
    frida.resume(pid)
    session = frida.attach(pid)
    script = session.create_script(js_script)

    if callback:
        script.on("message", callback)
    script.load()
    script.post({"type": "dump", "payload": 0})


# 定义 UI Automation 相关 GUID 和接口
CLSID_CUIAutomationRegistrar = GUID("{6e29fabf-9977-42d1-8d0e-ca7e61ad87e6}")
IID_IUIAutomationRegistrar = GUID("{8609c4ec-4a1a-4d88-a357-5a66e060e1cf}")
CUSTOM_IsVisiblePropertyId_GUID = GUID("{bd2bceed-735d-475d-95d8-c18db79c6389}")


class UIAutomationPropertyInfo(ctypes.Structure):
    _fields_ = [
        ("guid", GUID),
        ("pProgrammaticName", ctypes.c_wchar_p),
        ("type", ctypes.c_ulong),
    ]


class UIAutomationEventInfo(ctypes.Structure):
    _fields_ = [
        ("guid", GUID),
        ("pProgrammaticName", ctypes.c_wchar_p),
        ("type", ctypes.c_ulong),
    ]


class UIAutomationPatternInfo(ctypes.Structure):
    _fields_ = [
        ("guid", GUID),
        ("pProgrammaticName", ctypes.c_wchar_p),
        ("providerInterfaceId", GUID),
        ("controlPatternInterfaceId", GUID),
        ("patternFlags", ctypes.c_uint),
    ]


# 定义 IUIAutomationRegistrar 接口
class IUIAutomationRegistrar(IUnknown):
    _iid_ = IID_IUIAutomationRegistrar
    _methods_: ClassVar[List["comtypes._ComMemberSpec"]] = [
        comtypes.STDMETHOD(
            comtypes.HRESULT,
            "RegisterProperty",
            [
                comtypes.POINTER(UIAutomationPropertyInfo),
                comtypes.POINTER(ctypes.c_ulong),
            ],
        ),
    ]


def register_custom_property(name: str, guid: GUID, prop_type: int):
    """
    注册自定义 UI Automation 属性
    返回注册的属性ID（成功）或 None（失败）
    """
    try:
        registrar = comtypes.client.CreateObject(
            CLSID_CUIAutomationRegistrar, interface=IUIAutomationRegistrar
        )
    except Exception as e:
        print(f"无法创建 Registrar 对象: {e}")
        return None

    prop_info = UIAutomationPropertyInfo()
    prop_info.guid = guid
    prop_info.pProgrammaticName = name
    prop_info.type = prop_type

    property_id = ctypes.c_ulong(0)

    # 传入结构体和输出参数的指针
    hr = registrar.RegisterProperty(ctypes.byref(prop_info), ctypes.byref(property_id))

    if hr == 0:  # S_OK
        print(f"成功注册属性 '{name}'，ID: {property_id.value}")
        return property_id.value
    else:
        print(f"注册属性失败，错误代码: 0x{hr:X}")
        return None


if __name__ == "__main__":
    CUSTOM_IsVisiblePropertyId = register_custom_property(
        "IsVisible", CUSTOM_IsVisiblePropertyId_GUID, 2
    )
    # element.GetPropertyValue(CUSTOM_IsVisiblePropertyId)
