from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class Source_enforcement(AdditionalDataHolder, Parsable):
    """
    Defines an enforcement for this source to make sure that a device can only access its associated Thing.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # An array of filters. One of the defined filters must match the input value from the message otherwise the message is rejected.
    filters: Optional[list[str]] = None
    # The input value of the enforcement that should identify the origin of the message (e.g. adevice id). You can use placeholders within this field depending on the connection type. E.g. for AMQP1.0 connections you can use `{{ header:[any-header-name] }}` to resolve the value from a message header.
    input: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> Source_enforcement:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: Source_enforcement
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return Source_enforcement()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "filters": lambda n : setattr(self, 'filters', n.get_collection_of_primitive_values(str)),
            "input": lambda n : setattr(self, 'input', n.get_str_value()),
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
        writer.write_collection_of_primitive_values("filters", self.filters)
        writer.write_str_value("input", self.input)
        writer.write_additional_data_value(self.additional_data)
    

