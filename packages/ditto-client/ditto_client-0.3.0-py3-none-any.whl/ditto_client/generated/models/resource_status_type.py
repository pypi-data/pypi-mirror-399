from enum import Enum

class ResourceStatus_type(str, Enum):
    Client = "client",
    Source = "source",
    Target = "target",

