from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .overall_connection_metrics import OverallConnectionMetrics
    from .source_metrics import SourceMetrics
    from .target_metrics import TargetMetrics

@dataclass
class ConnectionMetrics(AdditionalDataHolder, Parsable):
    """
    Metrics of a connection
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The connection ID
    connection_id: Optional[str] = None
    # Overall metrics of the connection
    connection_metrics: Optional[OverallConnectionMetrics] = None
    # Whether the connection metrics contains any failures
    contains_failures: Optional[bool] = None
    # Source metrics of the connection
    source_metrics: Optional[SourceMetrics] = None
    # Target metrics of the connection
    target_metrics: Optional[TargetMetrics] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ConnectionMetrics:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ConnectionMetrics
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ConnectionMetrics()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .overall_connection_metrics import OverallConnectionMetrics
        from .source_metrics import SourceMetrics
        from .target_metrics import TargetMetrics

        from .overall_connection_metrics import OverallConnectionMetrics
        from .source_metrics import SourceMetrics
        from .target_metrics import TargetMetrics

        fields: dict[str, Callable[[Any], None]] = {
            "connectionId": lambda n : setattr(self, 'connection_id', n.get_str_value()),
            "connectionMetrics": lambda n : setattr(self, 'connection_metrics', n.get_object_value(OverallConnectionMetrics)),
            "containsFailures": lambda n : setattr(self, 'contains_failures', n.get_bool_value()),
            "sourceMetrics": lambda n : setattr(self, 'source_metrics', n.get_object_value(SourceMetrics)),
            "targetMetrics": lambda n : setattr(self, 'target_metrics', n.get_object_value(TargetMetrics)),
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
        writer.write_str_value("connectionId", self.connection_id)
        writer.write_object_value("connectionMetrics", self.connection_metrics)
        writer.write_bool_value("containsFailures", self.contains_failures)
        writer.write_object_value("sourceMetrics", self.source_metrics)
        writer.write_object_value("targetMetrics", self.target_metrics)
        writer.write_additional_data_value(self.additional_data)
    

