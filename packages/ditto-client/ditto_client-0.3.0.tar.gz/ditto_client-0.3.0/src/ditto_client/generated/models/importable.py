from enum import Enum

class Importable(str, Enum):
    Implicit = "implicit",
    Explicit = "explicit",
    Never = "never",

