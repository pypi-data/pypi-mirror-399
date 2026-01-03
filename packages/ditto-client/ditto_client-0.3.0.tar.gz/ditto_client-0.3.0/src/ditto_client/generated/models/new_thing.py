from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .attributes import Attributes
    from .features import Features
    from .policy import Policy

@dataclass
class NewThing(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # This field may contain* the policy ID of an existing policy.  The policy is copied and used for this newly created thing. The  caller needs to have READ and WRITE<sup>*</sup> access to the policy.* a placeholder reference to a thing in the format {{ ref:things/[thingId]/policyId }} where you need to  replace [thingId] with a valid thing ID.  The newly created thing will then obtain a copy of the policy of  the referenced thing. The caller needs to have READ access to the thing and READ and WRITE<sup>*</sup>  access to the policy of the thing.<sup>*</sup> The check for WRITE permission avoids locking yourself out of the newly created policy. You canbypass this check by setting the header `allowPolicyLockout` to `true`. Be aware that the authorizedsubject cannot modify the policy if you do not assign WRITE permission on the policy resource!If you want to specify a policy ID for the copied policy, use the policyId field.This field must not be used together with the field _policy. If you specify both _policy and _copyPolicyFromthis will lead to an error response.
    _copy_policy_from: Optional[str] = None
    # The initial policy to create for this thing. This will create a separate policy entity managed by resource `/policies/{thingId}`.Use the placeholder `{{ request:subjectId }}` in order to let the backend insert the authenticated subjectId of the HTTP request.
    _policy: Optional[Policy] = None
    # An arbitrary JSON object describing the attributes of a thing.
    attributes: Optional[Attributes] = None
    # A single fully qualified identifier of a definition in the form '<namespace>:<name>:<version>' or a valid HTTP(s) URL
    definition: Optional[str] = None
    # List of features where the key represents the `featureId` of each feature.The `featureId` key must be unique in the list.
    features: Optional[Features] = None
    # The policy ID used for controlling access to this thing. Managed byresource `/policies/{policyId}`.
    policy_id: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> NewThing:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: NewThing
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return NewThing()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .attributes import Attributes
        from .features import Features
        from .policy import Policy

        from .attributes import Attributes
        from .features import Features
        from .policy import Policy

        fields: dict[str, Callable[[Any], None]] = {
            "_copyPolicyFrom": lambda n : setattr(self, '_copy_policy_from', n.get_str_value()),
            "_policy": lambda n : setattr(self, '_policy', n.get_object_value(Policy)),
            "attributes": lambda n : setattr(self, 'attributes', n.get_object_value(Attributes)),
            "definition": lambda n : setattr(self, 'definition', n.get_str_value()),
            "features": lambda n : setattr(self, 'features', n.get_object_value(Features)),
            "policyId": lambda n : setattr(self, 'policy_id', n.get_str_value()),
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
        writer.write_str_value("_copyPolicyFrom", self._copy_policy_from)
        writer.write_object_value("_policy", self._policy)
        writer.write_object_value("attributes", self.attributes)
        writer.write_str_value("definition", self.definition)
        writer.write_object_value("features", self.features)
        writer.write_str_value("policyId", self.policy_id)
        writer.write_additional_data_value(self.additional_data)
    

