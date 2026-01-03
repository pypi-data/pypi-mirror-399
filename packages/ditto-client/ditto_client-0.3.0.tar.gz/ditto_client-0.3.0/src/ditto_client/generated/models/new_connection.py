from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from warnings import warn

if TYPE_CHECKING:
    from .connection_type import ConnectionType
    from .connectivity_status import ConnectivityStatus
    from .mapping_context import MappingContext
    from .new_connection_specific_config import NewConnection_specificConfig
    from .new_connection_ssh_tunnel import NewConnection_sshTunnel
    from .payload_mapping_definitions import PayloadMappingDefinitions
    from .source import Source
    from .target import Target

@dataclass
class NewConnection(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # How many clients on different cluster nodes should establish the connection
    client_count: Optional[float] = None
    # The status of a connection or resource
    connection_status: Optional[ConnectivityStatus] = None
    # The type of a connection
    connection_type: Optional[ConnectionType] = None
    # Whether or not failover is enabled for this connection
    failover_enabled: Optional[bool] = None
    # MappingContext to apply in this connection containing JavaScript scripts mapping from external messages tointernal Ditto Protocol messages. Usage of MappingContext is deprecated, use PayloadMappingDefinitions instead.
    mapping_context: Optional[MappingContext] = None
    # List of mapping definitions where the key represents the ID of each mapping that can be used in sources andtargets to reference a mapping.
    mapping_definitions: Optional[PayloadMappingDefinitions] = None
    # The name of the connection
    name: Optional[str] = None
    # The subscription sources of this connection
    sources: Optional[list[Source]] = None
    # Configuration which is only applicable for a specific connection type
    specific_config: Optional[NewConnection_specificConfig] = None
    # The configuration of a local SSH port forwarding used to tunnel the connection to the actual endpoint.
    ssh_tunnel: Optional[NewConnection_sshTunnel] = None
    # The tags of the connection
    tags: Optional[list[str]] = None
    # The publish targets of this connection
    targets: Optional[list[Target]] = None
    # The URI of the connection
    uri: Optional[str] = None
    # Whether or not to validate server certificates on connection establishment
    validate_certificates: Optional[bool] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> NewConnection:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: NewConnection
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return NewConnection()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .connection_type import ConnectionType
        from .connectivity_status import ConnectivityStatus
        from .mapping_context import MappingContext
        from .new_connection_specific_config import NewConnection_specificConfig
        from .new_connection_ssh_tunnel import NewConnection_sshTunnel
        from .payload_mapping_definitions import PayloadMappingDefinitions
        from .source import Source
        from .target import Target

        from .connection_type import ConnectionType
        from .connectivity_status import ConnectivityStatus
        from .mapping_context import MappingContext
        from .new_connection_specific_config import NewConnection_specificConfig
        from .new_connection_ssh_tunnel import NewConnection_sshTunnel
        from .payload_mapping_definitions import PayloadMappingDefinitions
        from .source import Source
        from .target import Target

        fields: dict[str, Callable[[Any], None]] = {
            "clientCount": lambda n : setattr(self, 'client_count', n.get_float_value()),
            "connectionStatus": lambda n : setattr(self, 'connection_status', n.get_enum_value(ConnectivityStatus)),
            "connectionType": lambda n : setattr(self, 'connection_type', n.get_enum_value(ConnectionType)),
            "failoverEnabled": lambda n : setattr(self, 'failover_enabled', n.get_bool_value()),
            "mappingContext": lambda n : setattr(self, 'mapping_context', n.get_object_value(MappingContext)),
            "mappingDefinitions": lambda n : setattr(self, 'mapping_definitions', n.get_object_value(PayloadMappingDefinitions)),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "sources": lambda n : setattr(self, 'sources', n.get_collection_of_object_values(Source)),
            "specificConfig": lambda n : setattr(self, 'specific_config', n.get_object_value(NewConnection_specificConfig)),
            "sshTunnel": lambda n : setattr(self, 'ssh_tunnel', n.get_object_value(NewConnection_sshTunnel)),
            "tags": lambda n : setattr(self, 'tags', n.get_collection_of_primitive_values(str)),
            "targets": lambda n : setattr(self, 'targets', n.get_collection_of_object_values(Target)),
            "uri": lambda n : setattr(self, 'uri', n.get_str_value()),
            "validateCertificates": lambda n : setattr(self, 'validate_certificates', n.get_bool_value()),
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
        writer.write_float_value("clientCount", self.client_count)
        writer.write_enum_value("connectionStatus", self.connection_status)
        writer.write_enum_value("connectionType", self.connection_type)
        writer.write_bool_value("failoverEnabled", self.failover_enabled)
        writer.write_object_value("mappingContext", self.mapping_context)
        writer.write_object_value("mappingDefinitions", self.mapping_definitions)
        writer.write_str_value("name", self.name)
        writer.write_collection_of_object_values("sources", self.sources)
        writer.write_object_value("specificConfig", self.specific_config)
        writer.write_object_value("sshTunnel", self.ssh_tunnel)
        writer.write_collection_of_primitive_values("tags", self.tags)
        writer.write_collection_of_object_values("targets", self.targets)
        writer.write_str_value("uri", self.uri)
        writer.write_bool_value("validateCertificates", self.validate_certificates)
        writer.write_additional_data_value(self.additional_data)
    

