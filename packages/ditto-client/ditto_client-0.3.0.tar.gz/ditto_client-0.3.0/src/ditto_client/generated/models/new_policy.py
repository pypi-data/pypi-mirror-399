from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .policy_entries import PolicyEntries

@dataclass
class NewPolicy(AdditionalDataHolder, Parsable):
    """
    Policy consisting of policy entries
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Policy entries containing one policy entry for each arbitrary `label` key
    entries: Optional[PolicyEntries] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> NewPolicy:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: NewPolicy
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return NewPolicy()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .policy_entries import PolicyEntries

        from .policy_entries import PolicyEntries

        fields: dict[str, Callable[[Any], None]] = {
            "entries": lambda n : setattr(self, 'entries', n.get_object_value(PolicyEntries)),
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
        writer.write_object_value("entries", self.entries)
        writer.write_additional_data_value(self.additional_data)
    

