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
    from ...models.advanced_error import AdvancedError
    from ...models.base_piggyback_command_request_schema import BasePiggybackCommandRequestSchema
    from ...models.piggyback_managing_background_cleanup import PiggybackManagingBackgroundCleanup
    from .item.with_service_name_item_request_builder import WithServiceNameItemRequestBuilder

class PiggybackRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /devops/piggyback
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new PiggybackRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/devops/piggyback{?timeout*}", path_parameters)
    
    def by_service_name(self,service_name: str) -> WithServiceNameItemRequestBuilder:
        """
        Gets an item from the ApiSdk.devops.piggyback.item collection
        param service_name: Specified service target for the command execution
        Returns: WithServiceNameItemRequestBuilder
        """
        if service_name is None:
            raise TypeError("service_name cannot be null.")
        from .item.with_service_name_item_request_builder import WithServiceNameItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["serviceName"] = service_name
        return WithServiceNameItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def post(self,body: BasePiggybackCommandRequestSchema, request_configuration: Optional[RequestConfiguration[PiggybackRequestBuilderPostQueryParameters]] = None) -> Optional[PiggybackManagingBackgroundCleanup]:
        """
        Send a piggyback command to Pekko’s pub-sub-mediator
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[PiggybackManagingBackgroundCleanup]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        from ...models.advanced_error import AdvancedError

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ...models.piggyback_managing_background_cleanup import PiggybackManagingBackgroundCleanup

        return await self.request_adapter.send_async(request_info, PiggybackManagingBackgroundCleanup, error_mapping)
    
    def to_post_request_information(self,body: BasePiggybackCommandRequestSchema, request_configuration: Optional[RequestConfiguration[PiggybackRequestBuilderPostQueryParameters]] = None) -> RequestInformation:
        """
        Send a piggyback command to Pekko’s pub-sub-mediator
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = RequestInformation(Method.POST, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        request_info.set_content_from_parsable(self.request_adapter, "application/json", body)
        return request_info
    
    def with_url(self,raw_url: str) -> PiggybackRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: PiggybackRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return PiggybackRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class PiggybackRequestBuilderPostQueryParameters():
        """
        Send a piggyback command to Pekko’s pub-sub-mediator
        """
        # Defines how long the backend should wait for completion of the request, e.g. applied when waiting for requestedacknowledgements via the `requested-acks` param. Can be specified without unit (then seconds are assumed) ortogether with `s`, `ms` or `m` unit. Example: `42s`, `1m`.The default (if omitted) and maximum timeout is `60s`. A value of `0` applies fire and forget semantics forthe command resulting in setting `response-required=false`.
        timeout: Optional[str] = None

    
    @dataclass
    class PiggybackRequestBuilderPostRequestConfiguration(RequestConfiguration[PiggybackRequestBuilderPostQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

