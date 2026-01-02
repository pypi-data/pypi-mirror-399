from enum import Enum


class By(Enum):
    """Set of jsonpath supported locator strategies."""

    ID = "id"
    NAME = "name"
    CLASS = "class"
    TEXT = "text"
    TIP = "tip"
    JSONPATH = "jsonpath"
    HINT = "hint"
    ControlType = "ControlTypeName"

    # Native
    NAT_ID = "nat_id"
    NAT_NAME = "nat_name"
    NAT_CLASS = "nat_class"
    NAT_POINT = "nat_point"
