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
    from ....models.advanced_error import AdvancedError
    from ....models.connection import Connection
    from ....models.new_connection import NewConnection
    from .item.with_connection_item_request_builder import WithConnectionItemRequestBuilder

class ConnectionsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/2/connections
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new ConnectionsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/2/connections{?dry%2Drun*,fields*,ids%2Donly*}", path_parameters)
    
    def by_connection_id(self,connection_id: str) -> WithConnectionItemRequestBuilder:
        """
        Gets an item from the ApiSdk.api.Two.connections.item collection
        param connection_id: The ID of the connection
        Returns: WithConnectionItemRequestBuilder
        """
        if connection_id is None:
            raise TypeError("connection_id cannot be null.")
        from .item.with_connection_item_request_builder import WithConnectionItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["connectionId"] = connection_id
        return WithConnectionItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[ConnectionsRequestBuilderGetQueryParameters]] = None) -> Optional[list[Connection]]:
        """
        Returns all connections.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[list[Connection]]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ....models.advanced_error import AdvancedError

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
            "403": AdvancedError,
            "404": AdvancedError,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ....models.connection import Connection

        return await self.request_adapter.send_collection_async(request_info, Connection, error_mapping)
    
    async def post(self,body: NewConnection, request_configuration: Optional[RequestConfiguration[ConnectionsRequestBuilderPostQueryParameters]] = None) -> Optional[Connection]:
        """
        Creates the connection defined in the JSON body.The ID of the connection will be **generated** by the backend. Any `ID` specified in the request body is thereforeprohibited.Supported connection types are `amqp-091`, `amqp-10`, `mqtt`, `mqtt-5`, `kafka`, `hono` and `http-push`.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[Connection]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        from ....models.advanced_error import AdvancedError

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
            "403": AdvancedError,
            "404": AdvancedError,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ....models.connection import Connection

        return await self.request_adapter.send_async(request_info, Connection, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[ConnectionsRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Returns all connections.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_post_request_information(self,body: NewConnection, request_configuration: Optional[RequestConfiguration[ConnectionsRequestBuilderPostQueryParameters]] = None) -> RequestInformation:
        """
        Creates the connection defined in the JSON body.The ID of the connection will be **generated** by the backend. Any `ID` specified in the request body is thereforeprohibited.Supported connection types are `amqp-091`, `amqp-10`, `mqtt`, `mqtt-5`, `kafka`, `hono` and `http-push`.
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
    
    def with_url(self,raw_url: str) -> ConnectionsRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: ConnectionsRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return ConnectionsRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class ConnectionsRequestBuilderGetQueryParameters():
        """
        Returns all connections.
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "ids_only":
                return "ids%2Donly"
            if original_name == "fields":
                return "fields"
            return original_name
        
        # Contains a comma-separated list of fields to be included in the returnedJSON.#### Selectable fields* `id`* `name`* `_revision`  Specifically selects the revision of the connection. The revision is a counter, which is incremented on each modification of a connection.* `_created`  Specifically selects the created timestamp of the connection in ISO-8601 UTC format. The timestamp is set on creation of a connection.* `_modified`  Specifically selects the modified timestamp of the connection in ISO-8601 UTC format. The timestamp is set on each modification of a connection.* `connectionType`* `connectionStatus`* `credentials`* `uri`* `sources`* `targets`* `sshTunnel`* `clientCount`* `failoverEnabled`* `validateCertificates`* `processorPoolSize`* `specificConfig`* `mappingDefinitions`* `tags`* `ca`#### Examples* `?fields=id,_revision,sources`
        fields: Optional[str] = None

        # When set to true, the request will return the registered ids only and not the whole connections objects.
        ids_only: Optional[bool] = None

    
    @dataclass
    class ConnectionsRequestBuilderGetRequestConfiguration(RequestConfiguration[ConnectionsRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class ConnectionsRequestBuilderPostQueryParameters():
        """
        Creates the connection defined in the JSON body.The ID of the connection will be **generated** by the backend. Any `ID` specified in the request body is thereforeprohibited.Supported connection types are `amqp-091`, `amqp-10`, `mqtt`, `mqtt-5`, `kafka`, `hono` and `http-push`.
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "dry_run":
                return "dry%2Drun"
            return original_name
        
        # When set to true, the request will not try to create the connection, but only try to connect it.You can use this parameter to verify that the given connection is able to communicate with your externalsystem.
        dry_run: Optional[bool] = None

    
    @dataclass
    class ConnectionsRequestBuilderPostRequestConfiguration(RequestConfiguration[ConnectionsRequestBuilderPostQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

