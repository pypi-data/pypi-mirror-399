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
    from ....models.logging_update_fields import LoggingUpdateFields
    from ....models.module import Module
    from ....models.module_updated_log_level import ModuleUpdatedLogLevel

class WithModuleNameItemRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /devops/logging/{moduleName}
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new WithModuleNameItemRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/devops/logging/{moduleName}{?includeDisabledLoggers*}", path_parameters)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[WithModuleNameItemRequestBuilderGetQueryParameters]] = None) -> Optional[Module]:
        """
        Return the configured log
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[Module]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ....models.module import Module

        return await self.request_adapter.send_async(request_info, Module, None)
    
    async def put(self,body: LoggingUpdateFields, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> Optional[ModuleUpdatedLogLevel]:
        """
        Return outcome modify log level for a specific module
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[ModuleUpdatedLogLevel]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_put_request_information(
            body, request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ....models.module_updated_log_level import ModuleUpdatedLogLevel

        return await self.request_adapter.send_async(request_info, ModuleUpdatedLogLevel, None)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[WithModuleNameItemRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Return the configured log
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_put_request_information(self,body: LoggingUpdateFields, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Return outcome modify log level for a specific module
        param body: The request body
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
    
    def with_url(self,raw_url: str) -> WithModuleNameItemRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: WithModuleNameItemRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return WithModuleNameItemRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class WithModuleNameItemRequestBuilderGetQueryParameters():
        """
        Return the configured log
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "include_disabled_loggers":
                return "includeDisabledLoggers"
            return original_name
        
        # Include disabled loggers
        include_disabled_loggers: Optional[bool] = None

    
    @dataclass
    class WithModuleNameItemRequestBuilderGetRequestConfiguration(RequestConfiguration[WithModuleNameItemRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class WithModuleNameItemRequestBuilderPutRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

