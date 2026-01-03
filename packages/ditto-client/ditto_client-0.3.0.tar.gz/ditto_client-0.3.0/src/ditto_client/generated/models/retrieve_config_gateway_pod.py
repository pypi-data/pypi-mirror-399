from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .retrieve_config_gateway_pod_config import RetrieveConfig_gateway_pod_config

@dataclass
class RetrieveConfig_gateway_pod(AdditionalDataHolder, Parsable):
    """
    Return the configuration at the path ditto.info
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # name of service
    config: Optional[RetrieveConfig_gateway_pod_config] = None
    # The HTTP status
    status: Optional[int] = None
    # devops.responses:ResultConfig
    type: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> RetrieveConfig_gateway_pod:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: RetrieveConfig_gateway_pod
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return RetrieveConfig_gateway_pod()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .retrieve_config_gateway_pod_config import RetrieveConfig_gateway_pod_config

        from .retrieve_config_gateway_pod_config import RetrieveConfig_gateway_pod_config

        fields: dict[str, Callable[[Any], None]] = {
            "config": lambda n : setattr(self, 'config', n.get_object_value(RetrieveConfig_gateway_pod_config)),
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
        writer.write_object_value("config", self.config)
        writer.write_int_value("status", self.status)
        writer.write_str_value("type", self.type)
        writer.write_additional_data_value(self.additional_data)
    

