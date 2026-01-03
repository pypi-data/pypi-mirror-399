from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class ThingsPostRequestBody(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Similar to the `filter`, a `condition` may be passed to ensure strong consistency when querying things.This `condition` has the same syntax and semantics than the `filter` - it is however applied on the matched thingsselected by the `filter` - on their current state.So combining this together with `filter` can provide strong consistency when performing a search.
    condition: Optional[str] = None
    # Contains a comma-separated list of fields to be included in the returnedJSON. attributes can be selected in the same manner.#### Selectable fields* `thingId`* `policyId`* `definition`* `attributes`   Supports selecting arbitrary sub-fields by using a comma-separated list:    * several attribute paths can be passed as a comma-separated list of JSON pointers (RFC-6901)      For example:        * `?fields=attributes/model` would select only `model` attribute value (if present)        * `?fields=attributes/model,attributes/location` would select only `model` and           `location` attribute values (if present)  Supports selecting arbitrary sub-fields of objects by wrapping sub-fields inside parentheses `( )`:    * a comma-separated list of sub-fields (a sub-field is a JSON pointer (RFC-6901)      separated with `/`) to select    * sub-selectors can be used to request only specific sub-fields by placing expressions      in parentheses `( )` after a selected subfield      For example:       * `?fields=attributes(model,location)` would select only `model`          and `location` attribute values (if present)       * `?fields=attributes(coffeemaker/serialno)` would select the `serialno` value          inside the `coffeemaker` object       * `?fields=attributes/address/postal(city,street)` would select the `city` and          `street` values inside the `postal` object inside the `address` object* `features`  Supports selecting arbitrary fields in features similar to `attributes` (see also features documentation for more details)* `_namespace`  Specifically selects the namespace also contained in the `thingId`* `_revision`  Specifically selects the revision of the thing. The revision is a counter, which is incremented on each modification of a thing.* `_created`  Specifically selects the created timestamp of the thing in ISO-8601 UTC format. The timestamp is set on creation of a thing.* `_modified`  Specifically selects the modified timestamp of the thing in ISO-8601 UTC format. The timestamp is set on each modification of a thing.* `_metadata`  Specifically selects the Metadata of the thing. The content is a JSON object having the Thing's JSON structure with the difference that the JSON leaves of the Thing are JSON objects containing the metadata.* `_policy`  Specifically selects the content of the policy associated to the thing. (By default, only the policyId is returned.)#### Examples* `?fields=thingId,attributes,features`* `?fields=attributes(model,manufacturer),features`
    fields: Optional[str] = None
    # #### Filter predicates:* ```eq({property},{value})```  (i.e. equal to the given value)* ```ne({property},{value})```  (i.e. not equal to the given value)* ```gt({property},{value})```  (i.e. greater than the given value)* ```ge({property},{value})```  (i.e. equal to the given value or greater than it)* ```lt({property},{value})```  (i.e. lower than the given value or equal to it)* ```le({property},{value})```  (i.e. lower than the given value)* ```in({property},{value},{value},...)```  (i.e. contains at least one of the values listed)* ```like({property},{value})```  (i.e. contains values similar to the expressions listed)* ```ilike({property},{value})```  (i.e. contains values similar and case insensitive to the expressions listed)* ```exists({property})```  (i.e. all things in which the given path exists)Note: When using filter operations, only things with the specified properties are returned.For example, the filter `ne(attributes/owner, "SID123")` will only return things that do havethe `owner` attribute.#### Logical operations:* ```and({query},{query},...)```* ```or({query},{query},...)```* ```not({query})```#### Examples:* ```eq(attributes/location,"kitchen")```* ```ge(thingId,"myThing1")```* ```gt(_created,"2020-08-05T12:17")```* ```exists(features/featureId)```* ```and(eq(attributes/location,"kitchen"),eq(attributes/color,"red"))```* ```or(eq(attributes/location,"kitchen"),eq(attributes/location,"living-room"))```* ```like(attributes/key1,"known-chars-at-start*")```* ```like(attributes/key1,"*known-chars-at-end")```* ```like(attributes/key1,"*known-chars-in-between*")```* ```like(attributes/key1,"just-som?-char?-unkn?wn")```The `like` filters with the wildcard `*` at the beginning can slow down your search request.
    filter: Optional[str] = None
    # A comma-separated list of namespaces. This list is used to limit the query to things in the given namespacesonly.#### Examples:* `?namespaces=com.example.namespace`* `?namespaces=com.example.namespace1,com.example.namespace2`
    namespaces: Optional[str] = None
    # Possible values for the parameter:#### Sort operations* ```sort([+|-]{property})```* ```sort([+|-]{property},[+|-]{property},...)```#### Paging operations* ```size({page-size})```  Maximum allowed page size is `200`. Default page size is `25`.* ```cursor({cursor-id})```  Start the search from the cursor location. Specify the cursor ID withoutquotation marks. Cursor IDs are given in search responses and mark the position after the last entry ofthe previous search. The meaning of cursor IDs is unspecified and may change without notice.The paging option `limit({offset},{count})` is deprecated.It may result in slow queries or timeouts and will be removed eventually.#### Examples:* ```sort(+thingId)```* ```sort(-attributes/manufacturer)```* ```sort(+thingId,-attributes/manufacturer)```* ```size(10)``` return 10 results* ```cursor(LOREMIPSUM)```  return results after the position of the cursor `LOREMIPSUM`.#### Combine:If you need to specify multiple options, when using the swagger UI just write each option in a new line.When using the plain REST API programmatically,you will need to separate the options using a comma (,) character.```size(200),cursor(LOREMIPSUM)```The deprecated paging option `limit` may not be combined with the other paging options `size` and `cursor`.
    option: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ThingsPostRequestBody:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ThingsPostRequestBody
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ThingsPostRequestBody()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "condition": lambda n : setattr(self, 'condition', n.get_str_value()),
            "fields": lambda n : setattr(self, 'fields', n.get_str_value()),
            "filter": lambda n : setattr(self, 'filter', n.get_str_value()),
            "namespaces": lambda n : setattr(self, 'namespaces', n.get_str_value()),
            "option": lambda n : setattr(self, 'option', n.get_str_value()),
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
        writer.write_str_value("condition", self.condition)
        writer.write_str_value("fields", self.fields)
        writer.write_str_value("filter", self.filter)
        writer.write_str_value("namespaces", self.namespaces)
        writer.write_str_value("option", self.option)
        writer.write_additional_data_value(self.additional_data)
    

