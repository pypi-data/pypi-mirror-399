from dui_automation.da.common.decorator import mixins_call_with_auto_params
from dui_automation.hook.rpc import WindowRPCScript


class WindowActionRPCScriptMixin(WindowRPCScript):

    @mixins_call_with_auto_params
    def click_xy(self, x: int, y: int):
        """
        Click coordinates.
        """
