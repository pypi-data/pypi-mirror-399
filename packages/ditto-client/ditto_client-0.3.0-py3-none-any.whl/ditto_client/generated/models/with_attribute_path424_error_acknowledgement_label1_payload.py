from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .with_attribute_path424_error_acknowledgement_label1_payload_member1 import WithAttributePath424Error_acknowledgementLabel1_payloadMember1
    from .with_attribute_path424_error_acknowledgement_label1_payload_member2 import WithAttributePath424Error_acknowledgementLabel1_payloadMember2

@dataclass
class WithAttributePath424Error_acknowledgementLabel1_payload(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes bool, float, str, WithAttributePath424Error_acknowledgementLabel1_payloadMember1, WithAttributePath424Error_acknowledgementLabel1_payloadMember2
    """
    # Composed type representation for type bool
    boolean: Optional[bool] = None
    # Composed type representation for type float
    double: Optional[float] = None
    # Composed type representation for type str
    string: Optional[str] = None
    # Composed type representation for type WithAttributePath424Error_acknowledgementLabel1_payloadMember1
    with_attribute_path424_error_acknowledgement_label1_payload_member1: Optional[WithAttributePath424Error_acknowledgementLabel1_payloadMember1] = None
    # Composed type representation for type WithAttributePath424Error_acknowledgementLabel1_payloadMember2
    with_attribute_path424_error_acknowledgement_label1_payload_member2: Optional[WithAttributePath424Error_acknowledgementLabel1_payloadMember2] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> WithAttributePath424Error_acknowledgementLabel1_payload:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: WithAttributePath424Error_acknowledgementLabel1_payload
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        try:
            child_node = parse_node.get_child_node("")
            mapping_value = child_node.get_str_value() if child_node else None
        except AttributeError:
            mapping_value = None
        result = WithAttributePath424Error_acknowledgementLabel1_payload()
        if mapping_value and mapping_value.casefold() == "".casefold():
            from .with_attribute_path424_error_acknowledgement_label1_payload_member1 import WithAttributePath424Error_acknowledgementLabel1_payloadMember1

            result.with_attribute_path424_error_acknowledgement_label1_payload_member1 = WithAttributePath424Error_acknowledgementLabel1_payloadMember1()
        elif mapping_value and mapping_value.casefold() == "".casefold():
            from .with_attribute_path424_error_acknowledgement_label1_payload_member2 import WithAttributePath424Error_acknowledgementLabel1_payloadMember2

            result.with_attribute_path424_error_acknowledgement_label1_payload_member2 = WithAttributePath424Error_acknowledgementLabel1_payloadMember2()
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
        from .with_attribute_path424_error_acknowledgement_label1_payload_member1 import WithAttributePath424Error_acknowledgementLabel1_payloadMember1
        from .with_attribute_path424_error_acknowledgement_label1_payload_member2 import WithAttributePath424Error_acknowledgementLabel1_payloadMember2

        if self.with_attribute_path424_error_acknowledgement_label1_payload_member1:
            return self.with_attribute_path424_error_acknowledgement_label1_payload_member1.get_field_deserializers()
        if self.with_attribute_path424_error_acknowledgement_label1_payload_member2:
            return self.with_attribute_path424_error_acknowledgement_label1_payload_member2.get_field_deserializers()
        return {}
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        if self.with_attribute_path424_error_acknowledgement_label1_payload_member1:
            writer.write_object_value(None, self.with_attribute_path424_error_acknowledgement_label1_payload_member1)
        elif self.with_attribute_path424_error_acknowledgement_label1_payload_member2:
            writer.write_object_value(None, self.with_attribute_path424_error_acknowledgement_label1_payload_member2)
        elif self.boolean:
            writer.write_bool_value(None, self.boolean)
        elif self.double:
            writer.write_float_value(None, self.double)
        elif self.string:
            writer.write_str_value(None, self.string)
    

