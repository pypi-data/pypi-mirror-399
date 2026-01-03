from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .retrieve_config_gateway_pod_config_env import RetrieveConfig_gateway_pod_config_env
    from .retrieve_config_gateway_pod_config_service import RetrieveConfig_gateway_pod_config_service

@dataclass
class RetrieveConfig_gateway_pod_config(AdditionalDataHolder, Parsable):
    """
    name of service
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The env property
    env: Optional[RetrieveConfig_gateway_pod_config_env] = None
    # The service property
    service: Optional[RetrieveConfig_gateway_pod_config_service] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> RetrieveConfig_gateway_pod_config:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: RetrieveConfig_gateway_pod_config
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return RetrieveConfig_gateway_pod_config()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .retrieve_config_gateway_pod_config_env import RetrieveConfig_gateway_pod_config_env
        from .retrieve_config_gateway_pod_config_service import RetrieveConfig_gateway_pod_config_service

        from .retrieve_config_gateway_pod_config_env import RetrieveConfig_gateway_pod_config_env
        from .retrieve_config_gateway_pod_config_service import RetrieveConfig_gateway_pod_config_service

        fields: dict[str, Callable[[Any], None]] = {
            "env": lambda n : setattr(self, 'env', n.get_object_value(RetrieveConfig_gateway_pod_config_env)),
            "service": lambda n : setattr(self, 'service', n.get_object_value(RetrieveConfig_gateway_pod_config_service)),
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
        writer.write_object_value("env", self.env)
        writer.write_object_value("service", self.service)
        writer.write_additional_data_value(self.additional_data)
    

