from enum import Enum

class GetLiveChannelTimeoutStrategyQueryParameterType(str, Enum):
    Fail = "fail",
    UseTwin = "use-twin",

