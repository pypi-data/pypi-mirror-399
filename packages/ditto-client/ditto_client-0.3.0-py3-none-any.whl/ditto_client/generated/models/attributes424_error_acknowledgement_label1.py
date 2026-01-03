from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .attributes424_error_acknowledgement_label1_payload import Attributes424Error_acknowledgementLabel1_payload

@dataclass
class Attributes424Error_acknowledgementLabel1(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The payload of the acknowledgement
    payload: Optional[Attributes424Error_acknowledgementLabel1_payload] = None
    # The HTTP status of the acknowledgement
    status: Optional[int] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> Attributes424Error_acknowledgementLabel1:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: Attributes424Error_acknowledgementLabel1
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return Attributes424Error_acknowledgementLabel1()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .attributes424_error_acknowledgement_label1_payload import Attributes424Error_acknowledgementLabel1_payload

        from .attributes424_error_acknowledgement_label1_payload import Attributes424Error_acknowledgementLabel1_payload

        fields: dict[str, Callable[[Any], None]] = {
            "payload": lambda n : setattr(self, 'payload', n.get_object_value(Attributes424Error_acknowledgementLabel1_payload)),
            "status": lambda n : setattr(self, 'status', n.get_int_value()),
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
        writer.write_object_value("payload", self.payload)
        writer.write_int_value("status", self.status)
        writer.write_additional_data_value(self.additional_data)
    

