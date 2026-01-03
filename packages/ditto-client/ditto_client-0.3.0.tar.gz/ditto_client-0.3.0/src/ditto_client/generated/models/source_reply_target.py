from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .source_reply_target_expected_response_types import Source_replyTarget_expectedResponseTypes
    from .source_reply_target_header_mapping import Source_replyTarget_headerMapping

@dataclass
class Source_replyTarget(Parsable):
    """
    Configuration for sending responses of incoming commands.
    """
    # The target address where responses of incoming commands from the parent source are published to.The following placeholders are allowed within the target address:* Thing ID: `{{ thing:id }}`* Thing Namespace: `{{ thing:namespace }}`* Thing Name: `{{ thing:name }}` (the part of the ID without the namespace)* Ditto protocol topic attribute: `{{ topic:[topic-placeholder-attr] }}`* Ditto protocol header value: `{{ header:[any-header-name] }}`If placeholder resolution fails for a response, then the response is dropped.NOTE Use "command" alias for connections of type "hono".
    address: Optional[str] = None
    # Whether reply target is enabled.
    enabled: Optional[bool] = None
    # Contains a list of response types that should be published to the reply target.
    expected_response_types: Optional[list[Source_replyTarget_expectedResponseTypes]] = None
    # External headers computed from headers and other properties of Ditto protocol messages.
    header_mapping: Optional[Source_replyTarget_headerMapping] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> Source_replyTarget:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: Source_replyTarget
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return Source_replyTarget()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .source_reply_target_expected_response_types import Source_replyTarget_expectedResponseTypes
        from .source_reply_target_header_mapping import Source_replyTarget_headerMapping

        from .source_reply_target_expected_response_types import Source_replyTarget_expectedResponseTypes
        from .source_reply_target_header_mapping import Source_replyTarget_headerMapping

        fields: dict[str, Callable[[Any], None]] = {
            "address": lambda n : setattr(self, 'address', n.get_str_value()),
            "enabled": lambda n : setattr(self, 'enabled', n.get_bool_value()),
            "expectedResponseTypes": lambda n : setattr(self, 'expected_response_types', n.get_collection_of_enum_values(Source_replyTarget_expectedResponseTypes)),
            "headerMapping": lambda n : setattr(self, 'header_mapping', n.get_object_value(Source_replyTarget_headerMapping)),
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
        writer.write_bool_value("enabled", self.enabled)
        writer.write_collection_of_enum_values("expectedResponseTypes", self.expected_response_types)
        writer.write_object_value("headerMapping", self.header_mapping)
    

