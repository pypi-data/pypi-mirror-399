from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .policy_entry import PolicyEntry

@dataclass
class PolicyEntries(AdditionalDataHolder, Parsable):
    """
    Policy entries containing one policy entry for each arbitrary `label` key
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Single policy entry containing Subjects and Resources.
    label_n: Optional[PolicyEntry] = None
    # Single policy entry containing Subjects and Resources.
    label1: Optional[PolicyEntry] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> PolicyEntries:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: PolicyEntries
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return PolicyEntries()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .policy_entry import PolicyEntry

        from .policy_entry import PolicyEntry

        fields: dict[str, Callable[[Any], None]] = {
            "labelN": lambda n : setattr(self, 'label_n', n.get_object_value(PolicyEntry)),
            "label1": lambda n : setattr(self, 'label1', n.get_object_value(PolicyEntry)),
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
        writer.write_object_value("labelN", self.label_n)
        writer.write_object_value("label1", self.label1)
        writer.write_additional_data_value(self.additional_data)
    

