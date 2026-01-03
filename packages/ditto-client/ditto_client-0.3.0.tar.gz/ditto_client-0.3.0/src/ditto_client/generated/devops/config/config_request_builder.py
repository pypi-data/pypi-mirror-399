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
    from ...models.retrieve_config import RetrieveConfig
    from .item.with_module_name_item_request_builder import WithModuleNameItemRequestBuilder

class ConfigRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /devops/config
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new ConfigRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/devops/config{?path*}", path_parameters)
    
    def by_module_name(self,module_name: str) -> WithModuleNameItemRequestBuilder:
        """
        Gets an item from the ApiSdk.devops.config.item collection
        param module_name: The name of module
        Returns: WithModuleNameItemRequestBuilder
        """
        if module_name is None:
            raise TypeError("module_name cannot be null.")
        from .item.with_module_name_item_request_builder import WithModuleNameItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["moduleName"] = module_name
        return WithModuleNameItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[ConfigRequestBuilderGetQueryParameters]] = None) -> Optional[RetrieveConfig]:
        """
        It is recommended to not omit the query parameter path.Otherwise, the full configurations of all services are aggregated in the response, which can become megabytes big.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[RetrieveConfig]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ...models.retrieve_config import RetrieveConfig

        return await self.request_adapter.send_async(request_info, RetrieveConfig, None)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[ConfigRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        It is recommended to not omit the query parameter path.Otherwise, the full configurations of all services are aggregated in the response, which can become megabytes big.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> ConfigRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: ConfigRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return ConfigRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class ConfigRequestBuilderGetQueryParameters():
        """
        It is recommended to not omit the query parameter path.Otherwise, the full configurations of all services are aggregated in the response, which can become megabytes big.
        """
        # The path points to information on service name, service instance index, JVM arguments and environment variables.
        path: Optional[str] = None

    
    @dataclass
    class ConfigRequestBuilderGetRequestConfiguration(RequestConfiguration[ConfigRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

