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
    from ......models.policy_entries import PolicyEntries
    from .item.with_label_item_request_builder import WithLabelItemRequestBuilder

class EntriesRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/2/policies/{policyId}/entries
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new EntriesRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/2/policies/{policyId}/entries{?response%2Drequired*,timeout*}", path_parameters)
    
    def by_label(self,label: str) -> WithLabelItemRequestBuilder:
        """
        Gets an item from the ApiSdk.api.Two.policies.item.entries.item collection
        param label: The label of a policy entry
        Returns: WithLabelItemRequestBuilder
        """
        if label is None:
            raise TypeError("label cannot be null.")
        from .item.with_label_item_request_builder import WithLabelItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["label"] = label
        return WithLabelItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[EntriesRequestBuilderGetQueryParameters]] = None) -> Optional[PolicyEntries]:
        """
        Returns all policy entries of the policy identified by the `policyId`path parameter.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[PolicyEntries]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ......models.advanced_error import AdvancedError

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
            "404": AdvancedError,
            "412": AdvancedError,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ......models.policy_entries import PolicyEntries

        return await self.request_adapter.send_async(request_info, PolicyEntries, error_mapping)
    
    async def put(self,body: PolicyEntries, request_configuration: Optional[RequestConfiguration[EntriesRequestBuilderPutQueryParameters]] = None) -> None:
        """
        Modify the policy entries of the policy identified by the `policyId`path parameter.Note: Take care to not lock yourself out. Use the placeholder {{ request:subjectId }}in order to let the backend insert the authenticated subjectId of the HTTP request.
        param body: Policy entries containing one policy entry for each arbitrary `label` key
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: None
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_put_request_information(
            body, request_configuration
        )
        from ......models.advanced_error import AdvancedError

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
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[EntriesRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Returns all policy entries of the policy identified by the `policyId`path parameter.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_put_request_information(self,body: PolicyEntries, request_configuration: Optional[RequestConfiguration[EntriesRequestBuilderPutQueryParameters]] = None) -> RequestInformation:
        """
        Modify the policy entries of the policy identified by the `policyId`path parameter.Note: Take care to not lock yourself out. Use the placeholder {{ request:subjectId }}in order to let the backend insert the authenticated subjectId of the HTTP request.
        param body: Policy entries containing one policy entry for each arbitrary `label` key
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
    
    def with_url(self,raw_url: str) -> EntriesRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: EntriesRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return EntriesRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class EntriesRequestBuilderGetQueryParameters():
        """
        Returns all policy entries of the policy identified by the `policyId`path parameter.
        """
        # Defines how long the backend should wait for completion of the request, e.g. applied when waiting for requestedacknowledgements via the `requested-acks` param. Can be specified without unit (then seconds are assumed) ortogether with `s`, `ms` or `m` unit. Example: `42s`, `1m`.The default (if omitted) and maximum timeout is `60s`. A value of `0` applies fire and forget semantics forthe command resulting in setting `response-required=false`.
        timeout: Optional[str] = None

    
    @dataclass
    class EntriesRequestBuilderGetRequestConfiguration(RequestConfiguration[EntriesRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class EntriesRequestBuilderPutQueryParameters():
        """
        Modify the policy entries of the policy identified by the `policyId`path parameter.Note: Take care to not lock yourself out. Use the placeholder {{ request:subjectId }}in order to let the backend insert the authenticated subjectId of the HTTP request.
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
    class EntriesRequestBuilderPutRequestConfiguration(RequestConfiguration[EntriesRequestBuilderPutQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

