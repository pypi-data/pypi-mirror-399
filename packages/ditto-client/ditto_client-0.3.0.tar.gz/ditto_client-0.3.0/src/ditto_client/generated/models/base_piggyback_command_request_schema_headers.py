from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class BasePiggybackCommandRequestSchema_headers(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The aggregate property
    aggregate: Optional[bool] = None
    # The isGroupTopic property
    is_group_topic: Optional[bool] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> BasePiggybackCommandRequestSchema_headers:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: BasePiggybackCommandRequestSchema_headers
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return BasePiggybackCommandRequestSchema_headers()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "aggregate": lambda n : setattr(self, 'aggregate', n.get_bool_value()),
            "is-group-topic": lambda n : setattr(self, 'is_group_topic', n.get_bool_value()),
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
        writer.write_bool_value("aggregate", self.aggregate)
        writer.write_bool_value("is-group-topic", self.is_group_topic)
        writer.write_additional_data_value(self.additional_data)
    

