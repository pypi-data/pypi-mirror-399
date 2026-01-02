import copy


class RPCScriptMetaclass(type):

    def __new__(mcs, name, bases, attrs):
        super_new = super().__new__

        rpc_script: dict = attrs.get("rpc_scripts")
        rpc_scripts_with_hwnd = attrs.get("rpc_scripts_with_hwnd", None)      # control api with hwnd
        if rpc_scripts_with_hwnd:
            rpc_script += rpc_scripts_with_hwnd

        _script_call = attrs.get("_script_call")

        if rpc_script:
            for script_name in rpc_script.keys():
                def script_request():
                    copy_script_name = copy.deepcopy(script_name)

                    def wrapper(self, *args, **kwargs):
                        hwnd = kwargs.pop("hwnd", None)
                        control_id = kwargs.pop("control_id", None)
                        # There is some problem with the frida rpc call params.
                        # So we have to use this method to pass the **kwargs.
                        # But it will cause the problem with the order of **kwargs.
                        args_from_kwargs = [v for v in kwargs.values()]

                        args_list = []
                        if hwnd is not None:
                            args_list.append(hwnd)

                        if control_id is not None:
                            args_list.append(control_id)
                        args_list += args
                        args_list += args_from_kwargs

                        return self._script_call(copy_script_name)(*args_list)
                    return wrapper

                attrs[script_name] = script_request()

        return super_new(mcs, name, bases, attrs)


class RPCScript(metaclass=RPCScriptMetaclass):

    __slots__ = ()

    rpc_scripts = {}

    def _script_call(self, script_function_name):
        return getattr(getattr(self, "script").exports_sync, script_function_name)


class DriverRPCScript(RPCScript):

    rpc_scripts = {
        # driver api
        "find_window_hwnd": {
            "need_hwnd": False,
            "need_control_id": False,
        },
    }


class WindowRPCScript(RPCScript):

    rpc_scripts = {
        # window api
        "find_root_control": {
            "need_hwnd": True,
            "need_control_id": False,
        },
        "find_control_by_id": {
            "need_hwnd": True,
            "need_control_id": False,
        },
        "find_control_by_name_native": {
            "need_hwnd": True,
            "need_control_id": False,
        },
        "find_control_by_point_native": {
            "need_hwnd": True,
            "need_control_id": False,
        },

        "find_subcontrol_by_name_native": {
            "need_hwnd": True,
            "need_control_id": False,
        },
        "find_subcontrol_by_class_native": {
            "need_hwnd": True,
            "need_control_id": False,
        },
        "find_subcontrol_by_point_native": {
            "need_hwnd": True,
            "need_control_id": False,
        },
        "find_subcontrols_by_class_native": {
            "need_hwnd": True,
            "need_control_id": False,
        },

        # action api
        "click_xy": {
            "need_hwnd": True,
            "need_control_id": False,
        },
        "press_keycode": {
            "need_hwnd": True,
            "need_control_id": False,
        },
        "mouse_wheel": {
            "need_hwnd": True,
            "need_control_id": False,
        },
        "mouse_hover": {
            "need_hwnd": True,
            "need_control_id": False,
        },
    }


class ControlRPCScript(RPCScript):

    rpc_scripts = {
        # control api
        "set_visible": {
            "need_hwnd": False,
            "need_control_id": True,
        },
        "set_focus": {
            "need_hwnd": False,
            "need_control_id": True,
        },
        "set_enabled": {
            "need_hwnd": False,
            "need_control_id": True,
        },

        "active": {
            "need_hwnd": True,
            "need_control_id": True,
        },
        "set_text": {
            "need_hwnd": True,
            "need_control_id": True,
        },
        "click_xy": {
            "need_hwnd": True,
            "need_control_id": False,
        },
        "get_parent": {
            "need_hwnd": False,
            "need_control_id": True,
        },

        # common api
        "is_window_enabled": {
            "need_hwnd": True,
            "need_control_id": False,
        },

        # # ListOwnerUI api
        # "get_cur_sel": {
        #     "need_hwnd": False,
        #     "need_control_id": True,
        # }
    }
