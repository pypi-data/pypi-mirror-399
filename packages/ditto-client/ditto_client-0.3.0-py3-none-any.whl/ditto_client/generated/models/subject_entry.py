from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .subject_announcement import SubjectAnnouncement

@dataclass
class SubjectEntry(AdditionalDataHolder, Parsable):
    """
    Single (Authorization) Subject entry holding its type.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Settings for announcements to be made about the subject.
    announcement: Optional[SubjectAnnouncement] = None
    # The optional expiry timestamp (formatted in ISO-8601) indicates how long this subject should be considered active before it is automatically deleted from the Policy.
    expiry: Optional[datetime.datetime] = None
    # The type is offered only for documentation purposes. You are not restricted to any specific types, but we recommend to use it to specify the kind of the subject as shown in our examples.
    type: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> SubjectEntry:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: SubjectEntry
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return SubjectEntry()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .subject_announcement import SubjectAnnouncement

        from .subject_announcement import SubjectAnnouncement

        fields: dict[str, Callable[[Any], None]] = {
            "announcement": lambda n : setattr(self, 'announcement', n.get_object_value(SubjectAnnouncement)),
            "expiry": lambda n : setattr(self, 'expiry', n.get_datetime_value()),
            "type": lambda n : setattr(self, 'type', n.get_str_value()),
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
        writer.write_datetime_value("expiry", self.expiry)
        writer.write_str_value("type", self.type)
        writer.write_additional_data_value(self.additional_data)
    

