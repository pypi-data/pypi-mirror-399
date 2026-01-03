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
    from ......models.features import Features
    from ......models.features424_error import Features424Error
    from .delete_channel_query_parameter_type import DeleteChannelQueryParameterType
    from .get_channel_query_parameter_type import GetChannelQueryParameterType
    from .get_live_channel_timeout_strategy_query_parameter_type import GetLiveChannelTimeoutStrategyQueryParameterType
    from .item.with_feature_item_request_builder import WithFeatureItemRequestBuilder
    from .patch_channel_query_parameter_type import PatchChannelQueryParameterType
    from .put_channel_query_parameter_type import PutChannelQueryParameterType

class FeaturesRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/2/things/{thingId}/features
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new FeaturesRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/2/things/{thingId}/features{?channel*,condition*,fields*,live%2Dchannel%2Dcondition*,live%2Dchannel%2Dtimeout%2Dstrategy*,requested%2Dacks*,response%2Drequired*,timeout*}", path_parameters)
    
    def by_feature_id(self,feature_id: str) -> WithFeatureItemRequestBuilder:
        """
        Gets an item from the ApiSdk.api.Two.things.item.features.item collection
        param feature_id: The ID of the feature - has to conform to RFC-3986 (URI)
        Returns: WithFeatureItemRequestBuilder
        """
        if feature_id is None:
            raise TypeError("feature_id cannot be null.")
        from .item.with_feature_item_request_builder import WithFeatureItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["featureId"] = feature_id
        return WithFeatureItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def delete(self,request_configuration: Optional[RequestConfiguration[FeaturesRequestBuilderDeleteQueryParameters]] = None) -> None:
        """
        Deletes all features of the thing identified by the `thingId` path parameter.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: None
        """
        request_info = self.to_delete_request_information(
            request_configuration
        )
        from ......models.advanced_error import AdvancedError
        from ......models.features424_error import Features424Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
            "403": AdvancedError,
            "404": AdvancedError,
            "412": AdvancedError,
            "424": Features424Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_no_response_content_async(request_info, error_mapping)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[FeaturesRequestBuilderGetQueryParameters]] = None) -> Optional[Features]:
        """
        Returns all features of the thing identified by the `thingId` path parameter.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[Features]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ......models.advanced_error import AdvancedError
        from ......models.features424_error import Features424Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
            "404": AdvancedError,
            "412": AdvancedError,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ......models.features import Features

        return await self.request_adapter.send_async(request_info, Features, error_mapping)
    
    async def patch(self,body: Features, request_configuration: Optional[RequestConfiguration[FeaturesRequestBuilderPatchQueryParameters]] = None) -> None:
        """
        Patch all features of a thing identified by the `thingId` path parameter.The existing features will be merged with the JSON content set in the request body.Notice that the `null` value has a special meaning and can be used to delete specific features from the thing.For further documentation see [RFC 7396](https://tools.ietf.org/html/rfc7396).**Note**: In contrast to the "PUT thing/{thingId}/features" request, a partial update is supported hereand request body is merged with the existing features.### ExampleThe following example will add/update the properties `brewed-coffees`, `tempToHold` and `failState`.The configuration property `smartMode` will be deleted from the thing.```{  "coffee-brewer": {    "properties": {      "brewed-coffees": 10    }  },  "water-tank": {    "properties": {      "configuration": {        "smartMode": null,        "tempToHold": 50,      },      "status": {        "failState": true      }    }  }}```
        param body: List of features where the key represents the `featureId` of each feature.The `featureId` key must be unique in the list.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: None
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_patch_request_information(
            body, request_configuration
        )
        from ......models.advanced_error import AdvancedError
        from ......models.features424_error import Features424Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
            "403": AdvancedError,
            "404": AdvancedError,
            "412": AdvancedError,
            "413": AdvancedError,
            "424": Features424Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_no_response_content_async(request_info, error_mapping)
    
    async def put(self,body: Features, request_configuration: Optional[RequestConfiguration[FeaturesRequestBuilderPutQueryParameters]] = None) -> Optional[Features]:
        """
        Create or modify all features of a thing identified by the `thingId` path parameter.### Create all features at onceIn case at the initial creation of your thing you have not specified any features, these can be created here.### Update all features at onceTo update all features at once prepare the JSON body accordingly.Note: In contrast to the "PUT thing" request, a partial update is not supported here,but the content will be **overwritten**.If you need to update single features or their paths, please use the sub-resources instead.### Example:```{     "coffee-brewer": {       "definition": ["com.acme:coffeebrewer:0.1.0"],       "properties": {         "brewed-coffees": 0       }     },     "water-tank": {       "properties": {         "configuration": {           "smartMode": true,           "brewingTemp": 87,           "tempToHold": 44,           "timeoutSeconds": 6000         },         "status": {           "waterAmount": 731,           "temperature": 44         }       }     }}```
        param body: List of features where the key represents the `featureId` of each feature.The `featureId` key must be unique in the list.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[Features]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_put_request_information(
            body, request_configuration
        )
        from ......models.advanced_error import AdvancedError
        from ......models.features424_error import Features424Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
            "403": AdvancedError,
            "404": AdvancedError,
            "412": AdvancedError,
            "413": AdvancedError,
            "424": Features424Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ......models.features import Features

        return await self.request_adapter.send_async(request_info, Features, error_mapping)
    
    def to_delete_request_information(self,request_configuration: Optional[RequestConfiguration[FeaturesRequestBuilderDeleteQueryParameters]] = None) -> RequestInformation:
        """
        Deletes all features of the thing identified by the `thingId` path parameter.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.DELETE, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[FeaturesRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Returns all features of the thing identified by the `thingId` path parameter.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_patch_request_information(self,body: Features, request_configuration: Optional[RequestConfiguration[FeaturesRequestBuilderPatchQueryParameters]] = None) -> RequestInformation:
        """
        Patch all features of a thing identified by the `thingId` path parameter.The existing features will be merged with the JSON content set in the request body.Notice that the `null` value has a special meaning and can be used to delete specific features from the thing.For further documentation see [RFC 7396](https://tools.ietf.org/html/rfc7396).**Note**: In contrast to the "PUT thing/{thingId}/features" request, a partial update is supported hereand request body is merged with the existing features.### ExampleThe following example will add/update the properties `brewed-coffees`, `tempToHold` and `failState`.The configuration property `smartMode` will be deleted from the thing.```{  "coffee-brewer": {    "properties": {      "brewed-coffees": 10    }  },  "water-tank": {    "properties": {      "configuration": {        "smartMode": null,        "tempToHold": 50,      },      "status": {        "failState": true      }    }  }}```
        param body: List of features where the key represents the `featureId` of each feature.The `featureId` key must be unique in the list.
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
    
    def to_put_request_information(self,body: Features, request_configuration: Optional[RequestConfiguration[FeaturesRequestBuilderPutQueryParameters]] = None) -> RequestInformation:
        """
        Create or modify all features of a thing identified by the `thingId` path parameter.### Create all features at onceIn case at the initial creation of your thing you have not specified any features, these can be created here.### Update all features at onceTo update all features at once prepare the JSON body accordingly.Note: In contrast to the "PUT thing" request, a partial update is not supported here,but the content will be **overwritten**.If you need to update single features or their paths, please use the sub-resources instead.### Example:```{     "coffee-brewer": {       "definition": ["com.acme:coffeebrewer:0.1.0"],       "properties": {         "brewed-coffees": 0       }     },     "water-tank": {       "properties": {         "configuration": {           "smartMode": true,           "brewingTemp": 87,           "tempToHold": 44,           "timeoutSeconds": 6000         },         "status": {           "waterAmount": 731,           "temperature": 44         }       }     }}```
        param body: List of features where the key represents the `featureId` of each feature.The `featureId` key must be unique in the list.
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
    
    def with_url(self,raw_url: str) -> FeaturesRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: FeaturesRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return FeaturesRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class FeaturesRequestBuilderDeleteQueryParameters():
        """
        Deletes all features of the thing identified by the `thingId` path parameter.
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
    class FeaturesRequestBuilderDeleteRequestConfiguration(RequestConfiguration[FeaturesRequestBuilderDeleteQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class FeaturesRequestBuilderGetQueryParameters():
        """
        Returns all features of the thing identified by the `thingId` path parameter.
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
            if original_name == "requested_acks":
                return "requested%2Dacks"
            if original_name == "response_required":
                return "response%2Drequired"
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

        # Contains a comma-separated list of fields from one or more features to beincluded in the returned JSON.#### Selectable fields* `{featureId}` The ID of the feature to select properties in  * `properties`    Supports selecting arbitrary sub-fields by using a comma-separated list:      * several properties paths can be passed as a comma-separated list of JSON pointers (RFC-6901)        For example:          * `?fields={featureId}/properties/color` would select only `color` property value (if present) of the feature identified with `{featureId}`          * `?fields={featureId}/properties/color,properties/brightness` would select only `color` and `brightness` property values (if present) of the feature identified with `{featureId}`    Supports selecting arbitrary sub-fields of objects by wrapping sub-fields inside parentheses `( )`:      * a comma-separated list of sub-fields (a sub-field is a JSON pointer (RFC-6901) separated with `/`) to select      * sub-selectors can be used to request only specific sub-fields by placing expressions in parentheses `( )` after a selected subfield        For example:         * `?fields={featureId}/properties(color,brightness)` would select only `color` and `brightness` property values (if present) of the feature identified with `{featureId}`         * `?fields={featureId}/properties(location/longitude)` would select the `longitude` value inside the `location` object of the feature identified with `{featureId}`#### Examples* `?fields=EnvironmentScanner/properties(temperature,humidity)`* `?fields=EnvironmentScanner/properties(temperature,humidity),Vehicle/properties/configuration`
        fields: Optional[str] = None

        # Defines that the request should fetch thing data via `live` channel if the given condition is met. The condition can be specified using RQL syntax.#### Examples  * ```?live-channel-condition=lt(_modified,"2021-12-24T12:23:42Z")```  * ```?live-channel-condition=ge(features/ConnectionStatus/properties/status/readyUntil,time:now)```
        live_channel_condition: Optional[str] = None

        # Defines a strategy how to handle timeouts of a live response to a request sent via `channel=live` or with a matching  live-channel-condition.
        live_channel_timeout_strategy: Optional[GetLiveChannelTimeoutStrategyQueryParameterType] = None

        # Contains the "requested acknowledgements" for this modifying request as comma separated list. The HTTP call willblock until all requested acknowledgements were aggregated or will time out based on the specified `timeout`parameter.The default (if omitted) requested acks is `requested-acks=twin-persisted` which will block theHTTP call until the change was persited to the twin.
        requested_acks: Optional[str] = None

        # Defines whether a response is required to the API call or not - if set to `false` the response will directlysent back with a status code of `202` (Accepted).The default (if ommited) response is `true`.
        response_required: Optional[bool] = None

        # Defines how long the backend should wait for completion of the request, e.g. applied when waiting for requestedacknowledgements via the `requested-acks` param. Can be specified without unit (then seconds are assumed) ortogether with `s`, `ms` or `m` unit. Example: `42s`, `1m`.The default (if omitted) and maximum timeout is `60s`. A value of `0` applies fire and forget semantics forthe command resulting in setting `response-required=false`.
        timeout: Optional[str] = None

    
    @dataclass
    class FeaturesRequestBuilderGetRequestConfiguration(RequestConfiguration[FeaturesRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class FeaturesRequestBuilderPatchQueryParameters():
        """
        Patch all features of a thing identified by the `thingId` path parameter.The existing features will be merged with the JSON content set in the request body.Notice that the `null` value has a special meaning and can be used to delete specific features from the thing.For further documentation see [RFC 7396](https://tools.ietf.org/html/rfc7396).**Note**: In contrast to the "PUT thing/{thingId}/features" request, a partial update is supported hereand request body is merged with the existing features.### ExampleThe following example will add/update the properties `brewed-coffees`, `tempToHold` and `failState`.The configuration property `smartMode` will be deleted from the thing.```{  "coffee-brewer": {    "properties": {      "brewed-coffees": 10    }  },  "water-tank": {    "properties": {      "configuration": {        "smartMode": null,        "tempToHold": 50,      },      "status": {        "failState": true      }    }  }}```
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
    class FeaturesRequestBuilderPatchRequestConfiguration(RequestConfiguration[FeaturesRequestBuilderPatchQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class FeaturesRequestBuilderPutQueryParameters():
        """
        Create or modify all features of a thing identified by the `thingId` path parameter.### Create all features at onceIn case at the initial creation of your thing you have not specified any features, these can be created here.### Update all features at onceTo update all features at once prepare the JSON body accordingly.Note: In contrast to the "PUT thing" request, a partial update is not supported here,but the content will be **overwritten**.If you need to update single features or their paths, please use the sub-resources instead.### Example:```{     "coffee-brewer": {       "definition": ["com.acme:coffeebrewer:0.1.0"],       "properties": {         "brewed-coffees": 0       }     },     "water-tank": {       "properties": {         "configuration": {           "smartMode": true,           "brewingTemp": 87,           "tempToHold": 44,           "timeoutSeconds": 6000         },         "status": {           "waterAmount": 731,           "temperature": 44         }       }     }}```
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
    class FeaturesRequestBuilderPutRequestConfiguration(RequestConfiguration[FeaturesRequestBuilderPutQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

