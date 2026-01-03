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
    from .....models.connection import Connection
    from .....models.new_connection import NewConnection
    from .command.command_request_builder import CommandRequestBuilder
    from .logs.logs_request_builder import LogsRequestBuilder
    from .metrics.metrics_request_builder import MetricsRequestBuilder
    from .status.status_request_builder import StatusRequestBuilder

class WithConnectionItemRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/2/connections/{connectionId}
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new WithConnectionItemRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/2/connections/{connectionId}{?fields*}", path_parameters)
    
    async def delete(self,request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> None:
        """
        Delete the connection identified by the `connectionId` path parameter.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: None
        """
        request_info = self.to_delete_request_information(
            request_configuration
        )
        from .....models.advanced_error import AdvancedError

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
            "403": AdvancedError,
            "404": AdvancedError,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_no_response_content_async(request_info, error_mapping)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[WithConnectionItemRequestBuilderGetQueryParameters]] = None) -> Optional[Connection]:
        """
        Returns the connection identified by the `connectionId` path parameter.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[Connection]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from .....models.advanced_error import AdvancedError

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
            "403": AdvancedError,
            "404": AdvancedError,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from .....models.connection import Connection

        return await self.request_adapter.send_async(request_info, Connection, error_mapping)
    
    async def put(self,body: NewConnection, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> None:
        """
        Update the connection identified by the `connectionId` path parameter.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: None
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_put_request_information(
            body, request_configuration
        )
        from .....models.advanced_error import AdvancedError

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
            "403": AdvancedError,
            "404": AdvancedError,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_no_response_content_async(request_info, error_mapping)
    
    def to_delete_request_information(self,request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Delete the connection identified by the `connectionId` path parameter.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.DELETE, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[WithConnectionItemRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Returns the connection identified by the `connectionId` path parameter.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_put_request_information(self,body: NewConnection, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Update the connection identified by the `connectionId` path parameter.
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
    
    def with_url(self,raw_url: str) -> WithConnectionItemRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: WithConnectionItemRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return WithConnectionItemRequestBuilder(self.request_adapter, raw_url)
    
    @property
    def command(self) -> CommandRequestBuilder:
        """
        The command property
        """
        from .command.command_request_builder import CommandRequestBuilder

        return CommandRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def logs(self) -> LogsRequestBuilder:
        """
        The logs property
        """
        from .logs.logs_request_builder import LogsRequestBuilder

        return LogsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def metrics(self) -> MetricsRequestBuilder:
        """
        The metrics property
        """
        from .metrics.metrics_request_builder import MetricsRequestBuilder

        return MetricsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def status(self) -> StatusRequestBuilder:
        """
        The status property
        """
        from .status.status_request_builder import StatusRequestBuilder

        return StatusRequestBuilder(self.request_adapter, self.path_parameters)
    
    @dataclass
    class WithConnectionItemRequestBuilderDeleteRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class WithConnectionItemRequestBuilderGetQueryParameters():
        """
        Returns the connection identified by the `connectionId` path parameter.
        """
        # Contains a comma-separated list of fields to be included in the returnedJSON.#### Selectable fields* `id`* `name`* `_revision`  Specifically selects the revision of the connection. The revision is a counter, which is incremented on each modification of a connection.* `_created`  Specifically selects the created timestamp of the connection in ISO-8601 UTC format. The timestamp is set on creation of a connection.* `_modified`  Specifically selects the modified timestamp of the connection in ISO-8601 UTC format. The timestamp is set on each modification of a connection.* `connectionType`* `connectionStatus`* `credentials`* `uri`* `sources`* `targets`* `sshTunnel`* `clientCount`* `failoverEnabled`* `validateCertificates`* `processorPoolSize`* `specificConfig`* `mappingDefinitions`* `tags`* `ca`#### Examples* `?fields=id,_revision,sources`
        fields: Optional[str] = None

    
    @dataclass
    class WithConnectionItemRequestBuilderGetRequestConfiguration(RequestConfiguration[WithConnectionItemRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class WithConnectionItemRequestBuilderPutRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

