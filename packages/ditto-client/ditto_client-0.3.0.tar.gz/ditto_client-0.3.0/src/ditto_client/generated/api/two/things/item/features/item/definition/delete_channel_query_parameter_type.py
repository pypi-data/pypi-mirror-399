from enum import Enum

class DeleteChannelQueryParameterType(str, Enum):
    Twin = "twin",
    Live = "live",

