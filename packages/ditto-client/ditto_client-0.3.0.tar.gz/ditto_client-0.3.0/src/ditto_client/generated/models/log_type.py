from enum import Enum

class LogType(str, Enum):
    Consumed = "consumed",
    Dispatched = "dispatched",
    Filtered = "filtered",
    Mapped = "mapped",
    Dropped = "dropped",
    Enforced = "enforced",
    Published = "published",
    Other = "other",

