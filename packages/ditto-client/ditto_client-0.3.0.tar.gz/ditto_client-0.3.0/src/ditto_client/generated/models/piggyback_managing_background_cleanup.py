from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .piggyback_managing_background_cleanup_headers import PiggybackManagingBackgroundCleanup_headers
    from .piggyback_managing_background_cleanup_piggyback_command import PiggybackManagingBackgroundCleanup_piggybackCommand

@dataclass
class PiggybackManagingBackgroundCleanup(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The headers property
    headers: Optional[PiggybackManagingBackgroundCleanup_headers] = None
    # The piggybackCommand property
    piggyback_command: Optional[PiggybackManagingBackgroundCleanup_piggybackCommand] = None
    # The targetActorSelection property
    target_actor_selection: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> PiggybackManagingBackgroundCleanup:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: PiggybackManagingBackgroundCleanup
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return PiggybackManagingBackgroundCleanup()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .piggyback_managing_background_cleanup_headers import PiggybackManagingBackgroundCleanup_headers
        from .piggyback_managing_background_cleanup_piggyback_command import PiggybackManagingBackgroundCleanup_piggybackCommand

        from .piggyback_managing_background_cleanup_headers import PiggybackManagingBackgroundCleanup_headers
        from .piggyback_managing_background_cleanup_piggyback_command import PiggybackManagingBackgroundCleanup_piggybackCommand

        fields: dict[str, Callable[[Any], None]] = {
            "headers": lambda n : setattr(self, 'headers', n.get_object_value(PiggybackManagingBackgroundCleanup_headers)),
            "piggybackCommand": lambda n : setattr(self, 'piggyback_command', n.get_object_value(PiggybackManagingBackgroundCleanup_piggybackCommand)),
            "targetActorSelection": lambda n : setattr(self, 'target_actor_selection', n.get_str_value()),
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
        writer.write_object_value("piggybackCommand", self.piggyback_command)
        writer.write_str_value("targetActorSelection", self.target_actor_selection)
        writer.write_additional_data_value(self.additional_data)
    

