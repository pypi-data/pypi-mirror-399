from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .feature_desired_properties import FeatureDesiredProperties
    from .feature_properties import FeatureProperties

@dataclass
class Feature(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The definitions of a feature.
    definition: Optional[list[str]] = None
    # An arbitrary JSON object describing the desired properties of a feature.
    desired_properties: Optional[FeatureDesiredProperties] = None
    # An arbitrary JSON object describing the properties of a feature.
    properties: Optional[FeatureProperties] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> Feature:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: Feature
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return Feature()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .feature_desired_properties import FeatureDesiredProperties
        from .feature_properties import FeatureProperties

        from .feature_desired_properties import FeatureDesiredProperties
        from .feature_properties import FeatureProperties

        fields: dict[str, Callable[[Any], None]] = {
            "definition": lambda n : setattr(self, 'definition', n.get_collection_of_primitive_values(str)),
            "desiredProperties": lambda n : setattr(self, 'desired_properties', n.get_object_value(FeatureDesiredProperties)),
            "properties": lambda n : setattr(self, 'properties', n.get_object_value(FeatureProperties)),
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
        writer.write_collection_of_primitive_values("definition", self.definition)
        writer.write_object_value("desiredProperties", self.desired_properties)
        writer.write_object_value("properties", self.properties)
        writer.write_additional_data_value(self.additional_data)
    

