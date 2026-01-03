from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class ResultConfigService_config_gateway_authentication_devops(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The password property
    password: Optional[str] = None
    # The secured property
    secured: Optional[bool] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ResultConfigService_config_gateway_authentication_devops:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ResultConfigService_config_gateway_authentication_devops
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ResultConfigService_config_gateway_authentication_devops()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "password": lambda n : setattr(self, 'password', n.get_str_value()),
            "secured": lambda n : setattr(self, 'secured', n.get_bool_value()),
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
        writer.write_str_value("password", self.password)
        writer.write_bool_value("secured", self.secured)
        writer.write_additional_data_value(self.additional_data)
    

