from enum import Enum

class Source_replyTarget_expectedResponseTypes(str, Enum):
    Response = "response",
    Error = "error",
    Nack = "nack",

