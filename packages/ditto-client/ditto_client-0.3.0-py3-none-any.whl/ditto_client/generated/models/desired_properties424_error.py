from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.api_error import APIError
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .desired_properties424_error_acknowledgement_label1 import DesiredProperties424Error_acknowledgementLabel1

@dataclass
class DesiredProperties424Error(APIError, AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The acknowledgementLabel1 property
    acknowledgement_label1: Optional[DesiredProperties424Error_acknowledgementLabel1] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> DesiredProperties424Error:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: DesiredProperties424Error
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return DesiredProperties424Error()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .desired_properties424_error_acknowledgement_label1 import DesiredProperties424Error_acknowledgementLabel1

        from .desired_properties424_error_acknowledgement_label1 import DesiredProperties424Error_acknowledgementLabel1

        fields: dict[str, Callable[[Any], None]] = {
            "acknowledgementLabel1": lambda n : setattr(self, 'acknowledgement_label1', n.get_object_value(DesiredProperties424Error_acknowledgementLabel1)),
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
        writer.write_object_value("acknowledgementLabel1", self.acknowledgement_label1)
        writer.write_additional_data_value(self.additional_data)
    
    @property
    def primary_message(self) -> Optional[str]:
        """
        The primary error message.
        """
        return super().message

