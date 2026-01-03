from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .module_updated_log_level import ModuleUpdatedLogLevel

@dataclass
class ResultUpdateRequest(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Module that has been updated
    connectivity: Optional[ModuleUpdatedLogLevel] = None
    # Module that has been updated
    gateway: Optional[ModuleUpdatedLogLevel] = None
    # Module that has been updated
    policies: Optional[ModuleUpdatedLogLevel] = None
    # Module that has been updated
    things: Optional[ModuleUpdatedLogLevel] = None
    # Module that has been updated
    things_search: Optional[ModuleUpdatedLogLevel] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ResultUpdateRequest:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ResultUpdateRequest
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ResultUpdateRequest()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .module_updated_log_level import ModuleUpdatedLogLevel

        from .module_updated_log_level import ModuleUpdatedLogLevel

        fields: dict[str, Callable[[Any], None]] = {
            "connectivity": lambda n : setattr(self, 'connectivity', n.get_object_value(ModuleUpdatedLogLevel)),
            "gateway": lambda n : setattr(self, 'gateway', n.get_object_value(ModuleUpdatedLogLevel)),
            "policies": lambda n : setattr(self, 'policies', n.get_object_value(ModuleUpdatedLogLevel)),
            "things": lambda n : setattr(self, 'things', n.get_object_value(ModuleUpdatedLogLevel)),
            "things-search": lambda n : setattr(self, 'things_search', n.get_object_value(ModuleUpdatedLogLevel)),
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
        writer.write_object_value("connectivity", self.connectivity)
        writer.write_object_value("gateway", self.gateway)
        writer.write_object_value("policies", self.policies)
        writer.write_object_value("things", self.things)
        writer.write_object_value("things-search", self.things_search)
        writer.write_additional_data_value(self.additional_data)
    

