from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .log_category import LogCategory
    from .log_level import LogLevel
    from .log_type import LogType

@dataclass
class LogEntry(AdditionalDataHolder, Parsable):
    """
    Represents a log entry for a connection.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Connection address on which the log occurred.
    address: Optional[str] = None
    # A category to which the log entry can be referred to.
    category: Optional[LogCategory] = None
    # Correlation ID that is associated with the log entry.
    correlation_id: Optional[str] = None
    # Escalation level of a log entry.
    level: Optional[LogLevel] = None
    # The log message.
    message: Optional[str] = None
    # The thing for which the log entry was created.
    thing_id: Optional[str] = None
    # Timestamp of the log entry.
    timestamp: Optional[str] = None
    # The type of a log entry describing during what kind of activity the entry was created.
    type: Optional[LogType] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> LogEntry:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: LogEntry
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return LogEntry()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .log_category import LogCategory
        from .log_level import LogLevel
        from .log_type import LogType

        from .log_category import LogCategory
        from .log_level import LogLevel
        from .log_type import LogType

        fields: dict[str, Callable[[Any], None]] = {
            "address": lambda n : setattr(self, 'address', n.get_str_value()),
            "category": lambda n : setattr(self, 'category', n.get_enum_value(LogCategory)),
            "correlationId": lambda n : setattr(self, 'correlation_id', n.get_str_value()),
            "level": lambda n : setattr(self, 'level', n.get_enum_value(LogLevel)),
            "message": lambda n : setattr(self, 'message', n.get_str_value()),
            "thingId": lambda n : setattr(self, 'thing_id', n.get_str_value()),
            "timestamp": lambda n : setattr(self, 'timestamp', n.get_str_value()),
            "type": lambda n : setattr(self, 'type', n.get_enum_value(LogType)),
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
        writer.write_str_value("address", self.address)
        writer.write_enum_value("category", self.category)
        writer.write_str_value("correlationId", self.correlation_id)
        writer.write_enum_value("level", self.level)
        writer.write_str_value("message", self.message)
        writer.write_str_value("thingId", self.thing_id)
        writer.write_str_value("timestamp", self.timestamp)
        writer.write_enum_value("type", self.type)
        writer.write_additional_data_value(self.additional_data)
    

