from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .module_config_service import ModuleConfigService

@dataclass
class RetrieveConfigService(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Module
    gateway: Optional[ModuleConfigService] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> RetrieveConfigService:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: RetrieveConfigService
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return RetrieveConfigService()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .module_config_service import ModuleConfigService

        from .module_config_service import ModuleConfigService

        fields: dict[str, Callable[[Any], None]] = {
            "gateway": lambda n : setattr(self, 'gateway', n.get_object_value(ModuleConfigService)),
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
        writer.write_object_value("gateway", self.gateway)
        writer.write_additional_data_value(self.additional_data)
    

