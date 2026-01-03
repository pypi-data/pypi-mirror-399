from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .policy_import import PolicyImport

@dataclass
class PolicyImports(AdditionalDataHolder, Parsable):
    """
    Policy imports containing one policy import for each key. The key is the policy ID of the referenced policy.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Single policy import defining which policy entries of the referenced policy are imported.
    policy_import_n: Optional[PolicyImport] = None
    # Single policy import defining which policy entries of the referenced policy are imported.
    policy_import1: Optional[PolicyImport] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> PolicyImports:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: PolicyImports
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return PolicyImports()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .policy_import import PolicyImport

        from .policy_import import PolicyImport

        fields: dict[str, Callable[[Any], None]] = {
            "policyImportN": lambda n : setattr(self, 'policy_import_n', n.get_object_value(PolicyImport)),
            "policyImport1": lambda n : setattr(self, 'policy_import1', n.get_object_value(PolicyImport)),
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
        writer.write_object_value("policyImportN", self.policy_import_n)
        writer.write_object_value("policyImport1", self.policy_import1)
        writer.write_additional_data_value(self.additional_data)
    

