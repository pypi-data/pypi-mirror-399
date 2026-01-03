from enum import Enum

class NewConnection_sshTunnel_credentials_type(str, Enum):
    Password = "password",
    PublicKey = "public-key",

