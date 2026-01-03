from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .......models.subject_announcement import SubjectAnnouncement

@dataclass
class ActivateTokenIntegrationPostRequestBody(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Settings for announcements to be made about the subject.
    announcement: Optional[SubjectAnnouncement] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ActivateTokenIntegrationPostRequestBody:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ActivateTokenIntegrationPostRequestBody
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ActivateTokenIntegrationPostRequestBody()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .......models.subject_announcement import SubjectAnnouncement

        from .......models.subject_announcement import SubjectAnnouncement

        fields: dict[str, Callable[[Any], None]] = {
            "announcement": lambda n : setattr(self, 'announcement', n.get_object_value(SubjectAnnouncement)),
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
        writer.write_object_value("announcement", self.announcement)
        writer.write_additional_data_value(self.additional_data)
    

