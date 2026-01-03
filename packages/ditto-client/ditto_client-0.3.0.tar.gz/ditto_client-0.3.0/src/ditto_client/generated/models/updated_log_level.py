from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class UpdatedLogLevel(AdditionalDataHolder, Parsable):
    """
    Details of logging configuration
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # identifier of pod instance
    instance: Optional[str] = None
    # name of service that has been updated
    service_name: Optional[str] = None
    # http code 200 for success operation
    status: Optional[int] = None
    # outcome of the change
    successfull: Optional[bool] = None
    # devops.responses:changeLogLevel
    type: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> UpdatedLogLevel:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: UpdatedLogLevel
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return UpdatedLogLevel()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "instance": lambda n : setattr(self, 'instance', n.get_str_value()),
            "serviceName": lambda n : setattr(self, 'service_name', n.get_str_value()),
            "status": lambda n : setattr(self, 'status', n.get_int_value()),
            "successfull": lambda n : setattr(self, 'successfull', n.get_bool_value()),
            "type": lambda n : setattr(self, 'type', n.get_str_value()),
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
        writer.write_str_value("instance", self.instance)
        writer.write_str_value("serviceName", self.service_name)
        writer.write_int_value("status", self.status)
        writer.write_bool_value("successfull", self.successfull)
        writer.write_str_value("type", self.type)
        writer.write_additional_data_value(self.additional_data)
    

