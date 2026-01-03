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
    from .......models.advanced_error import AdvancedError
    from .......models.feature import Feature
    from .......models.feature424_error import Feature424Error
    from .......models.with_feature424_error import WithFeature424Error
    from .definition.definition_request_builder import DefinitionRequestBuilder
    from .delete_channel_query_parameter_type import DeleteChannelQueryParameterType
    from .desired_properties.desired_properties_request_builder import DesiredPropertiesRequestBuilder
    from .get_channel_query_parameter_type import GetChannelQueryParameterType
    from .get_live_channel_timeout_strategy_query_parameter_type import GetLiveChannelTimeoutStrategyQueryParameterType
    from .inbox.inbox_request_builder import InboxRequestBuilder
    from .outbox.outbox_request_builder import OutboxRequestBuilder
    from .patch_channel_query_parameter_type import PatchChannelQueryParameterType
    from .properties.properties_request_builder import PropertiesRequestBuilder
    from .put_channel_query_parameter_type import PutChannelQueryParameterType

class WithFeatureItemRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/2/things/{thingId}/features/{featureId}
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new WithFeatureItemRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/2/things/{thingId}/features/{featureId}{?channel*,condition*,fields*,live%2Dchannel%2Dcondition*,live%2Dchannel%2Dtimeout%2Dstrategy*,requested%2Dacks*,response%2Drequired*,timeout*}", path_parameters)
    
    async def delete(self,request_configuration: Optional[RequestConfiguration[WithFeatureItemRequestBuilderDeleteQueryParameters]] = None) -> None:
        """
        Deletes a specific feature identified by the `featureId` path parameterof the thing identified by the `thingId` path parameter.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: None
        """
        request_info = self.to_delete_request_information(
            request_configuration
        )
        from .......models.advanced_error import AdvancedError
        from .......models.feature424_error import Feature424Error
        from .......models.with_feature424_error import WithFeature424Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
            "403": AdvancedError,
            "404": AdvancedError,
            "412": AdvancedError,
            "424": WithFeature424Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_no_response_content_async(request_info, error_mapping)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[WithFeatureItemRequestBuilderGetQueryParameters]] = None) -> Optional[Feature]:
        """
        Returns a specific feature identified by the `featureId` path parameter of the thingidentified by the `thingId` path parameter.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[Feature]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from .......models.advanced_error import AdvancedError
        from .......models.feature424_error import Feature424Error
        from .......models.with_feature424_error import WithFeature424Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
            "404": AdvancedError,
            "412": AdvancedError,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from .......models.feature import Feature

        return await self.request_adapter.send_async(request_info, Feature, error_mapping)
    
    async def patch(self,body: Feature, request_configuration: Optional[RequestConfiguration[WithFeatureItemRequestBuilderPatchQueryParameters]] = None) -> None:
        """
        Patch a specific feature identified by the `featureId` path parameter of a thing identified by the `thingId` path parameter.The existing feature will be merged with the JSON content set in the request body.Notice that the `null` value can be used to delete the whole feature or specific parts of it.For further documentation see [RFC 7396](https://tools.ietf.org/html/rfc7396).**Note**: In contrast to the "PUT things/{thingId}/features/{featureId}" request,a partial update is supported here and request body is merged with the existing feature.### ExampleSet the `featureId` to **coffee-brewer** and all properties in the body partto update the `brewed-coffees` property and delete the definition.```{  "definition": null,  "properties": {    "brewed-coffees": 42  }}```
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: None
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_patch_request_information(
            body, request_configuration
        )
        from .......models.advanced_error import AdvancedError
        from .......models.feature424_error import Feature424Error
        from .......models.with_feature424_error import WithFeature424Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
            "403": AdvancedError,
            "404": AdvancedError,
            "412": AdvancedError,
            "413": AdvancedError,
            "424": WithFeature424Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_no_response_content_async(request_info, error_mapping)
    
    async def put(self,body: Feature, request_configuration: Optional[RequestConfiguration[WithFeatureItemRequestBuilderPutQueryParameters]] = None) -> Optional[Feature]:
        """
        Create or modify a specific feature identified by the `featureId` pathparameter of the thing identified by the `thingId` path parameter.### Create featureIf the feature ID is new, the feature and all content from the JSON body will be created### Update featureIf the feature ID is used already in this thing, the feature will be overwritternwith the content from the JSON body.### Example:Set the `featureId` to **coffee-brewer** and all properties in the body part.```{  "definition": ["com.acme:coffeebrewer:0.1.0"],  "properties": {    "brewed-coffees": 42  }}```
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[Feature]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_put_request_information(
            body, request_configuration
        )
        from .......models.advanced_error import AdvancedError
        from .......models.feature424_error import Feature424Error
        from .......models.with_feature424_error import WithFeature424Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
            "403": AdvancedError,
            "404": AdvancedError,
            "412": AdvancedError,
            "413": AdvancedError,
            "424": Feature424Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from .......models.feature import Feature

        return await self.request_adapter.send_async(request_info, Feature, error_mapping)
    
    def to_delete_request_information(self,request_configuration: Optional[RequestConfiguration[WithFeatureItemRequestBuilderDeleteQueryParameters]] = None) -> RequestInformation:
        """
        Deletes a specific feature identified by the `featureId` path parameterof the thing identified by the `thingId` path parameter.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.DELETE, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[WithFeatureItemRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Returns a specific feature identified by the `featureId` path parameter of the thingidentified by the `thingId` path parameter.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_patch_request_information(self,body: Feature, request_configuration: Optional[RequestConfiguration[WithFeatureItemRequestBuilderPatchQueryParameters]] = None) -> RequestInformation:
        """
        Patch a specific feature identified by the `featureId` path parameter of a thing identified by the `thingId` path parameter.The existing feature will be merged with the JSON content set in the request body.Notice that the `null` value can be used to delete the whole feature or specific parts of it.For further documentation see [RFC 7396](https://tools.ietf.org/html/rfc7396).**Note**: In contrast to the "PUT things/{thingId}/features/{featureId}" request,a partial update is supported here and request body is merged with the existing feature.### ExampleSet the `featureId` to **coffee-brewer** and all properties in the body partto update the `brewed-coffees` property and delete the definition.```{  "definition": null,  "properties": {    "brewed-coffees": 42  }}```
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = RequestInformation(Method.PATCH, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        request_info.set_content_from_parsable(self.request_adapter, "application/merge-patch+json", body)
        return request_info
    
    def to_put_request_information(self,body: Feature, request_configuration: Optional[RequestConfiguration[WithFeatureItemRequestBuilderPutQueryParameters]] = None) -> RequestInformation:
        """
        Create or modify a specific feature identified by the `featureId` pathparameter of the thing identified by the `thingId` path parameter.### Create featureIf the feature ID is new, the feature and all content from the JSON body will be created### Update featureIf the feature ID is used already in this thing, the feature will be overwritternwith the content from the JSON body.### Example:Set the `featureId` to **coffee-brewer** and all properties in the body part.```{  "definition": ["com.acme:coffeebrewer:0.1.0"],  "properties": {    "brewed-coffees": 42  }}```
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
    
    def with_url(self,raw_url: str) -> WithFeatureItemRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: WithFeatureItemRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return WithFeatureItemRequestBuilder(self.request_adapter, raw_url)
    
    @property
    def definition(self) -> DefinitionRequestBuilder:
        """
        The definition property
        """
        from .definition.definition_request_builder import DefinitionRequestBuilder

        return DefinitionRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def desired_properties(self) -> DesiredPropertiesRequestBuilder:
        """
        The desiredProperties property
        """
        from .desired_properties.desired_properties_request_builder import DesiredPropertiesRequestBuilder

        return DesiredPropertiesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def inbox(self) -> InboxRequestBuilder:
        """
        The inbox property
        """
        from .inbox.inbox_request_builder import InboxRequestBuilder

        return InboxRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def outbox(self) -> OutboxRequestBuilder:
        """
        The outbox property
        """
        from .outbox.outbox_request_builder import OutboxRequestBuilder

        return OutboxRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def properties(self) -> PropertiesRequestBuilder:
        """
        The properties property
        """
        from .properties.properties_request_builder import PropertiesRequestBuilder

        return PropertiesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @dataclass
    class WithFeatureItemRequestBuilderDeleteQueryParameters():
        """
        Deletes a specific feature identified by the `featureId` path parameterof the thing identified by the `thingId` path parameter.
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
    class WithFeatureItemRequestBuilderDeleteRequestConfiguration(RequestConfiguration[WithFeatureItemRequestBuilderDeleteQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class WithFeatureItemRequestBuilderGetQueryParameters():
        """
        Returns a specific feature identified by the `featureId` path parameter of the thingidentified by the `thingId` path parameter.
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
            if original_name == "fields":
                return "fields"
            if original_name == "timeout":
                return "timeout"
            return original_name
        
        # Defines to which channel to route the command: `twin` (digital twin) or `live` (the device).* If setting the channel parameter is omitted, the `twin` channel is set by default and the command is routed to the persisted representation of a thing in Eclipse Ditto.* When using the `live` channel, the command/message is sent towards the device.
        channel: Optional[GetChannelQueryParameterType] = None

        # Defines that the request should only be processed if the given condition is met. The condition can be specified using RQL syntax.#### ExamplesE.g. if the temperature is not 23.9 update it to 23.9:* ```PUT /api/2/things/{thingId}/features/temperature/properties/value?condition=ne(features/temperature/properties/value,23.9)```   `body: 23.9`Further example conditions:* ```?condition=eq(features/temperature/properties/unit,"Celsius")```* ```?condition=ge(features/temperature/properties/lastModified,"2021-08-22T19:45:00Z")```* ```?condition=gt(_modified,"2021-08-05T12:17:00Z")```* ```?condition=exists(features/temperature/properties/value)```* ```?condition=and(gt(features/temperature/properties/value,18.5),lt(features/temperature/properties/value,25.2))```* ```?condition=or(gt(features/temperature/properties/value,18.5),not(exists(features/temperature/properties/value))```
        condition: Optional[str] = None

        # Contains a comma-separated list of fields from the selected feature to beincluded in the returned JSON.#### Selectable fields* `properties`  Supports selecting arbitrary sub-fields by using a comma-separated list:    * several properties paths can be passed as a comma-separated list of JSON pointers (RFC-6901)      For example:        * `?fields=properties/color` would select only `color` property value (if present)        * `?fields=properties/color,properties/brightness` would select only `color` and `brightness` property values (if present)  Supports selecting arbitrary sub-fields of objects by wrapping sub-fields inside parentheses `( )`:    * a comma-separated list of sub-fields (a sub-field is a JSON pointer (RFC-6901) separated with `/`) to select    * sub-selectors can be used to request only specific sub-fields by placing expressions in parentheses `( )` after a selected subfield      For example:       * `?fields=properties(color,brightness)` would select only `color` and `brightness` property values (if present)       * `?fields=properties(location/longitude)` would select the `longitude` value inside the `location` object#### Examples* `?fields=properties(color,brightness)`
        fields: Optional[str] = None

        # Defines that the request should fetch thing data via `live` channel if the given condition is met. The condition can be specified using RQL syntax.#### Examples  * ```?live-channel-condition=lt(_modified,"2021-12-24T12:23:42Z")```  * ```?live-channel-condition=ge(features/ConnectionStatus/properties/status/readyUntil,time:now)```
        live_channel_condition: Optional[str] = None

        # Defines a strategy how to handle timeouts of a live response to a request sent via `channel=live` or with a matching  live-channel-condition.
        live_channel_timeout_strategy: Optional[GetLiveChannelTimeoutStrategyQueryParameterType] = None

        # Defines how long the backend should wait for completion of the request, e.g. applied when waiting for requestedacknowledgements via the `requested-acks` param. Can be specified without unit (then seconds are assumed) ortogether with `s`, `ms` or `m` unit. Example: `42s`, `1m`.The default (if omitted) and maximum timeout is `60s`. A value of `0` applies fire and forget semantics forthe command resulting in setting `response-required=false`.
        timeout: Optional[str] = None

    
    @dataclass
    class WithFeatureItemRequestBuilderGetRequestConfiguration(RequestConfiguration[WithFeatureItemRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class WithFeatureItemRequestBuilderPatchQueryParameters():
        """
        Patch a specific feature identified by the `featureId` path parameter of a thing identified by the `thingId` path parameter.The existing feature will be merged with the JSON content set in the request body.Notice that the `null` value can be used to delete the whole feature or specific parts of it.For further documentation see [RFC 7396](https://tools.ietf.org/html/rfc7396).**Note**: In contrast to the "PUT things/{thingId}/features/{featureId}" request,a partial update is supported here and request body is merged with the existing feature.### ExampleSet the `featureId` to **coffee-brewer** and all properties in the body partto update the `brewed-coffees` property and delete the definition.```{  "definition": null,  "properties": {    "brewed-coffees": 42  }}```
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
    class WithFeatureItemRequestBuilderPatchRequestConfiguration(RequestConfiguration[WithFeatureItemRequestBuilderPatchQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class WithFeatureItemRequestBuilderPutQueryParameters():
        """
        Create or modify a specific feature identified by the `featureId` pathparameter of the thing identified by the `thingId` path parameter.### Create featureIf the feature ID is new, the feature and all content from the JSON body will be created### Update featureIf the feature ID is used already in this thing, the feature will be overwritternwith the content from the JSON body.### Example:Set the `featureId` to **coffee-brewer** and all properties in the body part.```{  "definition": ["com.acme:coffeebrewer:0.1.0"],  "properties": {    "brewed-coffees": 42  }}```
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
    class WithFeatureItemRequestBuilderPutRequestConfiguration(RequestConfiguration[WithFeatureItemRequestBuilderPutQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

