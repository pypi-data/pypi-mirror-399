from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .subject_announcement_requested_acks import SubjectAnnouncement_requestedAcks

@dataclass
class SubjectAnnouncement(AdditionalDataHolder, Parsable):
    """
    Settings for announcements to be made about the subject.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Interval in which the announcement can be sent earlier than the configured `beforeExpiry`. The actual point in time when the announcement will be sent is `beforeExpire` plus a randomly chosen time within the `randomizationInterval`. E.g assuming `beforeExpiry` is set to 5m and `randomizationInterval` is set to 1m, the announcements will be sent between 5 and 6 minutes before the subject expires. If omitted, the default value will be applied. If set to minimum, no randomization will be applied.
    randomization_interval: Optional[str] = "5m"
    # The duration before expiry when an announcement should be made.Must be a positive integer followed by one of `h` (hour), `m` (minute) or `s` (second).
    before_expiry: Optional[str] = None
    # Settings to enable at-least-once delivery for policy announcements.
    requested_acks: Optional[SubjectAnnouncement_requestedAcks] = None
    # Whether an announcement should be made when this subject is deleted.
    when_deleted: Optional[bool] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> SubjectAnnouncement:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: SubjectAnnouncement
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return SubjectAnnouncement()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .subject_announcement_requested_acks import SubjectAnnouncement_requestedAcks

        from .subject_announcement_requested_acks import SubjectAnnouncement_requestedAcks

        fields: dict[str, Callable[[Any], None]] = {
            "beforeExpiry": lambda n : setattr(self, 'before_expiry', n.get_str_value()),
            "randomizationInterval": lambda n : setattr(self, 'randomization_interval', n.get_str_value()),
            "requestedAcks": lambda n : setattr(self, 'requested_acks', n.get_object_value(SubjectAnnouncement_requestedAcks)),
            "whenDeleted": lambda n : setattr(self, 'when_deleted', n.get_bool_value()),
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
        writer.write_str_value("beforeExpiry", self.before_expiry)
        writer.write_str_value("randomizationInterval", self.randomization_interval)
        writer.write_object_value("requestedAcks", self.requested_acks)
        writer.write_bool_value("whenDeleted", self.when_deleted)
        writer.write_additional_data_value(self.additional_data)
    

