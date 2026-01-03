from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .cloudevents_post_request_body_headers import CloudeventsPostRequestBody_headers
    from .cloudevents_post_request_body_value import CloudeventsPostRequestBody_value

@dataclass
class CloudeventsPostRequestBody(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Additional headers.
    headers: Optional[CloudeventsPostRequestBody_headers] = None
    # References the part of a Thing which is affected by this message.
    path: Optional[str] = None
    # Contains information about the contents of the payload:* the affected Thing (namespace and Thing ID)* the type of operation (command/event, create/retrieve/modify/delete)
    topic: Optional[str] = None
    # The `value` field contains the actual payload e.g. a sensor value.
    value: Optional[CloudeventsPostRequestBody_value] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> CloudeventsPostRequestBody:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: CloudeventsPostRequestBody
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return CloudeventsPostRequestBody()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .cloudevents_post_request_body_headers import CloudeventsPostRequestBody_headers
        from .cloudevents_post_request_body_value import CloudeventsPostRequestBody_value

        from .cloudevents_post_request_body_headers import CloudeventsPostRequestBody_headers
        from .cloudevents_post_request_body_value import CloudeventsPostRequestBody_value

        fields: dict[str, Callable[[Any], None]] = {
            "headers": lambda n : setattr(self, 'headers', n.get_object_value(CloudeventsPostRequestBody_headers)),
            "path": lambda n : setattr(self, 'path', n.get_str_value()),
            "topic": lambda n : setattr(self, 'topic', n.get_str_value()),
            "value": lambda n : setattr(self, 'value', n.get_object_value(CloudeventsPostRequestBody_value)),
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
        writer.write_object_value("headers", self.headers)
        writer.write_str_value("path", self.path)
        writer.write_str_value("topic", self.topic)
        writer.write_object_value("value", self.value)
        writer.write_additional_data_value(self.additional_data)
    

