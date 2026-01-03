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
    from ......models.advanced_error import AdvancedError
    from .count_post_request_body import CountPostRequestBody

class CountRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/2/search/things/count
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new CountRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/2/search/things/count{?filter*,namespaces*,timeout*}", path_parameters)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[CountRequestBuilderGetQueryParameters]] = None) -> Optional[int]:
        """
        This resource can be used to count things.The query parameter `filter` is not mandatory. If it is not set there isreturned the total amount of things which the logged in user is allowedto read.To search for nested properties, we use JSON Pointer notation(RFC-6901). See the following example how to search for the sub property`location` of the parent property `attributes` with a forward slash asseparator:```eq(attributes/location,"kitchen")```
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[int]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ......models.advanced_error import AdvancedError

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
            "403": AdvancedError,
            "504": AdvancedError,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_primitive_async(request_info, "int", error_mapping)
    
    async def post(self,body: CountPostRequestBody, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> Optional[int]:
        """
        This resource can be used to count things.The parameter `filter` is not mandatory. If it is not set there isreturned the total amount of things which the logged in user is allowedto read.To search for nested properties, we use JSON Pointer notation(RFC-6901). See the following example how to search for the sub property`location` of the parent property `attributes` with a forward slash asseparator:```eq(attributes/location,"kitchen")```
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[int]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        from ......models.advanced_error import AdvancedError

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
            "403": AdvancedError,
            "504": AdvancedError,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_primitive_async(request_info, "int", error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[CountRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        This resource can be used to count things.The query parameter `filter` is not mandatory. If it is not set there isreturned the total amount of things which the logged in user is allowedto read.To search for nested properties, we use JSON Pointer notation(RFC-6901). See the following example how to search for the sub property`location` of the parent property `attributes` with a forward slash asseparator:```eq(attributes/location,"kitchen")```
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_post_request_information(self,body: CountPostRequestBody, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        This resource can be used to count things.The parameter `filter` is not mandatory. If it is not set there isreturned the total amount of things which the logged in user is allowedto read.To search for nested properties, we use JSON Pointer notation(RFC-6901). See the following example how to search for the sub property`location` of the parent property `attributes` with a forward slash asseparator:```eq(attributes/location,"kitchen")```
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
    
    def with_url(self,raw_url: str) -> CountRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: CountRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return CountRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class CountRequestBuilderGetQueryParameters():
        """
        This resource can be used to count things.The query parameter `filter` is not mandatory. If it is not set there isreturned the total amount of things which the logged in user is allowedto read.To search for nested properties, we use JSON Pointer notation(RFC-6901). See the following example how to search for the sub property`location` of the parent property `attributes` with a forward slash asseparator:```eq(attributes/location,"kitchen")```
        """
        # #### Filter predicates:* ```eq({property},{value})```  (i.e. equal to the given value)* ```ne({property},{value})```  (i.e. not equal to the given value)* ```gt({property},{value})```  (i.e. greater than the given value)* ```ge({property},{value})```  (i.e. equal to the given value or greater than it)* ```lt({property},{value})```  (i.e. lower than the given value or equal to it)* ```le({property},{value})```  (i.e. lower than the given value)* ```in({property},{value},{value},...)```  (i.e. contains at least one of the values listed)* ```like({property},{value})```  (i.e. contains values similar to the expressions listed)* ```ilike({property},{value})```  (i.e. contains values similar and case insensitive to the expressions listed)* ```exists({property})```  (i.e. all things in which the given path exists)Note: When using filter operations, only things with the specified properties are returned.For example, the filter `ne(attributes/owner, "SID123")` will only return things that do havethe `owner` attribute.#### Logical operations:* ```and({query},{query},...)```* ```or({query},{query},...)```* ```not({query})```#### Examples:* ```eq(attributes/location,"kitchen")```* ```ge(thingId,"myThing1")```* ```gt(_created,"2020-08-05T12:17")```* ```exists(features/featureId)```* ```and(eq(attributes/location,"kitchen"),eq(attributes/color,"red"))```* ```or(eq(attributes/location,"kitchen"),eq(attributes/location,"living-room"))```* ```like(attributes/key1,"known-chars-at-start*")```* ```like(attributes/key1,"*known-chars-at-end")```* ```like(attributes/key1,"*known-chars-in-between*")```* ```like(attributes/key1,"just-som?-char?-unkn?wn")```The `like` filters with the wildcard `*` at the beginning can slow down your search request.
        filter: Optional[str] = None

        # A comma-separated list of namespaces. This list is used to limit the query to things in the given namespacesonly.#### Examples:* `?namespaces=com.example.namespace`* `?namespaces=com.example.namespace1,com.example.namespace2`
        namespaces: Optional[str] = None

        # Defines how long the backend should wait for completion of the request, e.g. applied when waiting for requestedacknowledgements via the `requested-acks` param. Can be specified without unit (then seconds are assumed) ortogether with `s`, `ms` or `m` unit. Example: `42s`, `1m`.The default (if omitted) and maximum timeout is `60s`. A value of `0` applies fire and forget semantics forthe command resulting in setting `response-required=false`.
        timeout: Optional[str] = None

    
    @dataclass
    class CountRequestBuilderGetRequestConfiguration(RequestConfiguration[CountRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class CountRequestBuilderPostRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

