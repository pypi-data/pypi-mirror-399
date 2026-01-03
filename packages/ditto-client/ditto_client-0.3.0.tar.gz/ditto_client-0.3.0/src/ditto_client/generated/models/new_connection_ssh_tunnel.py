from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .new_connection_ssh_tunnel_credentials import NewConnection_sshTunnel_credentials

@dataclass
class NewConnection_sshTunnel(AdditionalDataHolder, Parsable):
    """
    The configuration of a local SSH port forwarding used to tunnel the connection to the actual endpoint.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The credentials used to authenticate at the SSH host. Password and public key authentication are supported.
    credentials: Optional[NewConnection_sshTunnel_credentials] = None
    # Whether the tunnel is enabled
    enabled: Optional[bool] = None
    # A list of accepted public key fingerprints. One of these fingerprints must match the fingerprintof the public key the SSH host provides.
    known_hosts: Optional[list[str]] = None
    # The URI of the SSH host in the format `ssh://[host]:[port]`.
    uri: Optional[str] = None
    # Whether the SSH host is validated using the provided fingerprints.
    validate_host: Optional[bool] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> NewConnection_sshTunnel:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: NewConnection_sshTunnel
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return NewConnection_sshTunnel()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .new_connection_ssh_tunnel_credentials import NewConnection_sshTunnel_credentials

        from .new_connection_ssh_tunnel_credentials import NewConnection_sshTunnel_credentials

        fields: dict[str, Callable[[Any], None]] = {
            "credentials": lambda n : setattr(self, 'credentials', n.get_object_value(NewConnection_sshTunnel_credentials)),
            "enabled": lambda n : setattr(self, 'enabled', n.get_bool_value()),
            "knownHosts": lambda n : setattr(self, 'known_hosts', n.get_collection_of_primitive_values(str)),
            "uri": lambda n : setattr(self, 'uri', n.get_str_value()),
            "validateHost": lambda n : setattr(self, 'validate_host', n.get_bool_value()),
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
        writer.write_object_value("credentials", self.credentials)
        writer.write_bool_value("enabled", self.enabled)
        writer.write_collection_of_primitive_values("knownHosts", self.known_hosts)
        writer.write_str_value("uri", self.uri)
        writer.write_bool_value("validateHost", self.validate_host)
        writer.write_additional_data_value(self.additional_data)
    

