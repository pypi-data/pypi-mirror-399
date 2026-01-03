from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class SingleMetric(AdditionalDataHolder, Parsable):
    """
    Contains a single metric consisting of several time intervals and counter values for those intervals including the last message date.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The timestamp when the last message was processed
    last_message_at: Optional[str] = None
    # The counter containing how many messages were processed in the last hour
    p_t1_h: Optional[int] = None
    # The counter containing how many messages were processed in the last minute
    p_t1_m: Optional[int] = None
    # The counter containing how many messages were processed in the last 24 hours / last day
    p_t24_h: Optional[int] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> SingleMetric:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: SingleMetric
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return SingleMetric()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "lastMessageAt": lambda n : setattr(self, 'last_message_at', n.get_str_value()),
            "PT1H": lambda n : setattr(self, 'p_t1_h', n.get_int_value()),
            "PT1M": lambda n : setattr(self, 'p_t1_m', n.get_int_value()),
            "PT24H": lambda n : setattr(self, 'p_t24_h', n.get_int_value()),
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
        writer.write_str_value("lastMessageAt", self.last_message_at)
        writer.write_int_value("PT1H", self.p_t1_h)
        writer.write_int_value("PT1M", self.p_t1_m)
        writer.write_int_value("PT24H", self.p_t24_h)
        writer.write_additional_data_value(self.additional_data)
    

