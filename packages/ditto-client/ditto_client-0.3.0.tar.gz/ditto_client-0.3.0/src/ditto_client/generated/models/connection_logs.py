from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .log_entry import LogEntry

@dataclass
class ConnectionLogs(AdditionalDataHolder, Parsable):
    """
    Log entries of a connection.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # ID of the connection for which the log entries were logged.
    connection_id: Optional[str] = None
    # Log entries for the connection.
    connection_logs: Optional[list[LogEntry]] = None
    # Since when logging is enabled. Might be missing / null if logging is not enabled.
    enabled_since: Optional[str] = None
    # Until when logging is enabled. Might be missing / null if logging is not enabled.
    enabled_until: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ConnectionLogs:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ConnectionLogs
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ConnectionLogs()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .log_entry import LogEntry

        from .log_entry import LogEntry

        fields: dict[str, Callable[[Any], None]] = {
            "connectionId": lambda n : setattr(self, 'connection_id', n.get_str_value()),
            "connectionLogs": lambda n : setattr(self, 'connection_logs', n.get_collection_of_object_values(LogEntry)),
            "enabledSince": lambda n : setattr(self, 'enabled_since', n.get_str_value()),
            "enabledUntil": lambda n : setattr(self, 'enabled_until', n.get_str_value()),
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
        writer.write_collection_of_object_values("connectionLogs", self.connection_logs)
        writer.write_str_value("enabledSince", self.enabled_since)
        writer.write_str_value("enabledUntil", self.enabled_until)
        writer.write_additional_data_value(self.additional_data)
    

