from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .target_header_mapping import Target_headerMapping
    from .target_topics import Target_topics

@dataclass
class Target(AdditionalDataHolder, Parsable):
    """
    A publish target served by this connection
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The target address where events, commands and messages are published to.The following placeholders are allowed within the target address:* Thing ID: `{{ thing:id }}`* Thing Namespace: `{{ thing:namespace }}`* Thing Name: `{{ thing:name }}` (the part of the ID without the namespace)NOTE Use "command" alias for connections of type "hono".
    address: Optional[str] = None
    # The authorization context defines all authorization subjects associated for this target
    authorization_context: Optional[list[str]] = None
    # External headers computed from headers and other properties of Ditto protocol messages.
    header_mapping: Optional[Target_headerMapping] = None
    # The optional label of an acknowledgement which should automatically be issued by this target based on the technical settlement/ACK the connection channel provides.
    issued_acknowledgement_label: Optional[str] = None
    # A list of payload mappings that are applied to messages sent via this target. If no payload mapping is specified the standard Ditto mapping is used as default.
    payload_mapping: Optional[list[str]] = None
    # Maximum Quality-of-Service level to request when subscribing for messages
    qos: Optional[int] = None
    # The topics to which this target is registered for
    topics: Optional[list[Target_topics]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> Target:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: Target
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return Target()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .target_header_mapping import Target_headerMapping
        from .target_topics import Target_topics

        from .target_header_mapping import Target_headerMapping
        from .target_topics import Target_topics

        fields: dict[str, Callable[[Any], None]] = {
            "address": lambda n : setattr(self, 'address', n.get_str_value()),
            "authorizationContext": lambda n : setattr(self, 'authorization_context', n.get_collection_of_primitive_values(str)),
            "headerMapping": lambda n : setattr(self, 'header_mapping', n.get_object_value(Target_headerMapping)),
            "issuedAcknowledgementLabel": lambda n : setattr(self, 'issued_acknowledgement_label', n.get_str_value()),
            "payloadMapping": lambda n : setattr(self, 'payload_mapping', n.get_collection_of_primitive_values(str)),
            "qos": lambda n : setattr(self, 'qos', n.get_int_value()),
            "topics": lambda n : setattr(self, 'topics', n.get_collection_of_enum_values(Target_topics)),
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
        writer.write_collection_of_primitive_values("authorizationContext", self.authorization_context)
        writer.write_object_value("headerMapping", self.header_mapping)
        writer.write_str_value("issuedAcknowledgementLabel", self.issued_acknowledgement_label)
        writer.write_collection_of_primitive_values("payloadMapping", self.payload_mapping)
        writer.write_int_value("qos", self.qos)
        writer.write_collection_of_enum_values("topics", self.topics)
        writer.write_additional_data_value(self.additional_data)
    

