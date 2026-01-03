from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .typed_metric import TypedMetric

@dataclass
class InboundMetrics(AdditionalDataHolder, Parsable):
    """
    Metrics of an inbound (e.g. a Source) resource
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Contains from external sources consumed metric counts
    consumed: Optional[TypedMetric] = None
    # Contains dropped (in the payload mapping) messages metric counts
    dropped: Optional[TypedMetric] = None
    # Contains enforced (e.g. source address enforcement) messages metric counts
    enforced: Optional[TypedMetric] = None
    # Contains mapped (payload mapping) messages metric counts
    mapped: Optional[TypedMetric] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> InboundMetrics:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: InboundMetrics
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return InboundMetrics()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .typed_metric import TypedMetric

        from .typed_metric import TypedMetric

        fields: dict[str, Callable[[Any], None]] = {
            "consumed": lambda n : setattr(self, 'consumed', n.get_object_value(TypedMetric)),
            "dropped": lambda n : setattr(self, 'dropped', n.get_object_value(TypedMetric)),
            "enforced": lambda n : setattr(self, 'enforced', n.get_object_value(TypedMetric)),
            "mapped": lambda n : setattr(self, 'mapped', n.get_object_value(TypedMetric)),
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
        writer.write_object_value("consumed", self.consumed)
        writer.write_object_value("dropped", self.dropped)
        writer.write_object_value("enforced", self.enforced)
        writer.write_object_value("mapped", self.mapped)
        writer.write_additional_data_value(self.additional_data)
    

