from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .subject_entry import SubjectEntry

@dataclass
class Subjects(AdditionalDataHolder, Parsable):
    """
    A SubjectEntry defines who is addressed.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Single (Authorization) Subject entry holding its type.
    nginx_subject_id_n: Optional[SubjectEntry] = None
    # Single (Authorization) Subject entry holding its type.
    nginx_subject_id1: Optional[SubjectEntry] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> Subjects:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: Subjects
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return Subjects()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .subject_entry import SubjectEntry

        from .subject_entry import SubjectEntry

        fields: dict[str, Callable[[Any], None]] = {
            "nginx:subjectIdN": lambda n : setattr(self, 'nginx_subject_id_n', n.get_object_value(SubjectEntry)),
            "nginx:subjectId1": lambda n : setattr(self, 'nginx_subject_id1', n.get_object_value(SubjectEntry)),
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
        writer.write_object_value("nginx:subjectIdN", self.nginx_subject_id_n)
        writer.write_object_value("nginx:subjectId1", self.nginx_subject_id1)
        writer.write_additional_data_value(self.additional_data)
    

