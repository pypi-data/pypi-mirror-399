from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .source_acknowledgement_requests import Source_acknowledgementRequests
    from .source_enforcement import Source_enforcement
    from .source_header_mapping import Source_headerMapping
    from .source_reply_target import Source_replyTarget

@dataclass
class Source(AdditionalDataHolder, Parsable):
    """
    A subscription source subscribed by this connection
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Contains requests to acknowledgements which must be fulfilled before a message consumed from this source is technically settled/ACKed at the e.g. message broker.
    acknowledgement_requests: Optional[Source_acknowledgementRequests] = None
    # The source addresses this connection consumes messages from. The "telemetry", "events","command_response" aliases should be used for connections of type "hono".
    addresses: Optional[list[str]] = None
    # The authorization context defines all authorization subjects associated for this source
    authorization_context: Optional[list[str]] = None
    # The number of consumers that should be attached to each source address
    consumer_count: Optional[int] = None
    # Defines an enforcement for this source to make sure that a device can only access its associated Thing.
    enforcement: Optional[Source_enforcement] = None
    # Ditto protocol headers computed from external headers and certain properties of the Ditto protocol messages created by payload mapping.
    header_mapping: Optional[Source_headerMapping] = None
    # A list of payload mappings that are applied to messages received via this source. If no payload mapping is specified the standard Ditto mapping is used as default.
    payload_mapping: Optional[list[str]] = None
    # Maximum Quality-of-Service level to request when subscribing for messages
    qos: Optional[int] = None
    # Configuration for sending responses of incoming commands.
    reply_target: Optional[Source_replyTarget] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> Source:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: Source
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return Source()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .source_acknowledgement_requests import Source_acknowledgementRequests
        from .source_enforcement import Source_enforcement
        from .source_header_mapping import Source_headerMapping
        from .source_reply_target import Source_replyTarget

        from .source_acknowledgement_requests import Source_acknowledgementRequests
        from .source_enforcement import Source_enforcement
        from .source_header_mapping import Source_headerMapping
        from .source_reply_target import Source_replyTarget

        fields: dict[str, Callable[[Any], None]] = {
            "acknowledgementRequests": lambda n : setattr(self, 'acknowledgement_requests', n.get_object_value(Source_acknowledgementRequests)),
            "addresses": lambda n : setattr(self, 'addresses', n.get_collection_of_primitive_values(str)),
            "authorizationContext": lambda n : setattr(self, 'authorization_context', n.get_collection_of_primitive_values(str)),
            "consumerCount": lambda n : setattr(self, 'consumer_count', n.get_int_value()),
            "enforcement": lambda n : setattr(self, 'enforcement', n.get_object_value(Source_enforcement)),
            "headerMapping": lambda n : setattr(self, 'header_mapping', n.get_object_value(Source_headerMapping)),
            "payloadMapping": lambda n : setattr(self, 'payload_mapping', n.get_collection_of_primitive_values(str)),
            "qos": lambda n : setattr(self, 'qos', n.get_int_value()),
            "replyTarget": lambda n : setattr(self, 'reply_target', n.get_object_value(Source_replyTarget)),
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
        writer.write_object_value("acknowledgementRequests", self.acknowledgement_requests)
        writer.write_collection_of_primitive_values("addresses", self.addresses)
        writer.write_collection_of_primitive_values("authorizationContext", self.authorization_context)
        writer.write_int_value("consumerCount", self.consumer_count)
        writer.write_object_value("enforcement", self.enforcement)
        writer.write_object_value("headerMapping", self.header_mapping)
        writer.write_collection_of_primitive_values("payloadMapping", self.payload_mapping)
        writer.write_int_value("qos", self.qos)
        writer.write_object_value("replyTarget", self.reply_target)
        writer.write_additional_data_value(self.additional_data)
    

