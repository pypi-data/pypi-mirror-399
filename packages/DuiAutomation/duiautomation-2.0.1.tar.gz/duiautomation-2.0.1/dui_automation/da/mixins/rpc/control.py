
from dui_automation.da.common.decorator import (
    mixins_call_with_auto_params,
    check_window_enabled,
    check_control_is_accessible
)
from dui_automation.da.core.exception import (
    UnrecognizableControlDataError
)
from dui_automation.hook.rpc import ControlRPCScript


class ControlRPCScriptMixin(ControlRPCScript):

    # **** RPC Native APIs **** #
    @check_window_enabled
    @mixins_call_with_auto_params
    def set_visible(self, visible: bool = True):
        """
        [Native Function] Set control visible.

        Arguments:
            visible {bool} -- visible.
        """

    @check_window_enabled
    @mixins_call_with_auto_params
    def set_focus(self):
        """
        [Native Function] Set control focus.
        """

    @check_window_enabled
    @mixins_call_with_auto_params
    def set_enabled(self, enable: bool = True):
        """
        [Native Function] Set control enable.

        Arguments:
            enable {bool} -- enable.
        """

    @check_control_is_accessible
    @check_window_enabled
    @mixins_call_with_auto_params
    def active(self, on_main_thread: bool = True):
        """
        [Native Function] Active control. some like click.

        Keyword Arguments:
            on_main_thread {bool} -- whether to run on the main thread. (default: {True}).
                                     if not set to True, the click event may not be triggered,
                                     or the target app may crash.
        """

    @check_control_is_accessible
    @check_window_enabled
    @mixins_call_with_auto_params
    def set_text(self, text: str, on_main_thread: bool = True):
        """
        [Native Function] Set control text.

        Arguments:
            text {str} -- text.

        Keyword Arguments:
            on_main_thread {bool} -- whether to run on the main thread. (default: {True}).
                         if not set to True, the click event may not be triggered,
                         or the target app may crash.
        """

    @check_control_is_accessible
    @check_window_enabled
    @mixins_call_with_auto_params
    def click_xy(self, x: int, y: int):
        """
        Click coordinates.

        Arguments:
            x {int} -- x.
            y {int} -- y.
        """

    @check_control_is_accessible
    @check_window_enabled
    def click(self):
        """
        Click control. (click center)
        """
        x = getattr(self, "x", None)
        y = getattr(self, "y", None)
        width = getattr(self, "width", None)
        height = getattr(self, "height", None)
        if x is None or y is None or width is None or height is None:
            raise UnrecognizableControlDataError(
                "The control data is not complete, \n"
                "maybe the control is invalid or not visible, \n"
                "if you want to click the control, \n"
                "please use the 'click_xy' method to click."
            )
        return self.click_xy(x + width // 2, y + height // 2)

    @check_window_enabled
    def hover(self):
        """
        Move mouse to control.
        """
        x = getattr(self, "x", None)
        y = getattr(self, "y", None)
        width = getattr(self, "width", None)
        height = getattr(self, "height", None)
        owner = getattr(self, "owner", None)
        if x is None or y is None or width is None or height is None:
            raise UnrecognizableControlDataError(
                "The control data is not complete, \n"
                "maybe the control is invalid or not visible, \n"
            )
        if owner:
            return owner.window.mouse_hover(x + width // 2, y + height // 2)
        else:
            raise TypeError("The control has no owner.")

    @mixins_call_with_auto_params
    def get_parent(self, verbose: bool = False):
        """
        Get parent control.

        Keyword Arguments:
            verbose {bool} -- whether to return the parent control data. (default: {False}).
        """

    # common
    @mixins_call_with_auto_params
    def is_window_enabled(self) -> bool:
        """
        Check if window is enabled.

        Returns:
            bool -- True if window is enabled, otherwise False.
        """

    # @warning_msg("Warning: Don't use this method directly, use the `get_current_selected` property instead.")
    # @check_window_enabled
    # @mixins_call_with_auto_params
    # def get_cur_sel(self) -> int:
    #     """
    #     [ListControl] Get current selected index.
    #     (Warning: Don't use this method directly, use the `get_current_selected` property instead.)
    #
    #     Returns:
    #         int -- current selected index.
    #     """
    #
    # @check_window_enabled
    # def get_current_selected(self) -> int:
    #     """
    #     [ListControl] Get current selected index, only for ListControl.
    #
    #     Returns:
    #         int -- current selected index.
    #     """
    #     cur_sel_index = undecorated_control(self.get_cur_sel)()
    #     if cur_sel_index is not None:
    #         return cur_sel_index
    #     else:
    #         raise ControlMethodCallTypeError(
    #             "get_current_selected",
    #             "ListOwner | TabLayoutUI"
    #         )
