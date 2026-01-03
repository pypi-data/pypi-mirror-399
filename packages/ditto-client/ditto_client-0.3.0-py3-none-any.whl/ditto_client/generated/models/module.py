from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .module_pod import Module_pod

@dataclass
class Module(AdditionalDataHolder, Parsable):
    """
    Module
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Details of logging configuration
    pod: Optional[Module_pod] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> Module:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: Module
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return Module()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .module_pod import Module_pod

        from .module_pod import Module_pod

        fields: dict[str, Callable[[Any], None]] = {
            "pod": lambda n : setattr(self, 'pod', n.get_object_value(Module_pod)),
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
        writer.write_object_value("pod", self.pod)
        writer.write_additional_data_value(self.additional_data)
    

