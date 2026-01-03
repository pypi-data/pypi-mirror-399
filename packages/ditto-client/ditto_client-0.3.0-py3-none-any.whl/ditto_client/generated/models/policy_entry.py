from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .importable import Importable
    from .resources import Resources
    from .subjects import Subjects

@dataclass
class PolicyEntry(AdditionalDataHolder, Parsable):
    """
    Single policy entry containing Subjects and Resources.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    from .importable import Importable

    # Controls the import behavior of this policy entry i.e. whether this policy entry is implicitly,explicitly or never imported when referenced from another policy.* `implicit` (default): the policy entry is imported without being listed in the importing policy individually* `explicit`: the policy entry is only imported if it is listed in the importing policy* `never`: the policy entry is not imported, regardless of being listed in the importing policyIf the field is not specified, default value is `implicit`.
    importable: Optional[Importable] = Importable("implicit")
    # (Authorization) Resources containing one ResourceEntry for each`type:path` key, `type` being one of the following `thing`, `policy`, `message`.
    resources: Optional[Resources] = None
    # A SubjectEntry defines who is addressed.
    subjects: Optional[Subjects] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> PolicyEntry:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: PolicyEntry
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return PolicyEntry()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .importable import Importable
        from .resources import Resources
        from .subjects import Subjects

        from .importable import Importable
        from .resources import Resources
        from .subjects import Subjects

        fields: dict[str, Callable[[Any], None]] = {
            "importable": lambda n : setattr(self, 'importable', n.get_enum_value(Importable)),
            "resources": lambda n : setattr(self, 'resources', n.get_object_value(Resources)),
            "subjects": lambda n : setattr(self, 'subjects', n.get_object_value(Subjects)),
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
        writer.write_enum_value("importable", self.importable)
        writer.write_object_value("resources", self.resources)
        writer.write_object_value("subjects", self.subjects)
        writer.write_additional_data_value(self.additional_data)
    

