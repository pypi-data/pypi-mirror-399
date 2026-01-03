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
    from ........models.definition424_error import Definition424Error
    from ........models.feature_definition424_error import FeatureDefinition424Error
    from .delete_channel_query_parameter_type import DeleteChannelQueryParameterType
    from .get_channel_query_parameter_type import GetChannelQueryParameterType
    from .get_live_channel_timeout_strategy_query_parameter_type import GetLiveChannelTimeoutStrategyQueryParameterType
    from .patch_channel_query_parameter_type import PatchChannelQueryParameterType
    from .put_channel_query_parameter_type import PutChannelQueryParameterType

class DefinitionRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/2/things/{thingId}/features/{featureId}/definition
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new DefinitionRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/2/things/{thingId}/features/{featureId}/definition{?channel*,condition*,live%2Dchannel%2Dcondition*,live%2Dchannel%2Dtimeout%2Dstrategy*,requested%2Dacks*,response%2Drequired*,timeout*}", path_parameters)
    
    async def delete(self,request_configuration: Optional[RequestConfiguration[DefinitionRequestBuilderDeleteQueryParameters]] = None) -> None:
        """
        Deletes the complete definition of the feature identified by the `thingId` and `featureId` path parameter.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: None
        """
        request_info = self.to_delete_request_information(
            request_configuration
        )
        from ........models.advanced_error import AdvancedError
        from ........models.definition424_error import Definition424Error
        from ........models.feature_definition424_error import FeatureDefinition424Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
            "403": AdvancedError,
            "404": AdvancedError,
            "412": AdvancedError,
            "424": Definition424Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_no_response_content_async(request_info, error_mapping)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[DefinitionRequestBuilderGetQueryParameters]] = None) -> Optional[list[str]]:
        """
        Returns the complete definition field of the feature identified by the `thingId` and `featureId` path parameter.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[list[str]]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ........models.advanced_error import AdvancedError
        from ........models.definition424_error import Definition424Error
        from ........models.feature_definition424_error import FeatureDefinition424Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
            "404": AdvancedError,
            "412": AdvancedError,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_collection_of_primitive_async(request_info, str, error_mapping)
    
    async def patch(self,body: list[str], request_configuration: Optional[RequestConfiguration[DefinitionRequestBuilderPatchQueryParameters]] = None) -> None:
        """
        Patch the definition of a feature identified by the `thingId` and `featureId` path parameter.The existing definition field will be overwritten with the JSON array set in the request body.Notice that the `null` value can be used to delete the definition of a feature.For further documentation see [RFC 7396](https://tools.ietf.org/html/rfc7396).
        param body: The definitions of a feature.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: None
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_patch_request_information(
            body, request_configuration
        )
        from ........models.advanced_error import AdvancedError
        from ........models.definition424_error import Definition424Error
        from ........models.feature_definition424_error import FeatureDefinition424Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
            "403": AdvancedError,
            "404": AdvancedError,
            "412": AdvancedError,
            "413": AdvancedError,
            "424": Definition424Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_no_response_content_async(request_info, error_mapping)
    
    async def put(self,body: list[str], request_configuration: Optional[RequestConfiguration[DefinitionRequestBuilderPutQueryParameters]] = None) -> Optional[list[str]]:
        """
        Create or update the complete definition of a feature identified by the `thingId` and `featureId` path parameter.The definition field will be overwritten with the JSON array set in the request body
        param body: The definitions of a feature.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[list[str]]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_put_request_information(
            body, request_configuration
        )
        from ........models.advanced_error import AdvancedError
        from ........models.definition424_error import Definition424Error
        from ........models.feature_definition424_error import FeatureDefinition424Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
            "403": AdvancedError,
            "404": AdvancedError,
            "412": AdvancedError,
            "413": AdvancedError,
            "424": FeatureDefinition424Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_collection_of_primitive_async(request_info, str, error_mapping)
    
    def to_delete_request_information(self,request_configuration: Optional[RequestConfiguration[DefinitionRequestBuilderDeleteQueryParameters]] = None) -> RequestInformation:
        """
        Deletes the complete definition of the feature identified by the `thingId` and `featureId` path parameter.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.DELETE, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[DefinitionRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Returns the complete definition field of the feature identified by the `thingId` and `featureId` path parameter.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_patch_request_information(self,body: list[str], request_configuration: Optional[RequestConfiguration[DefinitionRequestBuilderPatchQueryParameters]] = None) -> RequestInformation:
        """
        Patch the definition of a feature identified by the `thingId` and `featureId` path parameter.The existing definition field will be overwritten with the JSON array set in the request body.Notice that the `null` value can be used to delete the definition of a feature.For further documentation see [RFC 7396](https://tools.ietf.org/html/rfc7396).
        param body: The definitions of a feature.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = RequestInformation(Method.PATCH, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        request_info.set_content_from_scalar(self.request_adapter, "application/merge-patch+json", body)
        return request_info
    
    def to_put_request_information(self,body: list[str], request_configuration: Optional[RequestConfiguration[DefinitionRequestBuilderPutQueryParameters]] = None) -> RequestInformation:
        """
        Create or update the complete definition of a feature identified by the `thingId` and `featureId` path parameter.The definition field will be overwritten with the JSON array set in the request body
        param body: The definitions of a feature.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = RequestInformation(Method.PUT, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        request_info.set_content_from_scalar(self.request_adapter, "application/json", body)
        return request_info
    
    def with_url(self,raw_url: str) -> DefinitionRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: DefinitionRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return DefinitionRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class DefinitionRequestBuilderDeleteQueryParameters():
        """
        Deletes the complete definition of the feature identified by the `thingId` and `featureId` path parameter.
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "requested_acks":
                return "requested%2Dacks"
            if original_name == "response_required":
                return "response%2Drequired"
            if original_name == "channel":
                return "channel"
            if original_name == "condition":
                return "condition"
            if original_name == "timeout":
                return "timeout"
            return original_name
        
        # Defines to which channel to route the command: `twin` (digital twin) or `live` (the device).* If setting the channel parameter is omitted, the `twin` channel is set by default and the command is routed to the persisted representation of a thing in Eclipse Ditto.* When using the `live` channel, the command/message is sent towards the device.
        channel: Optional[DeleteChannelQueryParameterType] = None

        # Defines that the request should only be processed if the given condition is met. The condition can be specified using RQL syntax.#### ExamplesE.g. if the temperature is not 23.9 update it to 23.9:* ```PUT /api/2/things/{thingId}/features/temperature/properties/value?condition=ne(features/temperature/properties/value,23.9)```   `body: 23.9`Further example conditions:* ```?condition=eq(features/temperature/properties/unit,"Celsius")```* ```?condition=ge(features/temperature/properties/lastModified,"2021-08-22T19:45:00Z")```* ```?condition=gt(_modified,"2021-08-05T12:17:00Z")```* ```?condition=exists(features/temperature/properties/value)```* ```?condition=and(gt(features/temperature/properties/value,18.5),lt(features/temperature/properties/value,25.2))```* ```?condition=or(gt(features/temperature/properties/value,18.5),not(exists(features/temperature/properties/value))```
        condition: Optional[str] = None

        # Contains the "requested acknowledgements" for this modifying request as comma separated list. The HTTP call willblock until all requested acknowledgements were aggregated or will time out based on the specified `timeout`parameter.The default (if omitted) requested acks is `requested-acks=twin-persisted` which will block theHTTP call until the change was persited to the twin.
        requested_acks: Optional[str] = None

        # Defines whether a response is required to the API call or not - if set to `false` the response will directlysent back with a status code of `202` (Accepted).The default (if ommited) response is `true`.
        response_required: Optional[bool] = None

        # Defines how long the backend should wait for completion of the request, e.g. applied when waiting for requestedacknowledgements via the `requested-acks` param. Can be specified without unit (then seconds are assumed) ortogether with `s`, `ms` or `m` unit. Example: `42s`, `1m`.The default (if omitted) and maximum timeout is `60s`. A value of `0` applies fire and forget semantics forthe command resulting in setting `response-required=false`.
        timeout: Optional[str] = None

    
    @dataclass
    class DefinitionRequestBuilderDeleteRequestConfiguration(RequestConfiguration[DefinitionRequestBuilderDeleteQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class DefinitionRequestBuilderGetQueryParameters():
        """
        Returns the complete definition field of the feature identified by the `thingId` and `featureId` path parameter.
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "live_channel_condition":
                return "live%2Dchannel%2Dcondition"
            if original_name == "live_channel_timeout_strategy":
                return "live%2Dchannel%2Dtimeout%2Dstrategy"
            if original_name == "channel":
                return "channel"
            if original_name == "condition":
                return "condition"
            if original_name == "timeout":
                return "timeout"
            return original_name
        
        # Defines to which channel to route the command: `twin` (digital twin) or `live` (the device).* If setting the channel parameter is omitted, the `twin` channel is set by default and the command is routed to the persisted representation of a thing in Eclipse Ditto.* When using the `live` channel, the command/message is sent towards the device.
        channel: Optional[GetChannelQueryParameterType] = None

        # Defines that the request should only be processed if the given condition is met. The condition can be specified using RQL syntax.#### ExamplesE.g. if the temperature is not 23.9 update it to 23.9:* ```PUT /api/2/things/{thingId}/features/temperature/properties/value?condition=ne(features/temperature/properties/value,23.9)```   `body: 23.9`Further example conditions:* ```?condition=eq(features/temperature/properties/unit,"Celsius")```* ```?condition=ge(features/temperature/properties/lastModified,"2021-08-22T19:45:00Z")```* ```?condition=gt(_modified,"2021-08-05T12:17:00Z")```* ```?condition=exists(features/temperature/properties/value)```* ```?condition=and(gt(features/temperature/properties/value,18.5),lt(features/temperature/properties/value,25.2))```* ```?condition=or(gt(features/temperature/properties/value,18.5),not(exists(features/temperature/properties/value))```
        condition: Optional[str] = None

        # Defines that the request should fetch thing data via `live` channel if the given condition is met. The condition can be specified using RQL syntax.#### Examples  * ```?live-channel-condition=lt(_modified,"2021-12-24T12:23:42Z")```  * ```?live-channel-condition=ge(features/ConnectionStatus/properties/status/readyUntil,time:now)```
        live_channel_condition: Optional[str] = None

        # Defines a strategy how to handle timeouts of a live response to a request sent via `channel=live` or with a matching  live-channel-condition.
        live_channel_timeout_strategy: Optional[GetLiveChannelTimeoutStrategyQueryParameterType] = None

        # Defines how long the backend should wait for completion of the request, e.g. applied when waiting for requestedacknowledgements via the `requested-acks` param. Can be specified without unit (then seconds are assumed) ortogether with `s`, `ms` or `m` unit. Example: `42s`, `1m`.The default (if omitted) and maximum timeout is `60s`. A value of `0` applies fire and forget semantics forthe command resulting in setting `response-required=false`.
        timeout: Optional[str] = None

    
    @dataclass
    class DefinitionRequestBuilderGetRequestConfiguration(RequestConfiguration[DefinitionRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class DefinitionRequestBuilderPatchQueryParameters():
        """
        Patch the definition of a feature identified by the `thingId` and `featureId` path parameter.The existing definition field will be overwritten with the JSON array set in the request body.Notice that the `null` value can be used to delete the definition of a feature.For further documentation see [RFC 7396](https://tools.ietf.org/html/rfc7396).
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "requested_acks":
                return "requested%2Dacks"
            if original_name == "response_required":
                return "response%2Drequired"
            if original_name == "channel":
                return "channel"
            if original_name == "condition":
                return "condition"
            if original_name == "timeout":
                return "timeout"
            return original_name
        
        # Defines to which channel to route the command: `twin` (digital twin) or `live` (the device).* If setting the channel parameter is omitted, the `twin` channel is set by default and the command is routed to the persisted representation of a thing in Eclipse Ditto.* When using the `live` channel, the command/message is sent towards the device.
        channel: Optional[PatchChannelQueryParameterType] = None

        # Defines that the request should only be processed if the given condition is met. The condition can be specified using RQL syntax.#### ExamplesE.g. if the temperature is not 23.9 update it to 23.9:* ```PUT /api/2/things/{thingId}/features/temperature/properties/value?condition=ne(features/temperature/properties/value,23.9)```   `body: 23.9`Further example conditions:* ```?condition=eq(features/temperature/properties/unit,"Celsius")```* ```?condition=ge(features/temperature/properties/lastModified,"2021-08-22T19:45:00Z")```* ```?condition=gt(_modified,"2021-08-05T12:17:00Z")```* ```?condition=exists(features/temperature/properties/value)```* ```?condition=and(gt(features/temperature/properties/value,18.5),lt(features/temperature/properties/value,25.2))```* ```?condition=or(gt(features/temperature/properties/value,18.5),not(exists(features/temperature/properties/value))```
        condition: Optional[str] = None

        # Contains the "requested acknowledgements" for this modifying request as comma separated list. The HTTP call willblock until all requested acknowledgements were aggregated or will time out based on the specified `timeout`parameter.The default (if omitted) requested acks is `requested-acks=twin-persisted` which will block theHTTP call until the change was persited to the twin.
        requested_acks: Optional[str] = None

        # Defines whether a response is required to the API call or not - if set to `false` the response will directlysent back with a status code of `202` (Accepted).The default (if ommited) response is `true`.
        response_required: Optional[bool] = None

        # Defines how long the backend should wait for completion of the request, e.g. applied when waiting for requestedacknowledgements via the `requested-acks` param. Can be specified without unit (then seconds are assumed) ortogether with `s`, `ms` or `m` unit. Example: `42s`, `1m`.The default (if omitted) and maximum timeout is `60s`. A value of `0` applies fire and forget semantics forthe command resulting in setting `response-required=false`.
        timeout: Optional[str] = None

    
    @dataclass
    class DefinitionRequestBuilderPatchRequestConfiguration(RequestConfiguration[DefinitionRequestBuilderPatchQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class DefinitionRequestBuilderPutQueryParameters():
        """
        Create or update the complete definition of a feature identified by the `thingId` and `featureId` path parameter.The definition field will be overwritten with the JSON array set in the request body
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "requested_acks":
                return "requested%2Dacks"
            if original_name == "response_required":
                return "response%2Drequired"
            if original_name == "channel":
                return "channel"
            if original_name == "condition":
                return "condition"
            if original_name == "timeout":
                return "timeout"
            return original_name
        
        # Defines to which channel to route the command: `twin` (digital twin) or `live` (the device).* If setting the channel parameter is omitted, the `twin` channel is set by default and the command is routed to the persisted representation of a thing in Eclipse Ditto.* When using the `live` channel, the command/message is sent towards the device.
        channel: Optional[PutChannelQueryParameterType] = None

        # Defines that the request should only be processed if the given condition is met. The condition can be specified using RQL syntax.#### ExamplesE.g. if the temperature is not 23.9 update it to 23.9:* ```PUT /api/2/things/{thingId}/features/temperature/properties/value?condition=ne(features/temperature/properties/value,23.9)```   `body: 23.9`Further example conditions:* ```?condition=eq(features/temperature/properties/unit,"Celsius")```* ```?condition=ge(features/temperature/properties/lastModified,"2021-08-22T19:45:00Z")```* ```?condition=gt(_modified,"2021-08-05T12:17:00Z")```* ```?condition=exists(features/temperature/properties/value)```* ```?condition=and(gt(features/temperature/properties/value,18.5),lt(features/temperature/properties/value,25.2))```* ```?condition=or(gt(features/temperature/properties/value,18.5),not(exists(features/temperature/properties/value))```
        condition: Optional[str] = None

        # Contains the "requested acknowledgements" for this modifying request as comma separated list. The HTTP call willblock until all requested acknowledgements were aggregated or will time out based on the specified `timeout`parameter.The default (if omitted) requested acks is `requested-acks=twin-persisted` which will block theHTTP call until the change was persited to the twin.
        requested_acks: Optional[str] = None

        # Defines whether a response is required to the API call or not - if set to `false` the response will directlysent back with a status code of `202` (Accepted).The default (if ommited) response is `true`.
        response_required: Optional[bool] = None

        # Defines how long the backend should wait for completion of the request, e.g. applied when waiting for requestedacknowledgements via the `requested-acks` param. Can be specified without unit (then seconds are assumed) ortogether with `s`, `ms` or `m` unit. Example: `42s`, `1m`.The default (if omitted) and maximum timeout is `60s`. A value of `0` applies fire and forget semantics forthe command resulting in setting `response-required=false`.
        timeout: Optional[str] = None

    
    @dataclass
    class DefinitionRequestBuilderPutRequestConfiguration(RequestConfiguration[DefinitionRequestBuilderPutQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

