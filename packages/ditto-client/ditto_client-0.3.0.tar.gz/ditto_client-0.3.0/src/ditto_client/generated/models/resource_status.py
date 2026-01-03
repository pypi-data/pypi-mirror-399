from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .connectivity_status import ConnectivityStatus
    from .resource_status_type import ResourceStatus_type

@dataclass
class ResourceStatus(AdditionalDataHolder, Parsable):
    """
    The status of a single resource (e.g. a client or a source/target resource)
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The address information of the resource (optional)
    address: Optional[str] = None
    # A client identifier where the resource is held (e.g. a cluster instance ID)
    client: Optional[str] = None
    # Date since when the resource is in the present state
    in_state_since: Optional[str] = None
    # The status of a connection or resource
    status: Optional[ConnectivityStatus] = None
    # Details to the status of the resource
    status_details: Optional[str] = None
    # The type of the resource
    type: Optional[ResourceStatus_type] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ResourceStatus:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ResourceStatus
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ResourceStatus()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .connectivity_status import ConnectivityStatus
        from .resource_status_type import ResourceStatus_type

        from .connectivity_status import ConnectivityStatus
        from .resource_status_type import ResourceStatus_type

        fields: dict[str, Callable[[Any], None]] = {
            "address": lambda n : setattr(self, 'address', n.get_str_value()),
            "client": lambda n : setattr(self, 'client', n.get_str_value()),
            "inStateSince": lambda n : setattr(self, 'in_state_since', n.get_str_value()),
            "status": lambda n : setattr(self, 'status', n.get_enum_value(ConnectivityStatus)),
            "statusDetails": lambda n : setattr(self, 'status_details', n.get_str_value()),
            "type": lambda n : setattr(self, 'type', n.get_enum_value(ResourceStatus_type)),
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
        writer.write_str_value("address", self.address)
        writer.write_str_value("client", self.client)
        writer.write_str_value("inStateSince", self.in_state_since)
        writer.write_enum_value("status", self.status)
        writer.write_str_value("statusDetails", self.status_details)
        writer.write_enum_value("type", self.type)
        writer.write_additional_data_value(self.additional_data)
    

