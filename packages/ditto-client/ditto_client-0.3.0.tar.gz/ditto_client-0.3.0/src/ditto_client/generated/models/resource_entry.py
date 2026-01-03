from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .permission import Permission

@dataclass
class ResourceEntry(AdditionalDataHolder, Parsable):
    """
    Single (Authorization) Resource entry defining permissions per effect.Allowed effects are `grant` and `revoke`.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The grant property
    grant: Optional[list[Permission]] = None
    # The revoke property
    revoke: Optional[list[Permission]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ResourceEntry:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ResourceEntry
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ResourceEntry()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .permission import Permission

        from .permission import Permission

        fields: dict[str, Callable[[Any], None]] = {
            "grant": lambda n : setattr(self, 'grant', n.get_collection_of_enum_values(Permission)),
            "revoke": lambda n : setattr(self, 'revoke', n.get_collection_of_enum_values(Permission)),
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
        writer.write_collection_of_enum_values("grant", self.grant)
        writer.write_collection_of_enum_values("revoke", self.revoke)
        writer.write_additional_data_value(self.additional_data)
    

