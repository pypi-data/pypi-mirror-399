from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .connectivity_status import ConnectivityStatus
    from .resource_status import ResourceStatus

@dataclass
class ConnectionStatus(AdditionalDataHolder, Parsable):
    """
    Status of a connection and its resources
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The client states of the of the connection
    client_status: Optional[list[ResourceStatus]] = None
    # The timestamp since when the connection is connected
    connected_since: Optional[str] = None
    # The connection ID
    connection_id: Optional[str] = None
    # The desired/target status of the connection
    connection_status: Optional[ConnectivityStatus] = None
    # The current/actual status of the connection
    live_status: Optional[ConnectivityStatus] = None
    # The states of the sources the of the connection
    source_status: Optional[list[ResourceStatus]] = None
    # The states of the ssh tunnel the of the connection
    ssh_tunnel_status: Optional[list[ResourceStatus]] = None
    # The states of the targets the of the connection
    target_status: Optional[list[ResourceStatus]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ConnectionStatus:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ConnectionStatus
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ConnectionStatus()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .connectivity_status import ConnectivityStatus
        from .resource_status import ResourceStatus

        from .connectivity_status import ConnectivityStatus
        from .resource_status import ResourceStatus

        fields: dict[str, Callable[[Any], None]] = {
            "clientStatus": lambda n : setattr(self, 'client_status', n.get_collection_of_object_values(ResourceStatus)),
            "connectedSince": lambda n : setattr(self, 'connected_since', n.get_str_value()),
            "connectionId": lambda n : setattr(self, 'connection_id', n.get_str_value()),
            "connectionStatus": lambda n : setattr(self, 'connection_status', n.get_enum_value(ConnectivityStatus)),
            "liveStatus": lambda n : setattr(self, 'live_status', n.get_enum_value(ConnectivityStatus)),
            "sourceStatus": lambda n : setattr(self, 'source_status', n.get_collection_of_object_values(ResourceStatus)),
            "sshTunnelStatus": lambda n : setattr(self, 'ssh_tunnel_status', n.get_collection_of_object_values(ResourceStatus)),
            "targetStatus": lambda n : setattr(self, 'target_status', n.get_collection_of_object_values(ResourceStatus)),
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
        writer.write_collection_of_object_values("clientStatus", self.client_status)
        writer.write_str_value("connectedSince", self.connected_since)
        writer.write_str_value("connectionId", self.connection_id)
        writer.write_enum_value("connectionStatus", self.connection_status)
        writer.write_enum_value("liveStatus", self.live_status)
        writer.write_collection_of_object_values("sourceStatus", self.source_status)
        writer.write_collection_of_object_values("sshTunnelStatus", self.ssh_tunnel_status)
        writer.write_collection_of_object_values("targetStatus", self.target_status)
        writer.write_additional_data_value(self.additional_data)
    

