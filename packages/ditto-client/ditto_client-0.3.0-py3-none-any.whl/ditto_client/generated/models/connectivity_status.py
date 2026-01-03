from enum import Enum

class ConnectivityStatus(str, Enum):
    Open = "open",
    Closed = "closed",
    Failed = "failed",
    Misconfigured = "misconfigured",
    Unknown = "unknown",

