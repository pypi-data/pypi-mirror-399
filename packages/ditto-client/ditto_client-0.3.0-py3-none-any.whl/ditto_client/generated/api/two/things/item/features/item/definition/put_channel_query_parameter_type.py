from enum import Enum

class PutChannelQueryParameterType(str, Enum):
    Twin = "twin",
    Live = "live",

