from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration
from kiota_abstractions.default_query_parameters import QueryParameters
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.method import Method
from kiota_abstractions.request_adapter import RequestAdapter
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.request_option import RequestOption
from kiota_abstractions.serialization import Parsable, ParsableFactory
from typing import Any, Optional, TYPE_CHECKING, Union
from warnings import warn

if TYPE_CHECKING:
    from .....models.advanced_error import AdvancedError
    from .....models.search_result_things import SearchResultThings
    from .count.count_request_builder import CountRequestBuilder
    from .things_post_request_body import ThingsPostRequestBody

class ThingsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/2/search/things
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new ThingsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/2/search/things{?fields*,filter*,namespaces*,option*,timeout*}", path_parameters)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[ThingsRequestBuilderGetQueryParameters]] = None) -> Optional[SearchResultThings]:
        """
        This resource can be used to search for things.* The query parameter `filter` is not mandatory. If it is not set, the  result contains all things which the logged in user is allowed to read.* The search is case sensitive. In case you don't know how exactly the  spelling of value of the namespace, name, attribute, feature etc. is, use the *like*  notation instead of *eq* for filtering.* The resource supports sorting and paging. If paging is not explicitly  specified by means of the `size` option, a default count of `25`  documents is returned.* The internal search index is "eventually consistent".  Consistency with the latest  thing updates should recover within milliseconds.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[SearchResultThings]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from .....models.advanced_error import AdvancedError

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
            "403": AdvancedError,
            "504": AdvancedError,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from .....models.search_result_things import SearchResultThings

        return await self.request_adapter.send_async(request_info, SearchResultThings, error_mapping)
    
    async def post(self,body: ThingsPostRequestBody, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> Optional[SearchResultThings]:
        """
        This resource can be used to search for things.* The parameter `filter` is not mandatory. If it is not set, the  result contains all things which the logged in user is allowed to read.* The search is case sensitive. In case you don't know how exactly the  spelling of value of the namespace, name, attribute, feature etc. is, use the *like*  notation instead of *eq* for filtering.* The resource supports sorting and paging. If paging is not explicitly  specified by means of the `size` option, a default count of `25`  documents is returned.* The internal search index is "eventually consistent".  Consistency with the latest  thing updates should recover within milliseconds.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[SearchResultThings]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        from .....models.advanced_error import AdvancedError

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
            "403": AdvancedError,
            "504": AdvancedError,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from .....models.search_result_things import SearchResultThings

        return await self.request_adapter.send_async(request_info, SearchResultThings, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[ThingsRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        This resource can be used to search for things.* The query parameter `filter` is not mandatory. If it is not set, the  result contains all things which the logged in user is allowed to read.* The search is case sensitive. In case you don't know how exactly the  spelling of value of the namespace, name, attribute, feature etc. is, use the *like*  notation instead of *eq* for filtering.* The resource supports sorting and paging. If paging is not explicitly  specified by means of the `size` option, a default count of `25`  documents is returned.* The internal search index is "eventually consistent".  Consistency with the latest  thing updates should recover within milliseconds.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_post_request_information(self,body: ThingsPostRequestBody, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        This resource can be used to search for things.* The parameter `filter` is not mandatory. If it is not set, the  result contains all things which the logged in user is allowed to read.* The search is case sensitive. In case you don't know how exactly the  spelling of value of the namespace, name, attribute, feature etc. is, use the *like*  notation instead of *eq* for filtering.* The resource supports sorting and paging. If paging is not explicitly  specified by means of the `size` option, a default count of `25`  documents is returned.* The internal search index is "eventually consistent".  Consistency with the latest  thing updates should recover within milliseconds.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = RequestInformation(Method.POST, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        request_info.set_content_from_parsable(self.request_adapter, "application/x-www-form-urlencoded", body)
        return request_info
    
    def with_url(self,raw_url: str) -> ThingsRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: ThingsRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return ThingsRequestBuilder(self.request_adapter, raw_url)
    
    @property
    def count(self) -> CountRequestBuilder:
        """
        The count property
        """
        from .count.count_request_builder import CountRequestBuilder

        return CountRequestBuilder(self.request_adapter, self.path_parameters)
    
    @dataclass
    class ThingsRequestBuilderGetQueryParameters():
        """
        This resource can be used to search for things.* The query parameter `filter` is not mandatory. If it is not set, the  result contains all things which the logged in user is allowed to read.* The search is case sensitive. In case you don't know how exactly the  spelling of value of the namespace, name, attribute, feature etc. is, use the *like*  notation instead of *eq* for filtering.* The resource supports sorting and paging. If paging is not explicitly  specified by means of the `size` option, a default count of `25`  documents is returned.* The internal search index is "eventually consistent".  Consistency with the latest  thing updates should recover within milliseconds.
        """
        # Contains a comma-separated list of fields to be included in the returnedJSON. attributes can be selected in the same manner.#### Selectable fields* `thingId`* `policyId`* `definition`* `attributes`   Supports selecting arbitrary sub-fields by using a comma-separated list:    * several attribute paths can be passed as a comma-separated list of JSON pointers (RFC-6901)      For example:        * `?fields=attributes/model` would select only `model` attribute value (if present)        * `?fields=attributes/model,attributes/location` would select only `model` and           `location` attribute values (if present)  Supports selecting arbitrary sub-fields of objects by wrapping sub-fields inside parentheses `( )`:    * a comma-separated list of sub-fields (a sub-field is a JSON pointer (RFC-6901)      separated with `/`) to select    * sub-selectors can be used to request only specific sub-fields by placing expressions      in parentheses `( )` after a selected subfield      For example:       * `?fields=attributes(model,location)` would select only `model`          and `location` attribute values (if present)       * `?fields=attributes(coffeemaker/serialno)` would select the `serialno` value          inside the `coffeemaker` object       * `?fields=attributes/address/postal(city,street)` would select the `city` and          `street` values inside the `postal` object inside the `address` object* `features`  Supports selecting arbitrary fields in features similar to `attributes` (see also features documentation for more details)* `_namespace`  Specifically selects the namespace also contained in the `thingId`* `_revision`  Specifically selects the revision of the thing. The revision is a counter, which is incremented on each modification of a thing.* `_created`  Specifically selects the created timestamp of the thing in ISO-8601 UTC format. The timestamp is set on creation of a thing.* `_modified`  Specifically selects the modified timestamp of the thing in ISO-8601 UTC format. The timestamp is set on each modification of a thing.* `_metadata`  Specifically selects the Metadata of the thing. The content is a JSON object having the Thing's JSON structure with the difference that the JSON leaves of the Thing are JSON objects containing the metadata.* `_policy`  Specifically selects the content of the policy associated to the thing. (By default, only the policyId is returned.)#### Examples* `?fields=thingId,attributes,features`* `?fields=attributes(model,manufacturer),features`
        fields: Optional[str] = None

        # #### Filter predicates:* ```eq({property},{value})```  (i.e. equal to the given value)* ```ne({property},{value})```  (i.e. not equal to the given value)* ```gt({property},{value})```  (i.e. greater than the given value)* ```ge({property},{value})```  (i.e. equal to the given value or greater than it)* ```lt({property},{value})```  (i.e. lower than the given value or equal to it)* ```le({property},{value})```  (i.e. lower than the given value)* ```in({property},{value},{value},...)```  (i.e. contains at least one of the values listed)* ```like({property},{value})```  (i.e. contains values similar to the expressions listed)* ```ilike({property},{value})```  (i.e. contains values similar and case insensitive to the expressions listed)* ```exists({property})```  (i.e. all things in which the given path exists)Note: When using filter operations, only things with the specified properties are returned.For example, the filter `ne(attributes/owner, "SID123")` will only return things that do havethe `owner` attribute.#### Logical operations:* ```and({query},{query},...)```* ```or({query},{query},...)```* ```not({query})```#### Examples:* ```eq(attributes/location,"kitchen")```* ```ge(thingId,"myThing1")```* ```gt(_created,"2020-08-05T12:17")```* ```exists(features/featureId)```* ```and(eq(attributes/location,"kitchen"),eq(attributes/color,"red"))```* ```or(eq(attributes/location,"kitchen"),eq(attributes/location,"living-room"))```* ```like(attributes/key1,"known-chars-at-start*")```* ```like(attributes/key1,"*known-chars-at-end")```* ```like(attributes/key1,"*known-chars-in-between*")```* ```like(attributes/key1,"just-som?-char?-unkn?wn")```The `like` filters with the wildcard `*` at the beginning can slow down your search request.
        filter: Optional[str] = None

        # A comma-separated list of namespaces. This list is used to limit the query to things in the given namespacesonly.#### Examples:* `?namespaces=com.example.namespace`* `?namespaces=com.example.namespace1,com.example.namespace2`
        namespaces: Optional[str] = None

        # Possible values for the parameter:#### Sort operations* ```sort([+|-]{property})```* ```sort([+|-]{property},[+|-]{property},...)```#### Paging operations* ```size({page-size})```  Maximum allowed page size is `200`. Default page size is `25`.* ```cursor({cursor-id})```  Start the search from the cursor location. Specify the cursor ID withoutquotation marks. Cursor IDs are given in search responses and mark the position after the last entry ofthe previous search. The meaning of cursor IDs is unspecified and may change without notice.The paging option `limit({offset},{count})` is deprecated.It may result in slow queries or timeouts and will be removed eventually.#### Examples:* ```sort(+thingId)```* ```sort(-attributes/manufacturer)```* ```sort(+thingId,-attributes/manufacturer)```* ```size(10)``` return 10 results* ```cursor(LOREMIPSUM)```  return results after the position of the cursor `LOREMIPSUM`.#### Combine:If you need to specify multiple options, when using the swagger UI just write each option in a new line.When using the plain REST API programmatically,you will need to separate the options using a comma (,) character.```size(200),cursor(LOREMIPSUM)```The deprecated paging option `limit` may not be combined with the other paging options `size` and `cursor`.
        option: Optional[str] = None

        # Defines how long the backend should wait for completion of the request, e.g. applied when waiting for requestedacknowledgements via the `requested-acks` param. Can be specified without unit (then seconds are assumed) ortogether with `s`, `ms` or `m` unit. Example: `42s`, `1m`.The default (if omitted) and maximum timeout is `60s`. A value of `0` applies fire and forget semantics forthe command resulting in setting `response-required=false`.
        timeout: Optional[str] = None

    
    @dataclass
    class ThingsRequestBuilderGetRequestConfiguration(RequestConfiguration[ThingsRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class ThingsRequestBuilderPostRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

