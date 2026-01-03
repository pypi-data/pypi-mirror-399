from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .result_config_service_config_gateway_authentication_devops import ResultConfigService_config_gateway_authentication_devops

@dataclass
class ResultConfigService_config_gateway_authentication(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The devops property
    devops: Optional[ResultConfigService_config_gateway_authentication_devops] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ResultConfigService_config_gateway_authentication:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ResultConfigService_config_gateway_authentication
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ResultConfigService_config_gateway_authentication()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .result_config_service_config_gateway_authentication_devops import ResultConfigService_config_gateway_authentication_devops

        from .result_config_service_config_gateway_authentication_devops import ResultConfigService_config_gateway_authentication_devops

        fields: dict[str, Callable[[Any], None]] = {
            "devops": lambda n : setattr(self, 'devops', n.get_object_value(ResultConfigService_config_gateway_authentication_devops)),
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
        writer.write_object_value("devops", self.devops)
        writer.write_additional_data_value(self.additional_data)
    

