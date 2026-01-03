from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class CountPostRequestBody(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # #### Filter predicates:* ```eq({property},{value})```  (i.e. equal to the given value)* ```ne({property},{value})```  (i.e. not equal to the given value)* ```gt({property},{value})```  (i.e. greater than the given value)* ```ge({property},{value})```  (i.e. equal to the given value or greater than it)* ```lt({property},{value})```  (i.e. lower than the given value or equal to it)* ```le({property},{value})```  (i.e. lower than the given value)* ```in({property},{value},{value},...)```  (i.e. contains at least one of the values listed)* ```like({property},{value})```  (i.e. contains values similar to the expressions listed)* ```ilike({property},{value})```  (i.e. contains values similar and case insensitive to the expressions listed)* ```exists({property})```  (i.e. all things in which the given path exists)Note: When using filter operations, only things with the specified properties are returned.For example, the filter `ne(attributes/owner, "SID123")` will only return things that do havethe `owner` attribute.#### Logical operations:* ```and({query},{query},...)```* ```or({query},{query},...)```* ```not({query})```#### Examples:* ```eq(attributes/location,"kitchen")```* ```ge(thingId,"myThing1")```* ```gt(_created,"2020-08-05T12:17")```* ```exists(features/featureId)```* ```and(eq(attributes/location,"kitchen"),eq(attributes/color,"red"))```* ```or(eq(attributes/location,"kitchen"),eq(attributes/location,"living-room"))```* ```like(attributes/key1,"known-chars-at-start*")```* ```like(attributes/key1,"*known-chars-at-end")```* ```like(attributes/key1,"*known-chars-in-between*")```* ```like(attributes/key1,"just-som?-char?-unkn?wn")```The `like` filters with the wildcard `*` at the beginning can slow down your search request.
    filter: Optional[str] = None
    # A comma-separated list of namespaces. This list is used to limit the query to things in the given namespacesonly.#### Examples:* `?namespaces=com.example.namespace`* `?namespaces=com.example.namespace1,com.example.namespace2`
    namespaces: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> CountPostRequestBody:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: CountPostRequestBody
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return CountPostRequestBody()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "filter": lambda n : setattr(self, 'filter', n.get_str_value()),
            "namespaces": lambda n : setattr(self, 'namespaces', n.get_str_value()),
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
        writer.write_str_value("filter", self.filter)
        writer.write_str_value("namespaces", self.namespaces)
        writer.write_additional_data_value(self.additional_data)
    

