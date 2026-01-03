from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .new_connection_ssh_tunnel_credentials_type import NewConnection_sshTunnel_credentials_type

@dataclass
class NewConnection_sshTunnel_credentials(AdditionalDataHolder, Parsable):
    """
    The credentials used to authenticate at the SSH host. Password and public key authentication are supported.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The password used for authentication when credentials type `password` is used.
    password: Optional[str] = None
    # Private key in PEM base64-encoded format using PKCS #8 syntax. This field is required for credentials type`public-key`.
    private_key: Optional[str] = None
    # Public key in PEM base64-encoded format using X.509 syntax. This field is required for credentials type`public-key`.
    public_key: Optional[str] = None
    # The type of credentials used to authenticate. Either `password` or `public-key`.
    type: Optional[NewConnection_sshTunnel_credentials_type] = None
    # The username used for the authentication.
    username: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> NewConnection_sshTunnel_credentials:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: NewConnection_sshTunnel_credentials
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return NewConnection_sshTunnel_credentials()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .new_connection_ssh_tunnel_credentials_type import NewConnection_sshTunnel_credentials_type

        from .new_connection_ssh_tunnel_credentials_type import NewConnection_sshTunnel_credentials_type

        fields: dict[str, Callable[[Any], None]] = {
            "password": lambda n : setattr(self, 'password', n.get_str_value()),
            "privateKey": lambda n : setattr(self, 'private_key', n.get_str_value()),
            "publicKey": lambda n : setattr(self, 'public_key', n.get_str_value()),
            "type": lambda n : setattr(self, 'type', n.get_enum_value(NewConnection_sshTunnel_credentials_type)),
            "username": lambda n : setattr(self, 'username', n.get_str_value()),
        }
        return fields
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        writer.write_str_value("password", self.password)
        writer.write_str_value("privateKey", self.private_key)
        writer.write_str_value("publicKey", self.public_key)
        writer.write_enum_value("type", self.type)
        writer.write_str_value("username", self.username)
        writer.write_additional_data_value(self.additional_data)
    

