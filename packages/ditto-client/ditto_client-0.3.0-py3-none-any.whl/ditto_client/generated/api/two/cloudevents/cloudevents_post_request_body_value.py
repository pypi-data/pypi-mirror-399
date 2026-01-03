from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .cloudevents_post_request_body_value_member1 import CloudeventsPostRequestBody_valueMember1
    from .cloudevents_post_request_body_value_member2 import CloudeventsPostRequestBody_valueMember2

@dataclass
class CloudeventsPostRequestBody_value(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes bool, CloudeventsPostRequestBody_valueMember1, CloudeventsPostRequestBody_valueMember2, float, str
    """
    # Composed type representation for type bool
    boolean: Optional[bool] = None
    # Composed type representation for type CloudeventsPostRequestBody_valueMember1
    cloudevents_post_request_body_value_member1: Optional[CloudeventsPostRequestBody_valueMember1] = None
    # Composed type representation for type CloudeventsPostRequestBody_valueMember2
    cloudevents_post_request_body_value_member2: Optional[CloudeventsPostRequestBody_valueMember2] = None
    # Composed type representation for type float
    double: Optional[float] = None
    # Composed type representation for type str
    string: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> CloudeventsPostRequestBody_value:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: CloudeventsPostRequestBody_value
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        try:
            child_node = parse_node.get_child_node("")
            mapping_value = child_node.get_str_value() if child_node else None
        except AttributeError:
            mapping_value = None
        result = CloudeventsPostRequestBody_value()
        if mapping_value and mapping_value.casefold() == "".casefold():
            from .cloudevents_post_request_body_value_member1 import CloudeventsPostRequestBody_valueMember1

            result.cloudevents_post_request_body_value_member1 = CloudeventsPostRequestBody_valueMember1()
        elif mapping_value and mapping_value.casefold() == "".casefold():
            from .cloudevents_post_request_body_value_member2 import CloudeventsPostRequestBody_valueMember2

            result.cloudevents_post_request_body_value_member2 = CloudeventsPostRequestBody_valueMember2()
        elif boolean_value := parse_node.get_bool_value():
            result.boolean = boolean_value
        elif double_value := parse_node.get_float_value():
            result.double = double_value
        elif string_value := parse_node.get_str_value():
            result.string = string_value
        return result
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .cloudevents_post_request_body_value_member1 import CloudeventsPostRequestBody_valueMember1
        from .cloudevents_post_request_body_value_member2 import CloudeventsPostRequestBody_valueMember2

        if self.cloudevents_post_request_body_value_member1:
            return self.cloudevents_post_request_body_value_member1.get_field_deserializers()
        if self.cloudevents_post_request_body_value_member2:
            return self.cloudevents_post_request_body_value_member2.get_field_deserializers()
        return {}
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        if self.cloudevents_post_request_body_value_member1:
            writer.write_object_value(None, self.cloudevents_post_request_body_value_member1)
        elif self.cloudevents_post_request_body_value_member2:
            writer.write_object_value(None, self.cloudevents_post_request_body_value_member2)
        elif self.boolean:
            writer.write_bool_value(None, self.boolean)
        elif self.double:
            writer.write_float_value(None, self.double)
        elif self.string:
            writer.write_str_value(None, self.string)
    

