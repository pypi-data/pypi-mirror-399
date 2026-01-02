
const ControlUIVirtualMethod = {
    // C
    CControlUI: 0,

    GetName: {
        index: 1,
        returnType: "pointer",
        // 返回值是CDuiString对象，需要传入一个CDuiString对象的指针
        // 详见 https://frida.re/docs/javascript-api/#nativefunction
        params: ["pointer", "pointer"],
        thisCall: true
    },
    SetName: {
        index: 2,
        returnType: "void",
        params: ["pointer", "pointer"],
        thisCall: true
    },
    GetClass: {
        index: 3,
        returnType: "pointer",
        params: ["pointer"],
        thisCall: true
    },
    GetInterface: {
        index: 4,
        returnType: "pointer",
        params: ["pointer", "pointer"],
        thisCall: true
    },
    GetControlFlags: {
        index: 5,
        returnType: "bool",
        params: ["pointer"],
        thisCall: true
    },
    Activate: {
        index: 6,
        returnType: "bool",
        params: ["pointer"],
        thisCall: true
    },
    GetManager: {
        index: 7,
        returnType: "pointer",
        params: ["pointer"],
        thisCall: true
    },
    SetManager: {
        index: 8,
        returnType: "void",
        params: ["pointer", "pointer", "bool"],
        thisCall: true
    },
    GetParent: {
        index: 9,
        returnType: "pointer",
        params: ["pointer"],
        thisCall: true
    },

    // 文本相关
    GetText: {
        index: 10,
        returnType: "pointer",
        // 返回值是CDuiString对象，需要传入一个CDuiString对象的指针
        // 详见 https://frida.re/docs/javascript-api/#nativefunction
        params: ["pointer", "pointer"],
        thisCall: true
    },
    SetText: {
        index: 11,
        returnType: "void",
        params: ["pointer", "pointer"],
        thisCall: true
    },
    IsResourceText: {
        index: 12,
        returnType: "bool",
        params: ["pointer"],
        thisCall: true
    },
    SetResourceText: {
        index: 13,
        returnType: "void",
        params: ["pointer", "bool"],
        thisCall: true
    },
    IsDragEnabled: {
        index: 14,
        returnType: "bool",
        params: ["pointer"],
        thisCall: true
    },
    SetDragEnable: {
        index: 15,
        returnType: "void",
        params: ["pointer", "bool"],
        thisCall: true
    },
    IsDropEnabled: {
        index: 16,
        returnType: "bool",
        params: ["pointer"],
        thisCall: true
    },
    SetDropEnable: {
        index: 17,
        returnType: "void",
        params: ["pointer", "bool"],
        thisCall: true
    },
    IsRichEvent: {
        index: 18,
        returnType: "bool",
        params: ["pointer"],
        thisCall: true
    },
    SetRichEvent: {
        index: 19,
        returnType: "void",
        params: ["pointer", "bool"],
        thisCall: true
    },
    SetBkImage: {
        index: 20,
    },      // 未找到

    // 位置相关
    GetRelativePos: {
        index: 21,
        returnType: "pointer",
        params: ["pointer"],
        thisCall: true
    },
    GetClientPos: {
        index: 22,
        returnType: "pointer",
        params: ["pointer"],
        thisCall: true
    },
    GetPos: {
        index: 23,
        returnType: "pointer",
        params: ["pointer"],
        thisCall: true
    },
    GetPaintPos: {
        index: 24,
    },    // 未找到
    SetPos: {
        index: 25,
        returnType: "void",
        params: ["pointer", "pointer", "bool"],
        thisCall: true
    },
    Move: {
        index: 26,
        returnType: "void",
        params: ["pointer", "pointer", "bool"],
        thisCall: true
    },
    GetWidth: {
        index: 27,
        returnType: "int",
        params: ["pointer"],
        thisCall: true
    },
    GetHeight: {
        index: 28,
        returnType: "int",
        params: ["pointer"],
        thisCall: true
    },
    GetX: {
        index: 29,
        returnType: "int",
        params: ["pointer"],
        thisCall: true
    },
    GetY: {
        index: 30,
        returnType: "int",
        params: ["pointer"],
        thisCall: true
    },
    GetPadding: {
        index: 31,
        returnType: "pointer",
        params: ["pointer", "pointer"],
        thisCall: true
    },
    SetPadding: {
        index: 32,
        returnType: "void",
        params: ["pointer", "pointer"],
        thisCall: true
    },
    GetFixedXY: {
        index: 33,
        returnType: "int",
        params: ["pointer"],
        thisCall: true
    },
    SetFixedXY: {
        index: 34,
        returnType: "void",
        params: ["pointer", "int"],
        thisCall: true
    },
    GetFixedSize: {
        index: 35,
        returnType: "int",
        params: ["pointer"],
        thisCall: true
    },
    GetFixedWidth: {
        index: 36,
        returnType: "int",
        params: ["pointer"],
        thisCall: true
    },
    SetFixedWidth: {
        index: 37,
        returnType: "void",
        params: ["pointer", "int"],
        thisCall: true
    },
    GetFixedHeight: {
        index: 38,
        returnType: "int",
        params: ["pointer"],
        thisCall: true
    },
    SetFixedHeight: {
        index: 39,
        returnType: "void",
        params: ["pointer", "int"],
        thisCall: true
    },
    GetMinWidth: {
        index: 40,
        returnType: "int",
        params: ["pointer"],
        thisCall: true
    },
    SetMinWidth: {
        index: 41,
        returnType: "void",
        params: ["pointer", "int"],
        thisCall: true
    },
    GetMaxWidth: {
        index: 42,
        returnType: "int",
        params: ["pointer"],
        thisCall: true
    },
    SetMaxWidth: {
        index: 43,
        returnType: "void",
        params: ["pointer", "int"],
        thisCall: true
    },
    GetMinHeight: {
        index: 44,
        returnType: "int",
        params: ["pointer"],
        thisCall: true
    },
    SetMinHeight: {
        index: 45,
        returnType: "void",
        params: ["pointer", "int"],
        thisCall: true
    },
    GetMaxHeight: {
        index: 46,
        returnType: "int",
        params: ["pointer"],
        thisCall: true
    },
    SetMaxHeight: {
        index: 47,
        returnType: "void",
        params: ["pointer", "int"],
        thisCall: true
    },
    GetFloatPercent: {
        index: 48,
        returnType: "pointer",
        params: ["pointer"],
        thisCall: true
    },
    SetFloatPercent: {
        index: 49,
        returnType: "void",
        params: ["pointer", "pointer"],
        thisCall: true
    },
    SetFloatAlign: {
        index: 50,
        returnType: "void",
        params: ["pointer", "pointer"],
        thisCall: true
    },
    GetFloatAlign: {
        index: 51,
        returnType: "pointer",
        params: ["pointer"],
        thisCall: true
    },

    // 鼠标提示
    GetToolTip: {
        index: 52,
        returnType: "pointer",
        // 返回值是CDuiString对象，需要传入一个CDuiString对象的指针
        // 详见 https://frida.re/docs/javascript-api/#nativefunction
        params: ["pointer", "pointer"],
        thisCall: true
    },
    SetToolTip: {
        index: 53,
        returnType: "void",
        params: ["pointer", "pointer"],
        thisCall: true
    },
    SetToolTipWidth: {
        index: 54,
        returnType: "void",
        params: ["pointer", "int"],
        thisCall: true
    },
    GetToolTipWidth: {
        index: 55,
        returnType: "int",
        params: ["pointer"],
        thisCall: true
    },

    // 光标
    GetCursor: {
        index: 56,
        returnType: "int16",
        params: ["pointer"],
        thisCall: true
    },
    SetCursor: {
        index: 57,
        returnType: "void",
        params: ["pointer", "int16"],
        thisCall: true
    },

    // 快捷键
    GetShortcut: {
        index: 58,
        returnType: "char",
        params: ["pointer"],
        thisCall: true
    },
    SetShortcut: {
        index: 59,
        returnType: "void",
        params: ["pointer", "char"],
        thisCall: true
    },

    // 菜单
    IsContextMenuUsed: {
        index: 60,
        returnType: "bool",
        params: ["pointer"],
        thisCall: true
    },
    SetContextMenuUsed: {
        index: 61,
        returnType: "void",
        params: ["pointer", "bool"],
        thisCall: true
    },

    // 用户属性
    GetUserData: {
        index: 62,
        returnType: "pointer",
        // 返回值是CDuiString对象，需要传入一个CDuiString对象的指针
        // 详见 https://frida.re/docs/javascript-api/#nativefunction
        params: ["pointer", "pointer"],
        thisCall: true
    },
    SetUserData: {
        index: 63,
        returnType: "void",
        params: ["pointer", "pointer"],
        thisCall: true
    },
    GetTag: {
        index: 64,
        returnType: "int",
        params: ["pointer"],
        thisCall: true
    },
    SetTag: {
        index: 65,
        returnType: "void",
        params: ["pointer", "int"],
        thisCall: true
    },

    // 一些重要的属性
    IsVisible: {
        index: 66,
        returnType: "bool",
        params: ["pointer"],
        thisCall: true
    },
    SetVisible: {
        index: 67,
        returnType: "void",
        params: ["pointer", "bool"],
        thisCall: true
    },
    SetInternVisible: {
        index: 68,
        returnType: "void",
        params: ["pointer", "bool"],
        thisCall: true
    },
    IsEnabled: {
        index: 69,
        returnType: "bool",
        params: ["pointer"],
        thisCall: true
    },
    SetEnabled: {
        index: 70,
        returnType: "void",
        params: ["pointer", "bool"],
        thisCall: true
    },
    IsMouseEnabled: {
        index: 71,
        returnType: "bool",
        params: ["pointer"],
        thisCall: true
    },
    SetMouseEnabled: {
        index: 72,
        returnType: "void",
        params: ["pointer", "bool"],
        thisCall: true
    },
    IsKeyboardEnabled: {
        index: 73,
        returnType: "bool",
        params: ["pointer"],
        thisCall: true
    },
    SetKeyboardEnabled: {
        index: 74,
        returnType: "void",
        params: ["pointer", "bool"],
        thisCall: true
    },
    IsFocused: {
        index: 75,
        returnType: "bool",
        params: ["pointer"],
        thisCall: true
    },
    SetFocus: {
        index: 76,
        returnType: "void",
        params: ["pointer"],
        thisCall: true
    },
    IsFloat: {
        index: 77,
        returnType: "bool",
        params: ["pointer"],
        thisCall: true
    },
    SetFloat: {
        index: 78,
        returnType: "void",
        params: ["pointer", "bool"],
        thisCall: true
    },

    FindControl: {
        index: 79,
        returnType: "pointer",
        params: ["pointer", "pointer", "int"],
        thisCall: true
    },

    Init: {
        index: 80,
        returnType: "void",
        params: ["pointer"],
        thisCall: true
    },
    DoInit: {
        index: 81,
        returnType: "void",
        params: ["pointer"],
        thisCall: true
    },
    Event: 82,
    DoEvent: 83,
    SetAttribute: 84,
    EstimateSize: 85,

    Paint: 86,
    DoPaint: 87,
    PaintBkColor: 88,
    PaintBkImage: 89,
    PaintStatusImage: 90,
    PaintForeColor: 91,
    PaintForeImage: 92,
    PaintText: 93,
    PaintBorder: 94,
    DoPostPaint: 95,

    // **** Container **** //
    GetInset: 96,
    SetInset: 97,
    GetChildPadding: 98,
    SetChildPadding: 99,
    GetChildAlign: 100,
    SetChildAlign: 101,
    GetChildVAlign: 102,
    SetChildVAlign: 103,
    IsAutoDestroy: 104,
    SetAutoDestroy: 105,
    IsDelayedDestroy: 106,
    SetDelayedDestroy: 107,
    IsMouseChildEnabled: 108,
    SetMouseChildEnabled: 109,
    FindSelectable: 110,
    GetScrollPos: 111,
    GetScrollRange: 112,
    SetScrollPos: {
        index: 113,
        returnType: "void",
        params: ["pointer", "bool"],
        thisCall: true
    },
    SetScrollStepSize: {
        index: 114,
        returnType: "void",
        params: ["pointer", "int"],
        thisCall: true
    },
    GetScrollStepSize: {
        index: 115,
        returnType: "int",
        params: ["pointer"],
        thisCall: true
    },
    LineUp: 116,
    LineDown: 117,
    PageUp: 118,
    PageDown: 119,
    HomeUp: 120,
    EndDown: 121,
    LineLeft: 122,
    LineRight: 123,
    PageLeft: 124,
    PageRight: 125,
    HomeLeft: 126,
    EndRight: 127,
    EnableScrollBar: 128,
    GetVerticalScrollBar: 129,
    GetHorizontalScrollBar: 130,
    SetFloatPos: 131,
    ProcessScrollBar: 132,
}

const IContainerUIVirtualMethod = {
    GetItemAt: {
        index: 0,
        returnType: "pointer",
        params: ["pointer", "int"],
        thisCall: true
    },
    GetItemIndex: 1,
    SetItemIndex: 2,
    GetCount: {
        index: 3,
        returnType: "int",
        params: ["pointer"],
        thisCall: true
    },
    Add: 4,
    AddAt: 5,
    Remove: 6,
    RemoveAt: 7,
    RemoveAll: 8,
}

const IListItemUIVirtualMethod = {
    GetIndex: {
        index: 0,
        returnType: "int",
        params: ["pointer"],
        thisCall: true
    },
    SetIndex: 1,
    GetOwner: 2,
    SetOwner: 3,
    IsSelected: {
        index: 4,
        returnType: "bool",
        params: ["pointer"],
        thisCall: true
    },
    Select: 5,
    SelectMulti: 6,
    IsExpanded: 7,
    Expand: 8,
    DrawItemText: 9,
}

const IListOwnerUIVirtualMethod = {
    GetListType: 0,
    GetListInfo: 1,
    GetCurSel: {
        index: 2,
        returnType: "int",
        params: ["pointer"],
        thisCall: true
    },
    SelectItem: {
        index: 3,
        returnType: "bool",
        params: ["pointer", "int", "bool"],
        thisCall: true
    },
    SelectMultiItem: {
        index: 4,
        returnType: "bool",
        params: ["pointer", "int", "bool"],
        thisCall: true
    },
    UnSelectItem: {
        index: 5,
        returnType: "bool",
        params: ["pointer", "int", "bool"],
        thisCall: true
    },
    DoEvent: 6,
}

const invokeControlUIVirtualMethod = (thisControlUIPtr, methodName) => {
    let vTablePtr = ptr(thisControlUIPtr).readPointer()
    let vMethod = vTablePtr.add(ControlUIVirtualMethod[methodName].index * Process.pointerSize).readPointer()
    if (ControlUIVirtualMethod[methodName].thisCall) {
        return new NativeFunction(
            vMethod,
            ControlUIVirtualMethod[methodName].returnType,
            ControlUIVirtualMethod[methodName].params,
            "thiscall"
        )
    }
    else {
        return new NativeFunction(
            vMethod,
            ControlUIVirtualMethod[methodName].returnType,
            ControlUIVirtualMethod[methodName].params
        )
    }
}

const invokeIContainerUIVirtualMethod = (thisControlUIPtr, methodName) => {

    let vTablePtr = ptr(thisControlUIPtr).readPointer()
    let vMethod = vTablePtr.add(IContainerUIVirtualMethod[methodName].index * Process.pointerSize).readPointer()
    if (IContainerUIVirtualMethod[methodName].thisCall) {
        return new NativeFunction(
            vMethod,
            IContainerUIVirtualMethod[methodName].returnType,
            IContainerUIVirtualMethod[methodName].params,
            "thiscall"
        )
    }
    else {
        return new NativeFunction(
            vMethod,
            IContainerUIVirtualMethod[methodName].returnType,
            IContainerUIVirtualMethod[methodName].params
        )
    }
}

const invokeIListItemUIVirtualMethod = (thisControlUIPtr, methodName) => {
    let vTablePtr = ptr(thisControlUIPtr).readPointer()
    let vMethod = vTablePtr.add(IListItemUIVirtualMethod[methodName].index * Process.pointerSize).readPointer()
    if (IListItemUIVirtualMethod[methodName].thisCall) {
        return new NativeFunction(
            vMethod,
            IListItemUIVirtualMethod[methodName].returnType,
            IListItemUIVirtualMethod[methodName].params,
            "thiscall"
        )
    }
    else {
        return new NativeFunction(
            vMethod,
            IListItemUIVirtualMethod[methodName].returnType,
            IListItemUIVirtualMethod[methodName].params
        )
    }
}

const invokeIListOwnerUIVirtualMethod = (thisControlUIPtr, methodName) => {
    let vTablePtr = ptr(thisControlUIPtr).readPointer()
    let vMethod = vTablePtr.add(IListOwnerUIVirtualMethod[methodName].index * Process.pointerSize).readPointer()
    if (IListOwnerUIVirtualMethod[methodName].thisCall) {
        return new NativeFunction(
            vMethod,
            IListOwnerUIVirtualMethod[methodName].returnType,
            IListOwnerUIVirtualMethod[methodName].params,
            "thiscall"
        )
    }
    else {
        return new NativeFunction(
            vMethod,
            IListOwnerUIVirtualMethod[methodName].returnType,
            IListOwnerUIVirtualMethod[methodName].params
        )
    }
}

// ****** ControlUI虚拟方法API列表 ****** //
// 1
const GetName = (thisControlUIPtr) => {
    // 返回值是CDuiString对象，需要传入一个CDuiString对象的指针
    // 详见 https://frida.re/docs/javascript-api/#nativefunction
    let funcGetName = invokeControlUIVirtualMethod(thisControlUIPtr, "GetName")
    let cDuiStringPtr = Memory.alloc(132)   // 132是CDuiString对象的大小
    let controlNamePtr = funcGetName(thisControlUIPtr, cDuiStringPtr)
    return controlNamePtr.readPointer().readUtf16String()
}

// 3
const GetClass = (thisControlUIPtr) => {
    let funcGetClass = invokeControlUIVirtualMethod(thisControlUIPtr, "GetClass")
    return funcGetClass(thisControlUIPtr).readUtf16String()
}


// 4, 返回值是Container对象的指针
const GetInterface = (thisControlUIPtr, sName) => {
    let strName = Memory.allocUtf16String(sName)
    let funcGetInterface = invokeControlUIVirtualMethod(thisControlUIPtr, "GetInterface")
    return funcGetInterface(thisControlUIPtr, strName)
}

// 6, 返回bool
const Activate = (thisControlUIPtr) => {
    let funcActivate = invokeControlUIVirtualMethod(thisControlUIPtr, "Activate")
    return funcActivate(thisControlUIPtr)
}

// 9, 返回CControlUI对象的指针
const GetParent = (thisControlUIPtr) => {
    let funcGetParent = invokeControlUIVirtualMethod(thisControlUIPtr, "GetParent")
    return funcGetParent(thisControlUIPtr)
}

// 10
const GetText = (thisControlUIPtr) => {
    // 返回值是CDuiString对象，需要传入一个CDuiString对象的指针
    // 详见 https://frida.re/docs/javascript-api/#nativefunction
    let funcGetText = invokeControlUIVirtualMethod(thisControlUIPtr, "GetText")
    let cDuiStringPtr = Memory.alloc(132)   // 132是CDuiString对象的大小
    let textPtr = funcGetText(thisControlUIPtr, cDuiStringPtr)
    return textPtr.readPointer().readUtf16String()
}

// 11
const SetText = (thisControlUIPtr, sText) => {
    let funcSetText = invokeControlUIVirtualMethod(thisControlUIPtr, "SetText")
    let textPtr = Memory.allocUtf16String(sText)
    return funcSetText(thisControlUIPtr, textPtr)
}

// 23
const GetPos = (thisControlUIPtr) => {
    let funcGetPos = invokeControlUIVirtualMethod(thisControlUIPtr, "GetPos")
    let rectPtr = funcGetPos(thisControlUIPtr)
    let left = rectPtr.readUInt()
    let top = rectPtr.add(4).readUInt()
    let right = rectPtr.add(8).readUInt()
    let bottom = rectPtr.add(12).readUInt()
    return [left, top, right, bottom]
}

// 27
const GetWidth = (thisControlUIPtr) => {
    let funcGetWidth = invokeControlUIVirtualMethod(thisControlUIPtr, "GetWidth")
    return funcGetWidth(thisControlUIPtr)
}

// 28
const GetHeight = (thisControlUIPtr) => {
    let funcGetHeight = invokeControlUIVirtualMethod(thisControlUIPtr, "GetHeight")
    return funcGetHeight(thisControlUIPtr)
}

// 29
const GetX = (thisControlUIPtr) => {
    let funcGetX = invokeControlUIVirtualMethod(thisControlUIPtr, "GetX")
    return funcGetX(thisControlUIPtr)
}

// 30
const GetY = (thisControlUIPtr) => {
    let funcGetY = invokeControlUIVirtualMethod(thisControlUIPtr, "GetY")
    return funcGetY(thisControlUIPtr)
}

// 31
const GetPadding = (thisControlUIPtr) => {
    let funcGetPadding = invokeControlUIVirtualMethod(thisControlUIPtr, "GetPadding")
    let cRECT = Memory.alloc(16)   // 16是RECT对象的大小
    let rectPtr = funcGetPadding(thisControlUIPtr, cRECT)
    let left = rectPtr.readUInt()
    let top = rectPtr.add(4).readUInt()
    let right = rectPtr.add(8).readUInt()
    let bottom = rectPtr.add(12).readUInt()
    return [left, top, right, bottom]
}

// 52
const GetToolTip = (thisControlUIPtr) => {
    let funcGetToolTip = invokeControlUIVirtualMethod(thisControlUIPtr, "GetToolTip")
    let cDuiStringPtr = Memory.alloc(132)   // 132是CDuiString对象的大小
    let toolTipPtr = funcGetToolTip(thisControlUIPtr, cDuiStringPtr)
    return toolTipPtr.readPointer().readUtf16String()
}

// 55
const GetToolTipWidth = (thisControlUIPtr) => {
    let funcGetToolTipWidth = invokeControlUIVirtualMethod(thisControlUIPtr, "GetToolTipWidth")
    return funcGetToolTipWidth(thisControlUIPtr)
}

// 66
const IsVisible = (thisControlUIPtr) => {
    let funcIsVisible = invokeControlUIVirtualMethod(thisControlUIPtr, "IsVisible")
    return funcIsVisible(thisControlUIPtr)
}

// 67
const SetVisible = (thisControlUIPtr, bVisible) => {
    let funcSetVisible = invokeControlUIVirtualMethod(thisControlUIPtr, "SetVisible")
    return funcSetVisible(thisControlUIPtr, bVisible ? 1 : 0)
}

// 69
const IsEnabled = (thisControlUIPtr) => {
    let funcIsEnabled = invokeControlUIVirtualMethod(thisControlUIPtr, "IsEnabled")
    return funcIsEnabled(thisControlUIPtr)
}

// 70
const SetEnabled = (thisControlUIPtr, bEnabled) => {
    let funcSetEnabled = invokeControlUIVirtualMethod(thisControlUIPtr, "SetEnabled")
    let intEnabled = bEnabled ? 1 : 0
    return funcSetEnabled(thisControlUIPtr, intEnabled)
}

// 71
const IsMouseEnabled = (thisControlUIPtr) => {
    let funcIsMouseEnabled = invokeControlUIVirtualMethod(thisControlUIPtr, "IsMouseEnabled")
    return funcIsMouseEnabled(thisControlUIPtr)
}

// 75
const IsFocused = (thisControlUIPtr) => {
    let funcIsFocused = invokeControlUIVirtualMethod(thisControlUIPtr, "IsFocused")
    return funcIsFocused(thisControlUIPtr)
}

// 76
const SetFocus = (thisControlUIPtr) => {
    let funcSetFocus = invokeControlUIVirtualMethod(thisControlUIPtr, "SetFocus")
    return funcSetFocus(thisControlUIPtr)
}

// 113
const SetScrollPos = (thisControlUIPtr, iScrollX, iScrollY, bMsg) => {
    let funcSetScrollPos = invokeControlUIVirtualMethod(thisControlUIPtr, "SetScrollPos")
    let pScrollPos = Memory.alloc(8)
    pScrollPos.writeUInt(iScrollX)
    pScrollPos.add(4).writeUInt(iScrollY)
    return funcSetScrollPos(thisControlUIPtr, pScrollPos, bMsg)
}

// 114
const SetScrollStepSize = (thisControlUIPtr, iSize) => {
    let funcSetScrollStepSize = invokeControlUIVirtualMethod(thisControlUIPtr, "SetScrollStepSize")
    return funcSetScrollStepSize(thisControlUIPtr, iSize)
}

// 115
const GetScrollStepSize = (thisControlUIPtr) => {
    let funcGetScrollStepSize = invokeControlUIVirtualMethod(thisControlUIPtr, "GetScrollStepSize")
    return funcGetScrollStepSize(thisControlUIPtr)
}

// **** 以下是IContainerUI的方法, 需要先通过GetInterface获取到IContainerUI地址 **** //
// 134
const GetItemAt = (thisContainerUIPtr, iIndex) => {
    let funcGetItemAt = invokeIContainerUIVirtualMethod(thisContainerUIPtr, "GetItemAt")
    return funcGetItemAt(thisContainerUIPtr, iIndex)
}

// 135
const GetItemIndex = (thisContainerUIPtr, pControlUIPtr) => {
    let funcGetItemIndex = invokeIContainerUIVirtualMethod(thisContainerUIPtr, "GetItemIndex")
    return funcGetItemIndex(thisContainerUIPtr, pControlUIPtr)
}

// 137
const GetCount = (thisContainerUIPtr) => {
    let funcGetCount = invokeIContainerUIVirtualMethod(thisContainerUIPtr, "GetCount")
    return funcGetCount(thisContainerUIPtr)
}

// GetBkImage
const GetBkImage = (thisControlUIPtr) => {
    // 返回值是CDuiString对象，需要传入一个CDuiString对象的指针
    // 详见 https://frida.re/docs/javascript-api/#nativefunction
    let funcGetBkImage = new NativeFunction(
        Module.findExportByName(
            "DuiLib.dll", "?GetBkImage@CControlUI@DuiLib@@QAEPB_WXZ"
        ),
        "pointer",
        ["pointer", "pointer"],
        'thiscall'
    )
    let cDuiStringPtr = Memory.alloc(132)   // 132是CDuiString对象的大小
    let controlBkImagePtr = funcGetBkImage(thisControlUIPtr, cDuiStringPtr)
    return controlBkImagePtr.readUtf16String()
}

// GetForeImage
const GetForeImage = (thisControlUIPtr) => {
    // 返回值是CDuiString对象，需要传入一个CDuiString对象的指针
    // 详见 https://frida.re/docs/javascript-api/#nativefunction
    let funcGetForeImage = new NativeFunction(
        Module.findExportByName(
            "DuiLib.dll", "?GetForeImage@CControlUI@DuiLib@@QBEPB_WXZ"
        ),
        "pointer",
        ["pointer", "pointer"],
        'thiscall'
    )
    let cDuiStringPtr = Memory.alloc(132)   // 132是CDuiString对象的大小
    let controlForeImagePtr = funcGetForeImage(thisControlUIPtr, cDuiStringPtr)
    return controlForeImagePtr.readUtf16String()
}


// **** 以下是IListItemUI的方法, 需要先通过GetInterface获取到IListItemUI地址 **** //
const GetIndex = (thisListItemUIPtr) => {
    let funcGetIndex = invokeIListItemUIVirtualMethod(thisListItemUIPtr, "GetIndex")
    return funcGetIndex(thisListItemUIPtr)
}

const IsSelected = (thisListItemUIPtr) => {
    let funcIsSelected = invokeIListItemUIVirtualMethod(thisListItemUIPtr, "IsSelected")
    return funcIsSelected(thisListItemUIPtr)
}

// **** OptionUI **** //
const IsSelectedOptionUI = (pOptionUIPtr) => {
    let funcIsSelectedOptionUI = new NativeFunction(
        Module.findExportByName(
            "DuiLib.dll", "?IsSelected@COptionUI@DuiLib@@QBE_NXZ"
        ),
        "bool",
        ["pointer"],
        'thiscall'
    )
    return funcIsSelectedOptionUI(pOptionUIPtr)
}

const GetCurSel = (pListOwnerUIPtr) => {
    let funcGetCurSel = invokeIListOwnerUIVirtualMethod(pListOwnerUIPtr, "GetCurSel")
    return funcGetCurSel(pListOwnerUIPtr)
}

const GetCurSelTabLayoutUI = (pListOwnerUIPtr) => {
    let funcGetCurSelTabLayoutUI = new NativeFunction(
        Module.findExportByName(
            "DuiLib.dll", "?GetCurSel@CTabLayoutUI@DuiLib@@QBEHXZ"
        ),
        "bool",
        ["pointer"],
        'thiscall'
    )
    return funcGetCurSelTabLayoutUI(pListOwnerUIPtr)
}

// ****** CStdPtrArray API ****** //
// 获取CStdPtrArray长度
const getSizeFromCStdPtrArray = (cStdPtrArrayPtr) => {
    let funcGetSize = new NativeFunction(
        Module.findExportByName(
            "DuiLib.dll", "?GetSize@CStdPtrArray@DuiLib@@QBEHXZ"
        ),
        "int",
        ["pointer"],
        'thiscall'
    )
    return funcGetSize(cStdPtrArrayPtr)
}

// 获取CStdPtrArray指定索引的元素
const getAtFromCStdPtrArray = (cStdPtrArrayPtr, index) => {
    let funcGetAt = new NativeFunction(
        Module.findExportByName(
            "DuiLib.dll", "?GetAt@CStdPtrArray@DuiLib@@QBEPAXH@Z"
        ),
        "pointer",
        ["pointer", "int"],
        'thiscall'
    )
    return funcGetAt(cStdPtrArrayPtr, index)
}

// 获取EditUI的TipValue
const getTipValueFromEditUI = (pEditUIPtr) => {
    let funcGetTipValue = new NativeFunction(
        Module.findExportByName(
            "DuiLib.dll", "?GetTipValue@CEditUI@DuiLib@@QAEPB_WXZ"
        ),
        "pointer",
        ["pointer"],
        'thiscall'
    )
    return funcGetTipValue(pEditUIPtr).readUtf16String()
}

// 获取RichEditUI的TipValue
const getTipValueFromRichEditUI = (pRichEditUIPtr) => {
    let funcGetTipValue = new NativeFunction(
        Module.findExportByName(
            "DuiLib.dll", "?GetTipValue@CRichEditUI@DuiLib@@QAEPB_WXZ"
        ),
        "pointer",
        ["pointer"],
        'thiscall'
    )
    return funcGetTipValue(pRichEditUIPtr).readUtf16String()
}

// 获取ListUI的Headers
const getHeadersFromListUI = (pListUIPtr) => {
    let funcGetHeaders = new NativeFunction(
        Module.findExportByName(
            "DuiLib.dll", "?GetHeader@CListUI@DuiLib@@UBEPAVCListHeaderUI@2@XZ"
        ),
        "pointer",
        ["pointer"],
        'thiscall'
    )
    return funcGetHeaders(pListUIPtr)
}


// ****** 一些内部方法 ****** //
// 通过指针获取control属性
const enumControlAttribute = (pControlUiPtr) => {
    return {
        name: GetName(pControlUiPtr),
        class: GetClass(pControlUiPtr),
        text: GetText(pControlUiPtr),
        pos: GetPos(pControlUiPtr),
        width: GetWidth(pControlUiPtr),
        height: GetHeight(pControlUiPtr),
        x: GetX(pControlUiPtr),
        y: GetY(pControlUiPtr),
        padding: GetPadding(pControlUiPtr),
        toolTip: GetToolTip(pControlUiPtr),
        toolTipWidth: GetToolTipWidth(pControlUiPtr),
        visible: IsVisible(pControlUiPtr),
        enabled: IsEnabled(pControlUiPtr),
        mouseEnabled: IsMouseEnabled(pControlUiPtr),
        focused: IsFocused(pControlUiPtr),
        bkImage: GetBkImage(pControlUiPtr),
        foreImage: GetForeImage(pControlUiPtr),
    }
}

// 通过指针获取container属性
const enumIContainerAttribute = (pContainerPtr) => {
    return {
        // name: GetName(pControlUiPtr),
        // class: GetClass(pControlUiPtr),
        // text: GetText(pControlUiPtr),
        // pos: GetPos(pControlUiPtr),
        // width: GetWidth(pControlUiPtr),
        // height: GetHeight(pControlUiPtr),
        // x: GetX(pControlUiPtr),
        // y: GetY(pControlUiPtr),
        // padding: GetPadding(pControlUiPtr),
        // toolTip: GetToolTip(pControlUiPtr),
        // toolTipWidth: GetToolTipWidth(pControlUiPtr),
        // visible: IsVisible(pControlUiPtr),
        // enabled: IsEnabled(pControlUiPtr),
        // mouseEnabled: IsMouseEnabled(pControlUiPtr),
        // focused: IsFocused(pControlUiPtr),
        // scrollStepSize: GetScrollStepSize(pControlUiPtr),

        // IContainerUI，需要用container的地址获取
        childCount: GetCount(pContainerPtr),
    }
}

// 通过指针获取EditUI属性
const enumEditUIAttribute = (pEditUIPtr) => {
    return {
        // name: GetName(pEditUIPtr),
        // class: GetClass(pEditUIPtr),
        // text: GetText(pEditUIPtr),
        // pos: GetPos(pEditUIPtr),
        // width: GetWidth(pEditUIPtr),
        // height: GetHeight(pEditUIPtr),
        // x: GetX(pEditUIPtr),
        // y: GetY(pEditUIPtr),
        // padding: GetPadding(pEditUIPtr),
        // toolTip: GetToolTip(pEditUIPtr),
        // toolTipWidth: GetToolTipWidth(pEditUIPtr),
        // visible: IsVisible(pEditUIPtr),
        // enabled: IsEnabled(pEditUIPtr),
        // mouseEnabled: IsMouseEnabled(pEditUIPtr),
        // focused: IsFocused(pEditUIPtr),

        // EditUI，需要用editUI的地址获取
        hint: getTipValueFromEditUI(pEditUIPtr),
    }
}

// 通过指针获取RichEditUI属性
const enumRichEditUIAttribute = (pRichEditUIPtr) => {
    return {
        // name: GetName(pRichEditUIPtr),
        // class: GetClass(pRichEditUIPtr),
        // text: GetText(pRichEditUIPtr),
        // pos: GetPos(pRichEditUIPtr),
        // width: GetWidth(pRichEditUIPtr),
        // height: GetHeight(pRichEditUIPtr),
        // x: GetX(pRichEditUIPtr),
        // y: GetY(pRichEditUIPtr),
        // padding: GetPadding(pRichEditUIPtr),
        // toolTip: GetToolTip(pRichEditUIPtr),
        // toolTipWidth: GetToolTipWidth(pRichEditUIPtr),
        // visible: IsVisible(pRichEditUIPtr),
        // enabled: IsEnabled(pRichEditUIPtr),
        // focused: IsFocused(pRichEditUIPtr),

        // RichEditUI，需要用richEditUI的地址获取
        hint: getTipValueFromRichEditUI(pRichEditUIPtr),
    }
}

// 通过指针获取ListOwnerUI属性
const enumListOwnerUIAttribute = (pListOwnerUIPtr) => {
    return {
        selectedIndex: GetCurSel(pListOwnerUIPtr),
    }
}

// 通过指针获取TabLayoutUI属性
const enumTabLayoutUIAttribute = (pTabLayoutUIPtr) => {
    return {
        selectedIndex: GetCurSelTabLayoutUI(pTabLayoutUIPtr),
    }
}

// 通过指针获取ListItemUI属性
const enumListUIAttribute = (pListUIPtr) => {
    return {
        index: GetIndex(pListUIPtr),
        isSelected: IsSelected(pListUIPtr),
    }
}

// 通过指针获取OptionUI属性
const enumOptionUIAttribute = (pOptionUIPtr) => {
    return {
        isSelected: IsSelectedOptionUI(pOptionUIPtr),
    }
}

// 通过指针获取ListUI属性
const getHeaderControlsFromListUI = (pListUIPtr, bVerbose) => {
    let pIListOwner = GetInterface(pListUIPtr, "IListOwner")
    let headerContainer = getHeadersFromListUI(pIListOwner)
    let iContainerPtr = GetInterface(headerContainer, "IContainer")

    let containerAttribute = enumIContainerAttribute(iContainerPtr)

    return getChildControlsFromContainer(iContainerPtr, containerAttribute.childCount, bVerbose)
}

// 通过指针获取Container的子控件
const getChildControlsFromContainer = (pContainerPtr, childCount, bVerbose) => {
    let childControls = []
    for (let i = 0; i < childCount; i++) {
        let childControlPtr = GetItemAt(pContainerPtr, i)
        if (bVerbose) {
            childControls.push(getControlAttributeByPtr(childControlPtr, bVerbose))
        }
        else {
            childControls.push(parseInt(childControlPtr))
        }
    }
    return childControls
}

// 通过controlUiPtr获取control属性
const getControlAttributeByPtr = (pControlPtr, bVerbose = false) => {
    if (parseInt(pControlPtr) <= 0) {
        return {}
    }

    // 先获取ControlUI的通用属性
    let controlAttribute = enumControlAttribute(pControlPtr)
    controlAttribute.id = parseInt(pControlPtr)
    let iContainerPtr = GetInterface(pControlPtr, "IContainer")
    let pEditUIPtr = GetInterface(pControlPtr, "Edit")
    let pRichEditUIPtr = GetInterface(pControlPtr, "RichEdit")
    let pListUIPtr = GetInterface(pControlPtr, "List")
    let pListItemUIPtr = GetInterface(pControlPtr, "ListItem")
    let pOptionUIPtr = GetInterface(pControlPtr, "Option")
    let pListOwnerPtr = GetInterface(pControlPtr, "IListOwner")
    let pTabLayoutPtr = GetInterface(pControlPtr, "TabLayout")

    if (iContainerPtr > 0) {
        let containerAttribute = enumIContainerAttribute(iContainerPtr)
        containerAttribute.childControls = getChildControlsFromContainer(
            iContainerPtr,
            containerAttribute.childCount,
            bVerbose
        )
        Object.assign(controlAttribute, containerAttribute)     // 合并属性
    }

    if (pEditUIPtr > 0) {
        let editUIAttribute = enumEditUIAttribute(pEditUIPtr)
        Object.assign(controlAttribute, editUIAttribute)        // 合并属性
    }

    if (pRichEditUIPtr > 0) {
        let richEditUIAttribute = enumRichEditUIAttribute(pRichEditUIPtr)
        Object.assign(controlAttribute, richEditUIAttribute)    // 合并属性
    }

    if (pListUIPtr > 0) {
        controlAttribute.headers = getHeaderControlsFromListUI(pListUIPtr, bVerbose)
    }

    if (pListItemUIPtr > 0) {
        let listItemAttribute = enumListUIAttribute(pListItemUIPtr)
        Object.assign(controlAttribute, listItemAttribute)     // 合并属性
    }

    if (pOptionUIPtr > 0) {
        let optionUIAttribute = enumOptionUIAttribute(pOptionUIPtr)
        Object.assign(controlAttribute, optionUIAttribute)     // 合并属性
    }

    if (pListOwnerPtr > 0) {
        let listOwnerAttribute = enumListOwnerUIAttribute(pListOwnerPtr)
        Object.assign(controlAttribute, listOwnerAttribute)     // 合并属性
    }

    if (pTabLayoutPtr > 0) {
        let tabLayoutAttribute = enumTabLayoutUIAttribute(pTabLayoutPtr)
        Object.assign(controlAttribute, tabLayoutAttribute)     // 合并属性
    }

    return controlAttribute

    // if (pListUIPtr > 0) {
    //     console.log(iContainerPtr, pEditUIPtr, pRichEditUIPtr, pListUIPtr)
    // }
    // if (pEditUIPtr > 0) {
    //     let editUIAttribute = enumEditUIAttribute(pEditUIPtr)
    //     editUIAttribute.id = parseInt(pControlPtr)
    //     // EditUI，默认继承自IContainerUI，所以也有childCount属性
    //     if (parseInt(iContainerPtr) > 0) {
    //         editUIAttribute.childCount = GetCount(iContainerPtr)
    //         editUIAttribute.childControls = getChildControlsFromContainer(
    //             iContainerPtr,
    //             editUIAttribute.childCount,
    //             bVerbose
    //         )
    //     }
    //     return editUIAttribute
    // }
    // else if (pRichEditUIPtr > 0) {
    //     let richEditUIAttribute = enumRichEditUIAttribute(pRichEditUIPtr)
    //     richEditUIAttribute.id = parseInt(pControlPtr)
    //
    //     // RichEditUI，默认继承自IContainerUI，所以也有childCount属性
    //     if (parseInt(iContainerPtr) > 0) {
    //         richEditUIAttribute.childCount = GetCount(iContainerPtr)
    //         richEditUIAttribute.childControls = getChildControlsFromContainer(
    //             iContainerPtr,
    //             richEditUIAttribute.childCount,
    //             bVerbose
    //         )
    //     }
    //     return richEditUIAttribute
    // }
    // else if (pListUIPtr > 0) {
    //     let dll = Module.load("DuiLib.dll")
    //     let ep = dll.enumerateExports()
    //     for (let i = 0; i < ep.length; i++) {
    //         console.log(ep[i].name, ep[i].address, ep[i].type)
    //     }
    //
    //     let hex = hexdump(ptr(pListUIPtr).readPointer(), {
    //         length: 0x1000,
    //         header: true,
    //     })
    //     console.log(hex)
    //
    // }
    // else if (iContainerPtr > 0) {
    //     let containerAttribute = enumIContainerAttribute(pControlPtr, iContainerPtr)
    //     containerAttribute.id = parseInt(pControlPtr)
    //     containerAttribute.childControls = getChildControlsFromContainer(
    //         iContainerPtr,
    //         containerAttribute.childCount,
    //         bVerbose
    //     )
    //     return containerAttribute
    // }
    // else {
    //     let controlAttribute = enumControlAttribute(pControlPtr)
    //     controlAttribute.id = parseInt(pControlPtr)
    //     return controlAttribute
    // }
}

// 捕获访问异常，防止访问非法内存地址时崩溃
const withAccessErrorHanding = (func) => {
    return function () {
        try {
            return func.apply(this, arguments)
        }
        catch (e) {
            if (e.toString().indexOf("access violation accessing") !== -1) {
                return null
            }
            else {
                throw e
            }
        }
    }
}

// ****** FindControl API ****** //
// 获取root control
const FindRootControlPtr = (pHwnd) => {
    let paintManagerUIPtr = GetPaintManager(pHwnd)
    let GetRoot = Module.findExportByName("DuiLib.dll", '?GetRoot@CPaintManagerUI@DuiLib@@QBEPAVCControlUI@2@XZ')
    let funcGetRoot = new NativeFunction(GetRoot, 'pointer',['pointer'], 'thiscall')
    return funcGetRoot(paintManagerUIPtr)
}

const FindRootControl = (pHwnd, bVerbose) => {
    return getControlAttributeByPtr(FindRootControlPtr(pHwnd), bVerbose)
}

const FindControlById = (pControlPtr, bVerbose) => {
    return getControlAttributeByPtr(ptr(pControlPtr), bVerbose)
}

// 通过point查找control，point为相对于窗口左上角的坐标
const FindControlByPoint = (pHwnd, iPointX, iPointY, bVerbose) => {
    let paintManagerUIPtr = GetPaintManager(pHwnd)
    let funcFindControlByPoint = new NativeFunction(
        Module.findExportByName("DuiLib.dll", "?FindControl@CPaintManagerUI@DuiLib@@QBEPAVCControlUI@2@UtagPOINT@@@Z"),
        'pointer',
        ['pointer', 'uint64'],
        'thiscall'
    )
    let pPointPtr = Memory.alloc(8)
    pPointPtr.writeUInt(iPointX)
    pPointPtr.add(4).writeUInt(iPointY)
    return getControlAttributeByPtr(funcFindControlByPoint(paintManagerUIPtr, pPointPtr.readU64()), bVerbose)
}

// 通过name查找control
const FindControlByName = (pHwnd, sControlName, bVerbose) => {
    let funcFindControlByName = new NativeFunction(
        Module.findExportByName("DuiLib.dll", "?FindControl@CPaintManagerUI@DuiLib@@QBEPAVCControlUI@2@PB_W@Z"),
        'pointer',
        ['pointer', 'pointer'],
        'thiscall'
    )
    let paintManagerUIPtr = GetPaintManager(pHwnd)
    let sControlNamePtr = Memory.allocUtf16String(sControlName)
    return getControlAttributeByPtr(funcFindControlByName(paintManagerUIPtr, sControlNamePtr), bVerbose)
}

// 通过point查找sub control，point为相对于窗口左上角的坐标
const FindSubControlByPoint = (pHwnd, pParentControlUIPtr, iPointX, iPointY, bVerbose) => {
    let paintManagerUIPtr = GetPaintManager(pHwnd)
    let funcFindSubControlByTag = new NativeFunction(
        Module.findExportByName(
            "DuiLib.dll", "?FindSubControlByPoint@CPaintManagerUI@DuiLib@@QBEPAVCControlUI@2@PAV32@UtagPOINT@@@Z"
        ),
        'pointer',
        ['pointer', 'pointer', 'pointer'],
        'thiscall'
    )
    let pPointPtr = Memory.alloc(8)
    pPointPtr.writeUInt(iPointX)
    pPointPtr.add(4).writeUInt(iPointY)
    return getControlAttributeByPtr(
        funcFindSubControlByTag(paintManagerUIPtr, ptr(pParentControlUIPtr), pPointPtr),
        bVerbose
    )
}

// 通过name查找sub control
const FindSubControlByName = (pHwnd, pParentControlUIPtr, sControlName, bVerbose) => {
    let paintManagerUIPtr = GetPaintManager(pHwnd)
    let funcFindSubControlByName = new NativeFunction(
        Module.findExportByName(
            "DuiLib.dll", "?FindSubControlByName@CPaintManagerUI@DuiLib@@QBEPAVCControlUI@2@PAV32@PB_W@Z"
        ),
        'pointer',
        ['pointer', 'pointer', 'pointer'],
        'thiscall'
    )
    let sControlNamePtr = Memory.allocUtf16String(sControlName)
    return getControlAttributeByPtr(
        funcFindSubControlByName(paintManagerUIPtr, ptr(pParentControlUIPtr), sControlNamePtr),
        bVerbose
    )
}

// 通过class查找sub control
const FindSubControlByClass = (pHwnd, pParentControlUIPtr, sControlClass, iIndex, bVerbose) => {
    let paintManagerUIPtr = GetPaintManager(pHwnd)
    let funcFindSubControlByClass = new NativeFunction(
        Module.findExportByName(
            "DuiLib.dll", "?FindSubControlByClass@CPaintManagerUI@DuiLib@@QAEPAVCControlUI@2@PAV32@PB_WH@Z"
        ),
        'pointer',
        ['pointer', 'pointer', 'pointer', 'int'],
        'thiscall'
    )
    let sControlClassPtr = Memory.allocUtf16String(sControlClass)
    return getControlAttributeByPtr(
        funcFindSubControlByClass(
            paintManagerUIPtr,
            ptr(pParentControlUIPtr),
            sControlClassPtr,
            iIndex
        ),
        bVerbose
    )
}

// 通过class查找多个sub control
const FindSubControlsByClass = (pHwnd, pParentControlUIPtr, sControlClass, bVerbose) => {
    let paintManagerUIPtr = GetPaintManager(pHwnd)
    let funcFindSubControlsByClass = new NativeFunction(
        Module.findExportByName(
            "DuiLib.dll", "?FindSubControlsByClass@CPaintManagerUI@DuiLib@@QAEPAVCStdPtrArray@2@PAVCControlUI@2@PB_W@Z"
        ),
        'pointer',
        ['pointer', 'pointer', 'pointer'],
        'thiscall'
    )
    let sControlClassPtr = Memory.allocUtf16String(sControlClass)
    let controlArrayPtr = funcFindSubControlsByClass(
            paintManagerUIPtr,
            ptr(pParentControlUIPtr),
            sControlClassPtr
        )

    let controlAttributeArrayPtr = []
    for (let i = 0; i < getSizeFromCStdPtrArray(controlArrayPtr); i++) {
        controlAttributeArrayPtr.push(getControlAttributeByPtr(getAtFromCStdPtrArray(controlArrayPtr, i), bVerbose))
    }
    return controlAttributeArrayPtr
}

// ****** 其他API ****** //
// 获取HWND
const FindWindowHwnd = (sClassName = "", sWindowName = "") => {
    let findWindow = Module.findExportByName("User32.dll", 'FindWindowA')
    let funcFindWindow = new NativeFunction(findWindow, 'uint32',['pointer','pointer'])
    let classNameStrPtr = ptr(0)
    let windowNameStrPtr = ptr(0)
    if (sClassName) {
        classNameStrPtr = Memory.allocAnsiString(sClassName)
    }

    if (sWindowName) {
        windowNameStrPtr = Memory.allocAnsiString(sWindowName)
    }
    return funcFindWindow(ptr(classNameStrPtr), ptr(windowNameStrPtr))
}

// 获取WindowImplBase
const GetWindowLongA = (pHwnd) => {
    let GetWindowLongA = Module.findExportByName("User32.dll", 'GetWindowLongA')
    let funcGetWindowLongA = new NativeFunction(GetWindowLongA, 'uint32',['pointer', 'int32'])
    return funcGetWindowLongA(ptr(pHwnd), -21)
}

const GetWindowLongAWindProc = (pHwnd) => {
    let GetWindowLongA = Module.findExportByName("User32.dll", 'GetWindowLongW')
    let funcGetWindowLongA = new NativeFunction(GetWindowLongA, 'uint32',['pointer', 'int32'], 'stdcall')
    return funcGetWindowLongA(ptr(pHwnd), -4)
}

const SetWindowLongAWindProc = (pHwnd, pFunc) => {
    let SetWindowLongA = Module.findExportByName("User32.dll", 'SetWindowLongW')
    let funcSetWindowLongA = new NativeFunction(SetWindowLongA, 'uint32',['pointer', 'int32', 'uint32'], 'stdcall')
    return funcSetWindowLongA(ptr(pHwnd), -4, pFunc)
}

const PostMessage = (pHwnd, iMsg, wParam, lParam) => {
    let PostMessage = Module.findExportByName("User32.dll", 'PostMessageA')
    let funcPostMessage = new NativeFunction(PostMessage, 'uint32',['pointer', 'uint32', 'uint32', 'uint32'])
    return funcPostMessage(ptr(pHwnd), iMsg, wParam, lParam)
}

const SendMessage = (pHwnd, iMsg, wParam, lParam) => {
    let SendMessage = Module.findExportByName("User32.dll", 'SendMessageA')
    let funcSendMessage = new NativeFunction(SendMessage, 'uint32',['pointer', 'uint32', 'uint32', 'uint32'])
    return funcSendMessage(ptr(pHwnd), iMsg, wParam, lParam)
}

// 获取CPaintManagerUI
const GetPaintManager = (pHwnd) => {
    let windowImpBasePtr = GetWindowLongA(pHwnd)
    return ptr(windowImpBasePtr + 48)    // CPaintManagerUI是WindowImplBase的第一个成员变量，48是CPaintManagerUI的偏移
}

// 发送通知
const SendNotify = (pHwnd, pControlUIPtr, pStrMessage) => {
    let paintManagerUIPtr = GetPaintManager(pHwnd)
    let funcSendNotify = new NativeFunction(
        Module.findExportByName(
            "DuiLib.dll", "?SendNotify@CPaintManagerUI@DuiLib@@QAEXPAVCControlUI@2@PB_WIJ_N@Z"
        ),
        'void',
        ['pointer', 'pointer', 'pointer', 'uint32', 'uint32', 'bool'],
        'thiscall'
    )
    let pStrMessagePtr = Memory.allocUtf16String(pStrMessage)
    funcSendNotify(paintManagerUIPtr, ptr(pControlUIPtr), ptr(pStrMessagePtr), 0, 0, 0)
}

// 获取窗口线程ID
const GetWindowThreadProcessId = (pHwnd) => {
    let GetWindowThreadProcessId = Module.findExportByName("User32.dll", 'GetWindowThreadProcessId')
    let funcGetWindowThreadProcessId = new NativeFunction(
        GetWindowThreadProcessId,
        'uint32',
        ['pointer', 'pointer']
    )
    let pThreadIdPtr = Memory.alloc(4)
    funcGetWindowThreadProcessId(ptr(pHwnd), pThreadIdPtr)
    return pThreadIdPtr.readUInt()
}

// 确定指定窗口是否启用鼠标和键盘输入。
const IsWindowEnabled = (pHwnd) => {
    let IsWindowEnabled = Module.findExportByName("User32.dll", 'IsWindowEnabled')
    let funcIsWindowEnabled = new NativeFunction(
        IsWindowEnabled,
        'bool',
        ['pointer']
    )
    return funcIsWindowEnabled(ptr(pHwnd))
}


// 判断窗口线程是否是主线程
const isMainThread = (pHwnd) => {
    let currentThreadId = Process.getCurrentThreadId()
    let windowThreadId = GetWindowThreadProcessId(pHwnd)
    return currentThreadId === windowThreadId
}

// ****** 键鼠操作 ****** //
// 模拟键盘按键
const pressKeycode = (pHwnd, keyCode) => {
    PostMessage(ptr(pHwnd), 0x100, keyCode, 0); // 0x100: WM_KEYDOWN
    PostMessage(ptr(pHwnd), 0x101, keyCode, 0); // 0x101: WM_KEYUP
}

// 模拟鼠标滚动事件
const mouseWheel = (pHwnd, delta, iX=0, iY=0) => {
    // 将窗口坐标转换成屏幕坐标
    const [screenX, screenY] = clientToScreen(pHwnd, iX, iY);
    let wParam = (delta << 16) | 0
    let lParam = (screenY << 16) | screenX
    return PostMessage(pHwnd, 0x20A, wParam, lParam); // 0x20A: WM_MOUSEWHEEL
}

// 客户端坐标与屏幕坐标的相互转换
const convertXy = (pHwnd, x, y, isClientToScreen) => {
    const exportName = isClientToScreen ? 'ClientToScreen' : 'ScreenToClient';
    const funcName = isClientToScreen ? 'clientToScreen' : 'screenToClient';

    const convertFunction = Module.findExportByName('User32.dll', exportName);
    const pPointPtr = Memory.alloc(8);
    pPointPtr.writeInt(x);
    pPointPtr.add(4).writeInt(y);
    const funcConvert = new NativeFunction(convertFunction, 'uint32', ['pointer', 'pointer']);
    const ret = funcConvert(ptr(pHwnd), ptr(pPointPtr));
    const resultX = pPointPtr.readUInt();
    const resultY = pPointPtr.add(4).readUInt();
    return [resultX, resultY];
}

// 将窗口坐标转换成屏幕坐标
const clientToScreen = (pHwnd, x, y) => {
    return convertXy(pHwnd, x, y, true);
}

// 将屏幕坐标转换成窗口坐标
const screenToClient = (pHwnd, x, y) => {
    return convertXy(pHwnd, x, y, false);
}

// 鼠标移动到指定位置
const SetCursorPos = (x, y) => {
    let SetCursorPos = Module.findExportByName("User32.dll", 'SetCursorPos')
    let funcSetCursorPos = new NativeFunction(SetCursorPos, 'uint32',['int32', 'int32'])
    return funcSetCursorPos(x, y)
}

// 鼠标悬停到指定位置
const mouseHover = (pHwnd, x, y) => {
    const [screenX, screenY] = clientToScreen(pHwnd, x, y);
    return SetCursorPos(screenX, screenY);
}

rpc.exports = {
    findWindowHwnd: function (sClassName, sWindowName) {
        return FindWindowHwnd(sClassName, sWindowName)
    },
    getWindowLongA: function (pHwnd) {
        return GetWindowLongA(pHwnd)
    },

    // Find Control Api
    findRootControl: function (pHwnd, bVerbose = false) {
        return FindRootControl(pHwnd, bVerbose)
    },
    findControlById: function (pHwnd, iControlId, bVerbose = false) {
        return withAccessErrorHanding(FindControlById)(iControlId, bVerbose)
    },
    findControlByPointNative: function (pHwnd, iPointX, iPointY, bVerbose = false) {
        return withAccessErrorHanding(FindControlByPoint)(pHwnd, iPointX, iPointY, bVerbose)
    },
    findControlByNameNative: function (pHwnd, sControlName, bVerbose = false) {
        return withAccessErrorHanding(FindControlByName)(pHwnd, sControlName, bVerbose)
    },
    findSubcontrolByPointNative: function (pHwnd, pParentControlUIPtr, iPointX, iPointY, bVerbose = false) {
        return withAccessErrorHanding(FindSubControlByPoint)(pHwnd, pParentControlUIPtr, iPointX, iPointY, bVerbose)
    },
    findSubcontrolByNameNative: function (pHwnd, pParentControlUIPtr, sControlName, bVerbose = false) {
        return withAccessErrorHanding(FindSubControlByName)(pHwnd, pParentControlUIPtr, sControlName, bVerbose)
    },
    findSubcontrolByClassNative: function (pHwnd, pParentControlUIPtr, sControlClass, iIndex, bVerbose = false) {
        return withAccessErrorHanding(FindSubControlByClass)(pHwnd, pParentControlUIPtr, sControlClass, iIndex, bVerbose)
    },
    findSubcontrolsByClassNative: function (pHwnd, pParentControlUIPtr, sControlClass, bVerbose = false) {
        return withAccessErrorHanding(FindSubControlsByClass)(pHwnd, pParentControlUIPtr, sControlClass, bVerbose)
    },

    // Control Api
    getParent: function (pControlUIPtr, bVerbose = false) {
        let parentPtr = GetParent(ptr(pControlUIPtr))
        return withAccessErrorHanding(FindControlById)(parentPtr, bVerbose)
    },
    setVisible: function (pControlUIPtr, bVisible = true) {
        return SetVisible(ptr(pControlUIPtr), bVisible)
    },
    setFocus: function (pControlUIPtr) {
        return SetFocus(ptr(pControlUIPtr))
    },
    setEnabled: function (pControlUIPtr, bEnabled = true) {
        return SetEnabled(ptr(pControlUIPtr), bEnabled)
    },
    active: function (pHwnd, pControlUIPtr, onMainThread = true) {
        if (onMainThread) {
            let funcWndProc = GetWindowLongAWindProc(ptr(pHwnd))
            Interceptor.attach(ptr(funcWndProc), {
                onEnter: function(args) {
                    // 0x8FFF: Activate
                    if (args[1].toInt32() === 0x8FFF) {     // args[1] is iMsg
                        Activate(args[2])                   // args[2] is pControlUIPtr
                    }
                }
            });
            return PostMessage(ptr(pHwnd), 0x8FFF, pControlUIPtr, 0)
        }
        else {
            return Activate(ptr(pControlUIPtr))
        }

    },
    clickXy: function (pHwnd, iX, iY) {
        let lParam = (iY << 16) | iX
        PostMessage(ptr(pHwnd), 0x201, 0, lParam)           // 0x201: WM_LBUTTONDOWN
        return PostMessage(ptr(pHwnd), 0x202, 0, lParam)    // 0x202: WM_LBUTTONUP
    },
    setText: function (pHwnd, pControlUIPtr, sText, onMainThread = true) {

        if (onMainThread) {
            // pHwnd = 3018440
            let funcWndProc = GetWindowLongAWindProc(ptr(pHwnd))
            let inte = Interceptor.attach(ptr(funcWndProc), {
                onEnter: function(args) {
                    // isMainThread(pHwnd)
                    // 0x9FFF: setText
                    if (args[1].toInt32() === 0x9FFF) {             // args[1] is iMsg
                        let sText = ptr(args[3]).readUtf16String()  // args[3] is sText
                        SetText(args[2], sText)                     // args[2] is pControlUIPtr
                        SendNotify(pHwnd, args[2], "textchanged")           // args[2] is pControlUIPtr
                        // return true
                    }
                }
            });
            let pStrTextPtr = Memory.allocUtf16String(sText)
            SendMessage(ptr(pHwnd), 0x9FFF, pControlUIPtr, parseInt(pStrTextPtr))
            return true
        }
        else {
            SetText(ptr(pControlUIPtr), sText)
            SendNotify(pHwnd, pControlUIPtr, "textchanged")
            return true
        }
    },
    isWindowEnabled: function (pHwnd) {
        return IsWindowEnabled(ptr(pHwnd)) === 1
    },

    pressKeycode: function (pHwnd, keyCode) {
        return pressKeycode(pHwnd, keyCode);
    },

    mouseWheel: function (pHwnd, delta, x, y) {
    return mouseWheel(pHwnd, delta, x, y);
    },

    clientToScreen: function (pHwnd, x, y) {
    return clientToScreen(pHwnd, x, y);
    },

    screenToClient: function (pHwnd, x, y) {
    return screenToClient(pHwnd, x, y);
    },

    setCursorPos: function (x, y) {
    return SetCursorPos(x, y);
    },

    mouseHover: function (pHwnd, x, y) {
    return mouseHover(pHwnd, x, y);
    },

    // // ListOwnerUI Api
    // getCurSel: function (pControlUIPtr) {
    //     let pListOwnerPtr = GetInterface(ptr(pControlUIPtr), "IListOwner")
    //     let pTabLayoutPtr = GetInterface(ptr(pControlUIPtr), "TabLayout")
    //     if (pListOwnerPtr > 0) {
    //         return GetCurSel(pListOwnerPtr)
    //     }
    //     if (pTabLayoutPtr > 0) {
    //         return GetCurSelTabLayoutUI(pTabLayoutPtr)
    //     }
    //     return null
    // }
}
