from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .inbound_metrics import InboundMetrics
    from .outbound_metrics import OutboundMetrics

@dataclass
class OverallConnectionMetrics(AdditionalDataHolder, Parsable):
    """
    Overall metrics of the connection
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Metrics of an inbound (e.g. a Source) resource
    inbound: Optional[InboundMetrics] = None
    # Metrics of an outbound (e.g. a Target) resource
    outbound: Optional[OutboundMetrics] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> OverallConnectionMetrics:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: OverallConnectionMetrics
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return OverallConnectionMetrics()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .inbound_metrics import InboundMetrics
        from .outbound_metrics import OutboundMetrics

        from .inbound_metrics import InboundMetrics
        from .outbound_metrics import OutboundMetrics

        fields: dict[str, Callable[[Any], None]] = {
            "inbound": lambda n : setattr(self, 'inbound', n.get_object_value(InboundMetrics)),
            "outbound": lambda n : setattr(self, 'outbound', n.get_object_value(OutboundMetrics)),
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
        writer.write_object_value("inbound", self.inbound)
        writer.write_object_value("outbound", self.outbound)
        writer.write_additional_data_value(self.additional_data)
    

