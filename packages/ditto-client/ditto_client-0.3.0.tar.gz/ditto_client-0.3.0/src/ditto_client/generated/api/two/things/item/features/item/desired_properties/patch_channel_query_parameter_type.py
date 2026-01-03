from enum import Enum

class PatchChannelQueryParameterType(str, Enum):
    Twin = "twin",
    Live = "live",

