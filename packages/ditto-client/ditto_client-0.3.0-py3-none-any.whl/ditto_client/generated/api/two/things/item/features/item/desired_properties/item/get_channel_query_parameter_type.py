from enum import Enum

class GetChannelQueryParameterType(str, Enum):
    Twin = "twin",
    Live = "live",

