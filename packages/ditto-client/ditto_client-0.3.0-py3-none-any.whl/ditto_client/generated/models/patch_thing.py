from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .attributes import Attributes
    from .features import Features

@dataclass
class PatchThing(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # An arbitrary JSON object describing the attributes of a thing.
    attributes: Optional[Attributes] = None
    # A single fully qualified identifier of a definition in the form '<namespace>:<name>:<version>' or a valid HTTP(s) URL
    definition: Optional[str] = None
    # List of features where the key represents the `featureId` of each feature.The `featureId` key must be unique in the list.
    features: Optional[Features] = None
    # The ID of the policy which controls the access to this thing. policies are managed by resource `/policies/{policyId}`
    policy_id: Optional[str] = None
    # Unique identifier representing the thing
    thing_id: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> PatchThing:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: PatchThing
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return PatchThing()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .attributes import Attributes
        from .features import Features

        from .attributes import Attributes
        from .features import Features

        fields: dict[str, Callable[[Any], None]] = {
            "attributes": lambda n : setattr(self, 'attributes', n.get_object_value(Attributes)),
            "definition": lambda n : setattr(self, 'definition', n.get_str_value()),
            "features": lambda n : setattr(self, 'features', n.get_object_value(Features)),
            "policyId": lambda n : setattr(self, 'policy_id', n.get_str_value()),
            "thingId": lambda n : setattr(self, 'thing_id', n.get_str_value()),
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
        writer.write_object_value("attributes", self.attributes)
        writer.write_str_value("definition", self.definition)
        writer.write_object_value("features", self.features)
        writer.write_str_value("policyId", self.policy_id)
        writer.write_str_value("thingId", self.thing_id)
        writer.write_additional_data_value(self.additional_data)
    

