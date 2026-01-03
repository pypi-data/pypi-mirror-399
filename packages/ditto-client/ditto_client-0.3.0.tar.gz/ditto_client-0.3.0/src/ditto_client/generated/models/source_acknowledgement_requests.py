from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class Source_acknowledgementRequests(Parsable):
    """
    Contains requests to acknowledgements which must be fulfilled before a message consumed from this source is technically settled/ACKed at the e.g. message broker.
    """
    # Optional filter to be applied to the requested acknowledgements - takes an `fn:filter()` function expression
    filter: Optional[str] = None
    # Acknowledgement requests to be included for each message consumed by this source.
    includes: Optional[list[str]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> Source_acknowledgementRequests:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: Source_acknowledgementRequests
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return Source_acknowledgementRequests()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "filter": lambda n : setattr(self, 'filter', n.get_str_value()),
            "includes": lambda n : setattr(self, 'includes', n.get_collection_of_primitive_values(str)),
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
        writer.write_str_value("filter", self.filter)
        writer.write_collection_of_primitive_values("includes", self.includes)
    

