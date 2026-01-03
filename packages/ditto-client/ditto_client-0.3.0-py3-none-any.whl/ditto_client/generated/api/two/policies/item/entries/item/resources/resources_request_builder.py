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
    from ........models.advanced_error import AdvancedError
    from ........models.resources import Resources
    from .item.with_resource_path_item_request_builder import WithResourcePathItemRequestBuilder

class ResourcesRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/2/policies/{policyId}/entries/{label}/resources
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new ResourcesRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/2/policies/{policyId}/entries/{label}/resources{?response%2Drequired*,timeout*}", path_parameters)
    
    def by_resource_path(self,resource_path: str) -> WithResourcePathItemRequestBuilder:
        """
        Gets an item from the ApiSdk.api.Two.policies.item.entries.item.resources.item collection
        param resource_path: The path of an (Authorization) Resource
        Returns: WithResourcePathItemRequestBuilder
        """
        if resource_path is None:
            raise TypeError("resource_path cannot be null.")
        from .item.with_resource_path_item_request_builder import WithResourcePathItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["resourcePath"] = resource_path
        return WithResourcePathItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[ResourcesRequestBuilderGetQueryParameters]] = None) -> Optional[Resources]:
        """
        Returns all resource entries of the policy identified bythe `policyId` path parameter,and by the `label` path parameter.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[Resources]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ........models.advanced_error import AdvancedError

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
            "404": AdvancedError,
            "412": AdvancedError,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ........models.resources import Resources

        return await self.request_adapter.send_async(request_info, Resources, error_mapping)
    
    async def put(self,body: Resources, request_configuration: Optional[RequestConfiguration[ResourcesRequestBuilderPutQueryParameters]] = None) -> None:
        """
        Create or modify all resources of the policyidentified by the `policyId` path parameter,and by the `label` path parameter.### Delete all resource entriesSet the empty body part, if you need to delete all resource entries: { }### Set max permissions on all ressources```{  "policy:/": {    "grant": [      "READ",      "WRITE"    ],    "revoke": []  },  "thing:/": {    "grant": [      "READ",      "WRITE"    ],    "revoke": []  },  "message:/": {    "grant": [      "READ",      "WRITE"    ],    "revoke": []  }}```### Allow to read all parts of a thing except the "confidential" feature```{  "thing:/": {    "grant": [      "READ"    ],    "revoke": []  },  "things:/features/confidential": {    "grant": [],    "revoke": [      "READ"    ]  }}```
        param body: (Authorization) Resources containing one ResourceEntry for each`type:path` key, `type` being one of the following `thing`, `policy`, `message`.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: None
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_put_request_information(
            body, request_configuration
        )
        from ........models.advanced_error import AdvancedError

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
            "403": AdvancedError,
            "404": AdvancedError,
            "412": AdvancedError,
            "413": AdvancedError,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_no_response_content_async(request_info, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[ResourcesRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Returns all resource entries of the policy identified bythe `policyId` path parameter,and by the `label` path parameter.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_put_request_information(self,body: Resources, request_configuration: Optional[RequestConfiguration[ResourcesRequestBuilderPutQueryParameters]] = None) -> RequestInformation:
        """
        Create or modify all resources of the policyidentified by the `policyId` path parameter,and by the `label` path parameter.### Delete all resource entriesSet the empty body part, if you need to delete all resource entries: { }### Set max permissions on all ressources```{  "policy:/": {    "grant": [      "READ",      "WRITE"    ],    "revoke": []  },  "thing:/": {    "grant": [      "READ",      "WRITE"    ],    "revoke": []  },  "message:/": {    "grant": [      "READ",      "WRITE"    ],    "revoke": []  }}```### Allow to read all parts of a thing except the "confidential" feature```{  "thing:/": {    "grant": [      "READ"    ],    "revoke": []  },  "things:/features/confidential": {    "grant": [],    "revoke": [      "READ"    ]  }}```
        param body: (Authorization) Resources containing one ResourceEntry for each`type:path` key, `type` being one of the following `thing`, `policy`, `message`.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = RequestInformation(Method.PUT, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        request_info.set_content_from_parsable(self.request_adapter, "application/json", body)
        return request_info
    
    def with_url(self,raw_url: str) -> ResourcesRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: ResourcesRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return ResourcesRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class ResourcesRequestBuilderGetQueryParameters():
        """
        Returns all resource entries of the policy identified bythe `policyId` path parameter,and by the `label` path parameter.
        """
        # Defines how long the backend should wait for completion of the request, e.g. applied when waiting for requestedacknowledgements via the `requested-acks` param. Can be specified without unit (then seconds are assumed) ortogether with `s`, `ms` or `m` unit. Example: `42s`, `1m`.The default (if omitted) and maximum timeout is `60s`. A value of `0` applies fire and forget semantics forthe command resulting in setting `response-required=false`.
        timeout: Optional[str] = None

    
    @dataclass
    class ResourcesRequestBuilderGetRequestConfiguration(RequestConfiguration[ResourcesRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class ResourcesRequestBuilderPutQueryParameters():
        """
        Create or modify all resources of the policyidentified by the `policyId` path parameter,and by the `label` path parameter.### Delete all resource entriesSet the empty body part, if you need to delete all resource entries: { }### Set max permissions on all ressources```{  "policy:/": {    "grant": [      "READ",      "WRITE"    ],    "revoke": []  },  "thing:/": {    "grant": [      "READ",      "WRITE"    ],    "revoke": []  },  "message:/": {    "grant": [      "READ",      "WRITE"    ],    "revoke": []  }}```### Allow to read all parts of a thing except the "confidential" feature```{  "thing:/": {    "grant": [      "READ"    ],    "revoke": []  },  "things:/features/confidential": {    "grant": [],    "revoke": [      "READ"    ]  }}```
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "response_required":
                return "response%2Drequired"
            if original_name == "timeout":
                return "timeout"
            return original_name
        
        # Defines whether a response is required to the API call or not - if set to `false` the response will directlysent back with a status code of `202` (Accepted).The default (if ommited) response is `true`.
        response_required: Optional[bool] = None

        # Defines how long the backend should wait for completion of the request, e.g. applied when waiting for requestedacknowledgements via the `requested-acks` param. Can be specified without unit (then seconds are assumed) ortogether with `s`, `ms` or `m` unit. Example: `42s`, `1m`.The default (if omitted) and maximum timeout is `60s`. A value of `0` applies fire and forget semantics forthe command resulting in setting `response-required=false`.
        timeout: Optional[str] = None

    
    @dataclass
    class ResourcesRequestBuilderPutRequestConfiguration(RequestConfiguration[ResourcesRequestBuilderPutQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

