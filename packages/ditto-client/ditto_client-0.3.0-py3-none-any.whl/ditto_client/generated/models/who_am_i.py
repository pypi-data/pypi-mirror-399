from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class WhoAmI(AdditionalDataHolder, Parsable):
    """
    Contains information about the current user and the auth subjects available for the used authentication.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # An auth subject that can be used to provide access for a caller (e.g. in subject entries of policies).
    default_subject: Optional[str] = None
    # The subjects property
    subjects: Optional[list[str]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> WhoAmI:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: WhoAmI
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return WhoAmI()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "defaultSubject": lambda n : setattr(self, 'default_subject', n.get_str_value()),
            "subjects": lambda n : setattr(self, 'subjects', n.get_collection_of_primitive_values(str)),
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
        writer.write_str_value("defaultSubject", self.default_subject)
        writer.write_collection_of_primitive_values("subjects", self.subjects)
        writer.write_additional_data_value(self.additional_data)
    

