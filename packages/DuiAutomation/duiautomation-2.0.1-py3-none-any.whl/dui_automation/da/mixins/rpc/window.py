from typing import Union, List, Callable, Any

from jsonpath import jsonpath

from dui_automation.hook.rpc import WindowRPCScript

from dui_automation.da.common.by import By
from dui_automation.da.common.keycode import Keycode
from dui_automation.da.common.configurator import Configurator
from dui_automation.da.common.decorator import undecorated_control, poll, mixins_call_with_auto_params
from dui_automation.da.core.control import control, Control
from dui_automation.da.common.selector import Selector


class WindowRPCScriptMixin(WindowRPCScript):

    # **** RPC Native APIs **** #
    # Control APIs
    @control()
    @mixins_call_with_auto_params
    def find_root_control(self, verbose: bool = False) -> Control:
        """
        [Native Function] Find the root control of the window.

        Arguments:
            verbose {bool} -- return all control data (include subcontrols) if True
                              else return root control data only. Default: False.
                              Notice, verbose=True will take a long time to return.
                              (It will not pass to rpc script when you do not directly set it,
                              it means it will pass an undefined value to rpc script,
                              and the default value of verbose in rpc script is False.)

        Returns:
            Control -- root control
        """

    @control()
    @mixins_call_with_auto_params
    def find_control_by_id(self, control_id: int, verbose: bool = False) -> Control:
        """
        [Native Function] Find control by id.

        Arguments:
            control_id {int} -- control id

        Keyword Arguments:
            verbose {bool} -- return all control data (include subcontrols) if True
                              else return specified control data only. Default: False.

        Returns:
            Control -- Control
        """

    @control()
    @mixins_call_with_auto_params
    def find_control_by_name_native(
            self, control_name: str, instance: int = 0, verbose: bool = False
    ) -> Control:
        """
        [Native Function] Find control by name.

        Arguments:
            control_name {str} -- Control name

        Keyword Arguments:
            instance {int} -- instance of Control (default: {0})
            verbose {bool} -- return all Control data (include subcontrols) if True
                                else return specified control data only. Default: False.

        Returns:
            Control -- Control
        """

    @control()
    @mixins_call_with_auto_params
    def find_control_by_point_native(self, x: int, y: int, verbose: bool = False) -> Control:
        """
        [Native Function] Find control by point.

        Arguments:
            x {int} -- x coordinate
            y {int} -- y coordinate

        Keyword Arguments:
            verbose {bool} -- return all Control data (include subcontrols) if True
                              else return specified control data only. Default: False.

        Returns:
            Control -- Control
        """

    @control()
    @mixins_call_with_auto_params
    # SubControl APIs
    def find_subcontrol_by_name_native(
            self, parent_control_id: int, control_name: str, verbose: bool = False
    ) -> Control:
        """
        [Native Function] Find subcontrol by name.

        Arguments:
            parent_control_id {int} -- parent Control id
            control_name {str} -- subcontrol name

        Keyword Arguments:
            verbose {bool} -- return all Control data (include subcontrols) if True
                              else return specified control data only. Default: False.

        Returns:
            Control -- Control
        """

    @control()
    @mixins_call_with_auto_params
    def find_subcontrol_by_class_native(
            self, parent_control_id: int, control_class: str, instance: int = 0, verbose: bool = False
    ) -> Control:
        """
        [Native Function] Find subcontrol by class.

        Arguments:
            parent_control_id {int} -- parent Control id
            control_class {str} -- subcontrol class name

        Keyword Arguments:
            instance {int} -- instance of Control, it's named index in rpc script. (default: {0})
            verbose {bool} -- return all Control data (include subcontrols) if True
                              else return specified control data only. Default: False.

        Returns:
            Control -- Control
        """

    @control()
    @mixins_call_with_auto_params
    def find_subcontrol_by_point_native(
            self, parent_control_id: int, x: int, y: int, verbose: bool = False
    ) -> Control:
        """
        [Native Function] Find subcontrol by point.

        Arguments:
            parent_control_id {int} -- parent control id
            x {int} -- x coordinate
            y {int} -- y coordinate

        Keyword Arguments:
            verbose {bool} -- return all control data (include subcontrols) if True
                              else return specified control data only. Default: False.

        Returns:
            Control -- Control
        """

    @control()
    @mixins_call_with_auto_params
    def find_subcontrols_by_class_native(
            self, parent_control_id: int, control_class: str, verbose: bool = False
    ) -> List[Control]:
        """
        [Native Function] Find subcontrols by class.

        Arguments:
            parent_control_id {int} -- parent control id
            control_class {str} -- subcontrol class

        Keyword Arguments:
            verbose {bool} -- return all control data (include subcontrols) if True
                              else return specified control data only. Default: False.

        Returns:
            List[Control] -- controls
        """

    # **** Derived APIs **** #
    @staticmethod
    def _locator_convert_to_jsonpath(by: By, value: Union[str, int]) -> str:
        """
        Convert locator to jsonpath expression.

        Arguments:
            by {By} -- locator type
            value {Union[str, int]} -- locator value

        Returns:
            str -- jsonpath expression
        """
        match by:
            case By.ID:
                value = f"$..*[?(@.id=={value})]"
            case By.NAME:
                value = f'$..*[?(@.name=="{value}")]'
            case By.TEXT:
                value = f'$..*[?(@.text=="{value}")]'
            case By.CLASS:
                value = f'$..*[?(@.class=="{value}")]'
            case By.TIP:
                value = f'$..*[?(@.toolTip=="{value}")]'
            case By.HINT:
                value = f'$..*[?(@.hint=="{value}")]'
            case By.JSONPATH:
                value = value
            case _:
                raise ValueError(f"Invalid by: {by}")

        return value

    def _find_control_from_native(
            self,
            by: By,
            value: Union[str, int, List[int]],
            verbose: bool = False
    ) -> Control:
        match by:
            case By.NAT_ID:
                return self.find_control_by_id(value, verbose)
            case By.NAT_NAME:
                return self.find_control_by_name_native(value, verbose)
            case By.NAT_CLASS:
                raise ValueError(f"Not support by in `find_control`: {by}. "
                                 f"Maybe you should use if in `find_subcontrol`.")
            case By.NAT_POINT:
                if not isinstance(value, list):
                    raise ValueError(f"Invalid value for `find_control_by_point_native`: {value}, "
                                     f"must be a list of int.")
                return self.find_control_by_point_native(*value, verbose)
            case _:
                raise ValueError(f"Invalid by: {by}")

    def _find_subcontrol_from_native(
            self,
            by: By,
            value: Union[str, int, List[int]],
            parent_control: Union[Control, int],
            instance: int = 0,
            verbose: bool = False
    ) -> Control:

        if by != By.NAT_CLASS and instance != 0:
            raise ValueError(f"Not support instance: {instance} in Native find subcontrol apis,"
                             f"it should always return only one control.")

        parent_control_id = parent_control if isinstance(parent_control, int) else parent_control.id
        match by:
            case By.NAT_ID:
                raise ValueError(f"Not support by in `find_subcontrol`: {by}. "
                                 f"Maybe you should use if in `find_control`.")
            case By.NAT_NAME:
                return self.find_subcontrol_by_name_native(parent_control_id, value, verbose)
            case By.NAT_CLASS:
                return self.find_subcontrol_by_class_native(parent_control_id, value, instance, verbose)
            case By.NAT_POINT:
                if not isinstance(value, list):
                    raise ValueError(f"Invalid value for `find_subcontrol_by_point_native`: {value}, "
                                     f"must be a list of int.")
                return self.find_subcontrol_by_point_native(parent_control_id, *value, verbose)
            case _:
                raise ValueError(f"Invalid by: {by}")

    def _find_subcontrols_from_native(
            self,
            by: By,
            value: Union[str, int],
            parent_control: Union[Control, int],
            verbose: bool = False
    ) -> List[Control]:
        parent_control_id = parent_control if isinstance(parent_control, int) else parent_control.id
        match by:
            case By.NAT_ID:
                raise ValueError(f"Not support by in `find_subcontrols`: {by}. "
                                 f"Maybe you should use if in `find_control`.")
            case By.NAT_NAME:
                raise ValueError(f"Not support by in `find_subcontrols`: {by}. "
                                 f"Maybe you should use if in `find_controls` or `find_subcontrol`.")
            case By.NAT_CLASS:
                return self.find_subcontrols_by_class_native(parent_control_id, value, verbose)
            case By.NAT_POINT:
                raise ValueError(f"Not support by in `find_subcontrols`: {by}. "
                                 f"Maybe you should use if in `find_controls` or `find_subcontrol`.")
            case _:
                raise ValueError(f"Invalid by: {by}")

    def _find_controls_by_jsonpath_from_control(
            self, specified_control: Union[Control, int, None], jsonpath_expr: str
    ) -> List[Control]:
        """
        Find controls by jsonpath expression from specified control.

        Arguments:
            control_id {int} -- control id
            jsonpath_expr {str} -- jsonpath expression

        Returns:
            List[Control] -- controls
        """
        if isinstance(specified_control, Control):
            control_data = undecorated_control(self.find_control_by_id)(
                specified_control.id, verbose=True
            )
        elif isinstance(specified_control, int) and specified_control > 0:
            control_data = undecorated_control(self.find_control_by_id)(
                specified_control, verbose=True
            )
        else:
            # From root control
            control_data = undecorated_control(self.find_root_control)(verbose=True)

        parse_data = jsonpath(control_data, jsonpath_expr)

        return parse_data

    # Control APIs
    @control()
    def find_controls_by_jsonpath(self, jsonpath_expr: str) -> List[Control]:
        """
        Find controls by jsonpath expression.

        Arguments:
            jsonpath_expr {str} -- jsonpath expression

        Returns:
            List[Control] -- controls
        """
        return self._find_controls_by_jsonpath_from_control(0, jsonpath_expr)

    @control()
    def find_control_by_jsonpath(
            self, jsonpath_expr: str, instance: int = 0
    ) -> Control | None:
        """
        Find control by jsonpath expression.

        Arguments:
            jsonpath_expr {str} -- jsonpath expression

        Keyword Arguments:
            instance {int} --  the number of control instance (default: {0})

        Returns:
            Control -- Control
        """
        try:
            return self._find_controls_by_jsonpath_from_control(0, jsonpath_expr)[instance]
        except TypeError:
            return None

    def find_controls(
            self, by: Union[By, Selector] = By.ID, value: Union[str, int] = None
    ) -> List[Control]:
        """
        Find controls by locator.

        Arguments:
            by {Union[By, Selector]} -- locator type
            value {Union[str, int]} -- locator value

        Returns:
            List[Control] -- controls
        """
        if isinstance(by, Selector):
            _by = by.by
            _value = by.value
            return self.find_controls(_by, _value)

        value = self._locator_convert_to_jsonpath(by, value)

        return self.find_controls_by_jsonpath(value)

    def find_control_native(
            self,
            by: Union[By, Selector] = By.ID,
            value: Union[str, int] = None,
            verbose: bool = False
    ) -> Control:
        if isinstance(by, Selector):
            _by = by.by
            _value = by.value
            return self.find_control_native(_by, _value, verbose)

        support_native_by = [
            By.NAT_NAME,
            By.NAT_POINT
        ]

        if by.value.startswith("nat_"):
            if by not in support_native_by:
                raise ValueError(f"Not support by in `find_control_native`: {by}.")
            else:
                return self._find_control_from_native(by, value, verbose)
        else:
            raise ValueError(f"Not support by in `find_control_native`: {by}. Did you mean `find_control`?")

    def find_control(
            self,
            by: Union[By, Selector] = By.ID,
            value: Union[str, int] = None,
            instance: int = 0,
            verbose: bool = False
    ) -> Control | None:
        """
        Find control by locator.

        Arguments:
            by {Union[By, Selector]} -- locator type
            value {Union[str, int]} -- locator value

        Keyword Arguments:
            instance {int} --  the number of control instance, default: 0 (Invalid for native find api).
            verbose {bool} -- return all control data (include subcontrols) if True (Only for native find api),

        Returns:
            Control -- Control
        """
        if isinstance(by, Selector):
            _by = by.by
            _value = by.value
            _instance = by.instance
            return self.find_control(_by, _value, _instance, verbose)

        if by.value.startswith("nat_"):
            if instance != 0:
                raise ValueError(f"not support instance: {instance} in Native find control apis,"
                                 f"it should always return only one control.")
            return self.find_control_native(by, value, verbose)
        else:
            value = self._locator_convert_to_jsonpath(by, value)
            return self.find_control_by_jsonpath(value, instance)

    def find_control_by_name(self, control_name: str, instance: int = 0) -> Control:
        """
        Find control by name.

        Arguments:
            control_name {str} -- control name

        Keyword Arguments:
            instance {int} --  the number of control instance (default: {0})

        Returns:
            Control -- Control
        """
        return self.find_control(by=By.NAME, value=control_name, instance=instance)

    def find_control_by_text(self, text: str, instance: int = 0) -> Control:
        """
        Find control by text.

        Arguments:
            text {str} -- control text

        Keyword Arguments:
            instance {int} --  the number of control instance (default: {0})

        Returns:
            Control -- Control
        """
        return self.find_control(by=By.TEXT, value=text, instance=instance)

    def find_control_by_class(self, control_class: str, instance: int = 0) -> Control:
        """
        Find control by class.

        Arguments:
            control_class {str} -- control class

        Keyword Arguments:
            instance {int} --  the number of control instance (default: {0})

        Returns:
            Control -- Control
        """
        return self.find_control(by=By.CLASS, value=control_class, instance=instance)

    def find_control_by_tip(self, tip: str, instance: int = 0) -> Control:
        """
        Find control by tip.

        Arguments:
            tip {str} -- control tip

        Keyword Arguments:
            instance {int} --  the number of control instance (default: {0})

        Returns:
            Control -- Control
        """
        return self.find_control(by=By.TIP, value=tip, instance=instance)

    def find_control_by_hint(self, hint: str, instance: int = 0) -> Control:
        """
        Find control by hint.

        Arguments:
            hint {str} -- control hint

        Keyword Arguments:
            instance {int} --  the number of control instance (default: {0})

        Returns:
            Control -- Control
        """
        return self.find_control(by=By.HINT, value=hint, instance=instance)

    def dump(self) -> Control:
        """
        Dump root control (including all subcontrols).

        Returns:
            Control -- root control
        """
        return self.find_root_control(verbose=True)

    # SubControl APIs
    @control()
    def find_subcontrols_by_jsonpath(
            self, parent_control: Union[Control, int], jsonpath_expr: str
    ) -> List[Control]:
        """
        Find subcontrols by jsonpath expression.

        Arguments:
            parent_control {Union[Control, int]} -- parent control
            jsonpath_expr {str} -- jsonpath expression

        Returns:
            List[Control] -- subcontrols
        """
        return self._find_controls_by_jsonpath_from_control(
            parent_control, jsonpath_expr
        )

    @control()
    def find_subcontrol_by_jsonpath(
            self, parent_control: Union[Control, int], jsonpath_expr: str, instance: int = 0
    ) -> Control | None:
        """
        Find subcontrol by jsonpath expression.

        Arguments:
            parent_control {Union[Control, int]} -- parent control
            jsonpath_expr {str} -- jsonpath expression

        Keyword Arguments:
            instance {int} --  the number of control instance (default: {0})

        Returns:
            Control -- subcontrol
        """

        try:
            return self._find_controls_by_jsonpath_from_control(
                parent_control, jsonpath_expr
            )[instance]
        except IndexError:
            return None

    def find_subcontrols_native(
            self,
            parent_control: Union[Control, int],
            by: Union[By, Selector] = By.ID,
            value: Union[str, int] = None,
            verbose: bool = False
    ) -> List[Control]:
        support_native_by = [
            By.NAT_CLASS,
        ]
        if isinstance(by, Selector):
            _by = by.by
            _value = by.value
            return self.find_subcontrols_native(parent_control, _by, _value, verbose)

        if by.value.startswith("nat_"):
            if by not in support_native_by:
                raise ValueError(f"Not support by in `find_subcontrols_native`: {by}.")
            else:
                return self._find_subcontrols_from_native(by, value, parent_control, verbose)
        else:
            raise ValueError(f"Not support by in `find_subcontrols_native`: {by}. Did you mean `find_subcontrols`?")

    def find_subcontrols(
            self,
            parent_control: Union[Control, int],
            by: Union[By, Selector] = By.ID,
            value: Union[str, int] = None,
            verbose: bool = False
    ) -> List[Control]:
        """
        Find subcontrols by locator.

        Arguments:
            parent_control {Union[Control, int]} -- parent control

        Keyword Arguments:
            by {Union[By, Selector]} -- locator type (default: {By.ID})
            value {Union[str, int]} -- locator value (default: {None})
            verbose {bool} -- return all control data (include subcontrols) if True (Only for Native find control)

        Returns:
            List[Control] -- subcontrols
        """
        if isinstance(by, Selector):
            _by = by.by
            _value = by.value
            return self.find_subcontrols(parent_control, _by, _value)

        if by.value.startswith("nat_"):
            return self.find_subcontrols_native(parent_control, by, value, verbose)
        else:
            value = self._locator_convert_to_jsonpath(by, value)

            return self.find_subcontrols_by_jsonpath(parent_control, value)

    def find_subcontrol_native(
            self,
            parent_control: Union[Control, int],
            by: Union[By, Selector] = By.ID,
            value: Union[str, int] = None,
            instance: int = 0,
            verbose: bool = False
    ) -> Control:

        if isinstance(by, Selector):
            _by = by.by
            _value = by.value
            _instance = by.instance
            return self.find_subcontrol_native(parent_control, _by, _value, _instance, verbose)

        support_native_by = [
            By.NAT_NAME,
            By.NAT_CLASS,
            By.NAT_POINT
        ]

        if by.value.startswith("nat_"):
            if by not in support_native_by:
                raise ValueError(f"Not support by in `find_subcontrol_native`: {by}.")
            else:
                return self._find_subcontrol_from_native(by, value, parent_control, instance, verbose)
        else:
            raise ValueError(f"Not support by in `find_subcontrol_native`: {by}. Did you mean `find_subcontrol`?")

    def find_subcontrol(
            self,
            parent_control: Union[Control, int],
            by: Union[By, Selector] = By.ID,
            value: Union[str, int] = None,
            instance: int = 0,
            verbose: bool = False
    ) -> Control | None:
        """
        Find subcontrol by locator.

        Arguments:
            parent_control {Union[Control, int]} -- parent control

        Keyword Arguments:
            by {Union[By, Selector]} -- locator type (default: {By.ID})
            value {Union[str, int]} -- locator value (default: {None})
            instance {int} --  the number of control instance (default: {0})
            verbose {bool} -- return all control data (include subcontrols) if True (Only for Native find control)

        Returns:
            Control -- subcontrol
        """

        if isinstance(by, Selector):
            _by = by.by
            _value = by.value
            _instance = by.instance
            return self.find_subcontrol(parent_control, _by, _value, _instance, verbose)

        if by.value.startswith("nat_"):
            return self.find_subcontrol_native(parent_control, by, value, instance, verbose)
        else:
            value = self._locator_convert_to_jsonpath(by, value)

            return self.find_subcontrol_by_jsonpath(parent_control, value, instance)

    def find_subcontrol_by_name(
            self, parent_control: Union[Control, int], control_name: str, instance: int = 0
    ) -> Control:
        """
        Find subcontrol by name.

        Arguments:
            parent_control {Union[Control, int]} -- parent control
            control_name {str} -- control name

        Keyword Arguments:
            instance {int} --  the number of control instance (default: {0})

        Returns:
            Control -- subcontrol
        """
        return self.find_subcontrol(parent_control, by=By.NAME, value=control_name, instance=instance)

    def find_subcontrol_by_text(
            self, parent_control: Union[Control, int], text: str, instance: int = 0
    ) -> Control:
        """
        Find subcontrol by text.

        Arguments:
            parent_control {Union[Control, int]} -- parent control
            text {str} -- control text

        Keyword Arguments:
            instance {int} --  the number of control instance (default: {0})

        Returns:
            Control -- subcontrol
        """
        return self.find_subcontrol(parent_control, by=By.TEXT, value=text, instance=instance)

    def find_subcontrol_by_class(
            self, parent_control: Union[Control, int], control_class: str, instance: int = 0
    ) -> Control:
        """
        Find subcontrol by class.

        Arguments:
            parent_control {Union[Control, int]} -- parent control
            control_class {str} -- control class

        Keyword Arguments:
            instance {int} --  the number of control instance (default: {0})

        Returns:
            Control -- subcontrol
        """
        return self.find_subcontrol(parent_control, by=By.CLASS, value=control_class, instance=instance)

    def find_subcontrol_by_tip(
            self, parent_control: Union[Control, int], tip: str, instance: int = 0
    ) -> Control:
        """
        Find subcontrol by tip.

        Arguments:
            parent_control {Union[Control, int]} -- parent control
            tip {str} -- control tip

        Keyword Arguments:
            instance {int} --  the number of control instance (default: {0})

        Returns:
            Control -- subcontrol
        """
        return self.find_subcontrol(parent_control, by=By.TIP, value=tip, instance=instance)

    def find_subcontrol_by_hint(
            self, parent_control: Union[Control, int], hint: str, instance: int = 0
    ) -> Control:
        """
        Find subcontrol by hint.

        Arguments:
            parent_control {Union[Control, int]} -- parent control
            hint {str} -- control hint

        Keyword Arguments:
            instance {int} --  the number of control instance (default: {0})

        Returns:
            Control -- subcontrol
        """
        return self.find_subcontrol(parent_control, by=By.HINT, value=hint, instance=instance)

    # Exist APIs
    def exist(
            self,
            by: Union[By, Selector] = By.ID,
            value: Union[str, int] = None,
            instance: int = 0,
    ) -> bool:
        """
        Check if control exists.

        Keyword Arguments:
            by {Union[By, Selector]} -- locator type (default: {By.ID})
            value {Union[str, int]} -- locator value (default: {None})

        Returns:
            bool -- True if control exists, otherwise False
        """
        if isinstance(by, Selector):
            _by = by.by
            _value = by.value
            _instance = by.instance
            return self.exist(_by, _value, _instance)

        value = self._locator_convert_to_jsonpath(by, value)

        find_result = undecorated_control(self.find_control_by_jsonpath)(value, instance)

        return True if find_result else False

    def wait_for_exist(
            self,
            by: Union[By, Selector] = By.ID,
            value: Union[str, int] = None,
            timeout: int = 10,
    ):
        """
        Wait for control exists.

        Keyword Arguments:
            by {Union[By, Selector]} -- locator type (default: {By.ID})
            value {Union[str, int]} -- locator value (default: {None})
            timeout {int} -- timeout (default: {10})

        Returns:
            bool -- True if control exists, otherwise False
        """
        wait_for_control_poll = Configurator.WAIT_FOR_CONTROL_POLL
        find_result = poll(
            timeout=timeout,
            interval=wait_for_control_poll,
            # Need run watchers?
            callback=getattr(self, "run_watchers"),
        )(self.exist)(by, value)

        return True if find_result else False

    def is_visible(
            self,
            by: Union[By, Selector] = By.ID,
            value: Union[str, int] = None,
    ) -> bool:
        """
        Check if control is visible.

        Keyword Arguments:
            by {Union[By, Selector]} -- locator type (default: {By.ID})
            value {Union[str, int]} -- locator value (default: {None})

        Returns:
            bool -- True if control is visible, otherwise False
        """
        _control = self.find_control(by, value)
        return True if _control.visible else False

    def wait_for_visible(
            self,
            by: Union[By, Selector] = By.ID,
            value: Union[str, int] = None,
            timeout: int = 10,
    ):
        """
        Wait for the control to become visible.

        Keyword Arguments:
            by {Union[By, Selector]} -- locator type (default: {By.ID})
            value {Union[str, int]} -- locator value (default: {None})
            timeout {int} -- timeout (default: {10})

        Returns:
            bool -- True if control becomes visible or invisible, otherwise False
        """

        wait_for_control_poll = Configurator.WAIT_FOR_CONTROL_POLL

        result = poll(
            timeout=timeout,
            interval=wait_for_control_poll,
            callback=getattr(self, "run_watchers"),
        )(self.is_visible)(by, value)

        return True if result else False

    def wait_for_invisible(
            self,
            by: Union[By, Selector] = By.ID,
            value: Union[str, int] = None,
            timeout: int = 10):
        """
        Wait for the control to become invisible.

        Keyword Arguments:
            by {Union[By, Selector]} -- locator type (default: {By.ID})
            value {Union[str, int]} -- locator value (default: {None})
            timeout {int} -- timeout (default: {10})

        Returns:
            bool -- True if control becomes invisible, otherwise False
        """
        wait_for_control_poll = Configurator.WAIT_FOR_CONTROL_POLL

        def check_invisible():
            return not self.is_visible(by, value)

        result = poll(
            timeout=timeout,
            interval=wait_for_control_poll,
            callback=getattr(self, "run_watchers"),
        )(check_invisible)()

        return True if result else False

    @mixins_call_with_auto_params
    def press_keycode(self, keycode: int):
        """
        Press by keycode.

        Arguments:
            keycode -- keycode

        Returns:
            bool -- True if success, otherwise False
        """

    def press_key(self, keycode: Keycode):
        """
        Press key.

        Arguments:
            keycode -- keycode

        Returns:
            bool -- True if success, otherwise False
        """
        value = keycode.value
        return self.press_keycode(value)

    def press_enter(self):
        """
        Press enter.

        Returns:
            bool -- True if success, otherwise False
        """
        self.press_key(Keycode.ENTER)

    @mixins_call_with_auto_params
    def mouse_hover(self, x: int, y: int):
        """
        Mouse hover.

        Arguments:
            x {int} -- x
            y {int} -- y

        Returns:
            bool -- True if success, otherwise False
        """

    @mixins_call_with_auto_params
    def mouse_wheel(self, delta: int, x: int = 0, y: int = 0):
        """
        Mouse wheel.

        Arguments:
            delta {int} -- delta

        Keyword Arguments:

            x {int} -- x (default: {0})
            y {int} -- y (default: {0})

        Returns:
            bool -- True if success, otherwise False
        """
