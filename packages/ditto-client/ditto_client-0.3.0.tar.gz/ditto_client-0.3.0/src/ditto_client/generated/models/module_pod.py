from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .module_pod_logger_configs import Module_pod_loggerConfigs

@dataclass
class Module_pod(AdditionalDataHolder, Parsable):
    """
    Details of logging configuration
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # instance of module
    instance: Optional[str] = None
    # The loggerConfigs property
    logger_configs: Optional[list[Module_pod_loggerConfigs]] = None
    # name of service
    service_name: Optional[str] = None
    # The HTTP status
    status: Optional[int] = None
    # devops.responses:retrieveLoggerConfig
    type: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> Module_pod:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: Module_pod
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return Module_pod()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .module_pod_logger_configs import Module_pod_loggerConfigs

        from .module_pod_logger_configs import Module_pod_loggerConfigs

        fields: dict[str, Callable[[Any], None]] = {
            "instance": lambda n : setattr(self, 'instance', n.get_str_value()),
            "loggerConfigs": lambda n : setattr(self, 'logger_configs', n.get_collection_of_object_values(Module_pod_loggerConfigs)),
            "serviceName": lambda n : setattr(self, 'service_name', n.get_str_value()),
            "status": lambda n : setattr(self, 'status', n.get_int_value()),
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
        writer.write_collection_of_object_values("loggerConfigs", self.logger_configs)
        writer.write_str_value("serviceName", self.service_name)
        writer.write_int_value("status", self.status)
        writer.write_str_value("type", self.type)
        writer.write_additional_data_value(self.additional_data)
    

