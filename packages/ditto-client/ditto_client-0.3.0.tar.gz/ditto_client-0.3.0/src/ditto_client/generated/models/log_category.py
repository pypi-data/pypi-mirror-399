from enum import Enum

class LogCategory(str, Enum):
    Source = "source",
    Target = "target",
    Response = "response",
    Connection = "connection",

