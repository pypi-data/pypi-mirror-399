from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from warnings import warn

@dataclass
class MappingContext(AdditionalDataHolder, Parsable):
    """
    MappingContext to apply in this connection containing JavaScript scripts mapping from external messages tointernal Ditto Protocol messages. Usage of MappingContext is deprecated, use PayloadMappingDefinitions instead.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The mapping script for incoming messages
    incoming_script: Optional[str] = None
    # Whether or not ByteBufferJS library should be included
    load_bytebuffer_j_s: Optional[bool] = None
    # Whether or not LongJS library should be included
    load_long_j_s: Optional[bool] = None
    # The mapping script for outgoing messages
    outgoing_script: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> MappingContext:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: MappingContext
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return MappingContext()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "incomingScript": lambda n : setattr(self, 'incoming_script', n.get_str_value()),
            "loadBytebufferJS": lambda n : setattr(self, 'load_bytebuffer_j_s', n.get_bool_value()),
            "loadLongJS": lambda n : setattr(self, 'load_long_j_s', n.get_bool_value()),
            "outgoingScript": lambda n : setattr(self, 'outgoing_script', n.get_str_value()),
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
        writer.write_str_value("incomingScript", self.incoming_script)
        writer.write_bool_value("loadBytebufferJS", self.load_bytebuffer_j_s)
        writer.write_bool_value("loadLongJS", self.load_long_j_s)
        writer.write_str_value("outgoingScript", self.outgoing_script)
        writer.write_additional_data_value(self.additional_data)
    

