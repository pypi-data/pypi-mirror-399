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
    from .....models.new_thing import NewThing
    from .....models.patch_thing import PatchThing
    from .....models.thing import Thing
    from .....models.thing424_error import Thing424Error
    from .....models.with_thing424_error import WithThing424Error
    from .attributes.attributes_request_builder import AttributesRequestBuilder
    from .definition.definition_request_builder import DefinitionRequestBuilder
    from .delete_channel_query_parameter_type import DeleteChannelQueryParameterType
    from .features.features_request_builder import FeaturesRequestBuilder
    from .get_channel_query_parameter_type import GetChannelQueryParameterType
    from .get_live_channel_timeout_strategy_query_parameter_type import GetLiveChannelTimeoutStrategyQueryParameterType
    from .inbox.inbox_request_builder import InboxRequestBuilder
    from .migrate_definition.migrate_definition_request_builder import MigrateDefinitionRequestBuilder
    from .outbox.outbox_request_builder import OutboxRequestBuilder
    from .patch_channel_query_parameter_type import PatchChannelQueryParameterType
    from .policy_id.policy_id_request_builder import PolicyIdRequestBuilder
    from .put_channel_query_parameter_type import PutChannelQueryParameterType

class WithThingItemRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/2/things/{thingId}
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new WithThingItemRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/2/things/{thingId}{?channel*,condition*,fields*,live%2Dchannel%2Dcondition*,live%2Dchannel%2Dtimeout%2Dstrategy*,requested%2Dacks*,response%2Drequired*,timeout*}", path_parameters)
    
    async def delete(self,request_configuration: Optional[RequestConfiguration[WithThingItemRequestBuilderDeleteQueryParameters]] = None) -> None:
        """
        Deletes the thing identified by the `thingId` path parameter.This will not delete the policy, which is used for controlling access to this thing.You can delete the policy afterwards via DELETE `/policies/{policyId}` if you don't need it for other things.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: None
        """
        request_info = self.to_delete_request_information(
            request_configuration
        )
        from .....models.advanced_error import AdvancedError
        from .....models.thing424_error import Thing424Error
        from .....models.with_thing424_error import WithThing424Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
            "403": AdvancedError,
            "404": AdvancedError,
            "412": AdvancedError,
            "424": WithThing424Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_no_response_content_async(request_info, error_mapping)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[WithThingItemRequestBuilderGetQueryParameters]] = None) -> Optional[Thing]:
        """
        Returns the thing identified by the `thingId` path parameter. The response includes details about the thing,including the `policyId`, attributes, definition and features.Optionally, you can use the field selectors (see parameter `fields`) to only get specific fields,which you are interested in.### Example:Use the field selector `_policy` to retrieve the content of the policy.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[Thing]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from .....models.advanced_error import AdvancedError
        from .....models.thing424_error import Thing424Error
        from .....models.with_thing424_error import WithThing424Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
            "404": AdvancedError,
            "412": AdvancedError,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from .....models.thing import Thing

        return await self.request_adapter.send_async(request_info, Thing, error_mapping)
    
    async def patch(self,body: PatchThing, request_configuration: Optional[RequestConfiguration[WithThingItemRequestBuilderPatchQueryParameters]] = None) -> Optional[Thing]:
        """
        Create or patch an existing thing specified by the `thingId` path parameter.If the thing did not yet exist, it will be created.For an existing thing, patching a thing will merge the provided request body with the existing thing values.This makes it possible to change only some parts of a thing in single request without providing the full thingstructure in the request body.### Patch a thingWith this resource it is possible to add, update or delete parts of an existing thing or to create the thing if itdoes not yet exist.The request body provided in *JSON merge patch* (RFC-7396) format will be merged with the existing thing.Notice that the `null` value in the JSON body will delete the specified JSON key from the thing.For further documentation of JSON merge patch see [RFC 7396](https://tools.ietf.org/html/rfc7396).### ExampleA Thing already exists with the following content:```{  "definition": "com.acme:coffeebrewer:0.1.0",  "attributes": {    "manufacturer": "ACME demo corp.",    "location": "Berlin, main floor",    "serialno": "42",    "model": "Speaking coffee machine"  },  "features": {    "coffee-brewer": {      "definition": ["com.acme:coffeebrewer:0.1.0"],      "properties": {        "brewed-coffees": 0      }    },    "water-tank": {      "properties": {        "configuration": {          "smartMode": true,          "brewingTemp": 87,          "tempToHold": 44,          "timeoutSeconds": 6000        },        "status": {          "waterAmount": 731,          "temperature": 44        }      }    }  }}```To make changes that only affect parts of the existing thing, e.g. add some attribute and delete aspecific feature property, the content of the request body could look like this:```{  "attributes": {    "manufacturingYear": "2020"  },  "features": {    "water-tank": {      "properties": {        "configuration": {          "smartMode": null,          "tempToHold": 50,        }      }    }  }}```The request body will be merged with the existing thing and the result will be the following thing:```{  "definition": "com.acme:coffeebrewer:0.1.0",  "attributes": {    "manufacturer": "ACME demo corp.",    "manufacturingYear": "2020",    "location": "Berlin, main floor",    "serialno": "42",    "model": "Speaking coffee machine"  },  "features": {    "coffee-brewer": {      "definition": ["com.acme:coffeebrewer:0.1.0"],      "properties": {        "brewed-coffees": 0      }    },    "water-tank": {      "properties": {        "configuration": {          "brewingTemp": 87,          "tempToHold": 50,          "timeoutSeconds": 6000        },        "status": {          "waterAmount": 731,          "temperature": 44        }      }    }  }}```### Permissions for patching an existing ThingFor updating an existing thing, the authorized subject needs **WRITE** permission on those parts of the thingthat are affected by the merge update.For example, to successfully execute the above example the authorized subject needs to have unrestricted*WRITE* permissions on all affected paths of the JSON merge patch: `attributes/manufacturingYear`,`features/water-tank/properties/configuration/smartMode`,`features/water-tank/properties/configuration/tempToHold`. The *WRITE* permission must not be revoked on anylevel further down the hierarchy. Consequently it is also sufficient for the authorized subject to haveunrestricted *WRITE* permission at root level or unrestricted *WRITE* permission at `/attributes` and`/features` etc.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[Thing]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_patch_request_information(
            body, request_configuration
        )
        from .....models.advanced_error import AdvancedError
        from .....models.thing424_error import Thing424Error
        from .....models.with_thing424_error import WithThing424Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
            "403": AdvancedError,
            "404": AdvancedError,
            "412": AdvancedError,
            "413": AdvancedError,
            "424": Thing424Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from .....models.thing import Thing

        return await self.request_adapter.send_async(request_info, Thing, error_mapping)
    
    async def put(self,body: NewThing, request_configuration: Optional[RequestConfiguration[WithThingItemRequestBuilderPutQueryParameters]] = None) -> Optional[Thing]:
        """
        Create or update the thing specified by the `thingId` path parameter and the optional JSON body.* If you set a new `thingId` in the path, a thing will be created.* If you set an existing `thingId` in the path, the thing will be updated.### Create a new thingAt the initial creation of a thing, only a valid `thingId` is required.However, you can create a full-fledged thing all at once.### Example:To create a coffee maker thing, set the `thingId` in the path, e.g. to "com.acme.coffeemaker:BE-42"and the body part, like in the following snippet.``` {   "definition": "com.acme:coffeebrewer:0.1.0",   "attributes": {     "manufacturer": "ACME demo corp.",     "location": "Berlin, main floor",     "serialno": "42",     "model": "Speaking coffee machine"   },   "features": {     "coffee-brewer": {       "definition": [ "com.acme:coffeebrewer:0.1.0" ],       "properties": {         "brewed-coffees": 0       }     },     "water-tank": {       "properties": {         "configuration": {           "smartMode": true,           "brewingTemp": 87,           "tempToHold": 44,           "timeoutSeconds": 6000         },         "status": {           "waterAmount": 731,           "temperature": 44         }       }     }   }  } ```As the example does not set a policy in the request body, but the thing concept requires one,the service will create a default policy. The default policy, has the exactly same idas the thing, and grants ALL permissions to the authorized subject.In case you need to associate the new thing to an already existing policy you can additionallyset a policy e.g. "policyId": "com.acme.coffeemaker:policy-1" as the first element in the body part.Keep in mind, that you can also change the assignment to another policy anytime,with a request on the sub-resource "PUT /things/{thingId}/policyId"The field `_created` is filled automatically with the timestamp of the creation. The field is read-only and canbe retrieved later by explicitly selecting it or used in search filters.### Update an existing thingFor updating an existing thing, the authorized subject needs **WRITE** permission on the thing's root resource.The ID of a thing cannot be changed after creation. Any `thingId`specified in the request body is therefore ignored.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[Thing]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_put_request_information(
            body, request_configuration
        )
        from .....models.advanced_error import AdvancedError
        from .....models.thing424_error import Thing424Error
        from .....models.with_thing424_error import WithThing424Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
            "403": AdvancedError,
            "404": AdvancedError,
            "412": AdvancedError,
            "413": AdvancedError,
            "424": Thing424Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from .....models.thing import Thing

        return await self.request_adapter.send_async(request_info, Thing, error_mapping)
    
    def to_delete_request_information(self,request_configuration: Optional[RequestConfiguration[WithThingItemRequestBuilderDeleteQueryParameters]] = None) -> RequestInformation:
        """
        Deletes the thing identified by the `thingId` path parameter.This will not delete the policy, which is used for controlling access to this thing.You can delete the policy afterwards via DELETE `/policies/{policyId}` if you don't need it for other things.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.DELETE, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[WithThingItemRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Returns the thing identified by the `thingId` path parameter. The response includes details about the thing,including the `policyId`, attributes, definition and features.Optionally, you can use the field selectors (see parameter `fields`) to only get specific fields,which you are interested in.### Example:Use the field selector `_policy` to retrieve the content of the policy.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_patch_request_information(self,body: PatchThing, request_configuration: Optional[RequestConfiguration[WithThingItemRequestBuilderPatchQueryParameters]] = None) -> RequestInformation:
        """
        Create or patch an existing thing specified by the `thingId` path parameter.If the thing did not yet exist, it will be created.For an existing thing, patching a thing will merge the provided request body with the existing thing values.This makes it possible to change only some parts of a thing in single request without providing the full thingstructure in the request body.### Patch a thingWith this resource it is possible to add, update or delete parts of an existing thing or to create the thing if itdoes not yet exist.The request body provided in *JSON merge patch* (RFC-7396) format will be merged with the existing thing.Notice that the `null` value in the JSON body will delete the specified JSON key from the thing.For further documentation of JSON merge patch see [RFC 7396](https://tools.ietf.org/html/rfc7396).### ExampleA Thing already exists with the following content:```{  "definition": "com.acme:coffeebrewer:0.1.0",  "attributes": {    "manufacturer": "ACME demo corp.",    "location": "Berlin, main floor",    "serialno": "42",    "model": "Speaking coffee machine"  },  "features": {    "coffee-brewer": {      "definition": ["com.acme:coffeebrewer:0.1.0"],      "properties": {        "brewed-coffees": 0      }    },    "water-tank": {      "properties": {        "configuration": {          "smartMode": true,          "brewingTemp": 87,          "tempToHold": 44,          "timeoutSeconds": 6000        },        "status": {          "waterAmount": 731,          "temperature": 44        }      }    }  }}```To make changes that only affect parts of the existing thing, e.g. add some attribute and delete aspecific feature property, the content of the request body could look like this:```{  "attributes": {    "manufacturingYear": "2020"  },  "features": {    "water-tank": {      "properties": {        "configuration": {          "smartMode": null,          "tempToHold": 50,        }      }    }  }}```The request body will be merged with the existing thing and the result will be the following thing:```{  "definition": "com.acme:coffeebrewer:0.1.0",  "attributes": {    "manufacturer": "ACME demo corp.",    "manufacturingYear": "2020",    "location": "Berlin, main floor",    "serialno": "42",    "model": "Speaking coffee machine"  },  "features": {    "coffee-brewer": {      "definition": ["com.acme:coffeebrewer:0.1.0"],      "properties": {        "brewed-coffees": 0      }    },    "water-tank": {      "properties": {        "configuration": {          "brewingTemp": 87,          "tempToHold": 50,          "timeoutSeconds": 6000        },        "status": {          "waterAmount": 731,          "temperature": 44        }      }    }  }}```### Permissions for patching an existing ThingFor updating an existing thing, the authorized subject needs **WRITE** permission on those parts of the thingthat are affected by the merge update.For example, to successfully execute the above example the authorized subject needs to have unrestricted*WRITE* permissions on all affected paths of the JSON merge patch: `attributes/manufacturingYear`,`features/water-tank/properties/configuration/smartMode`,`features/water-tank/properties/configuration/tempToHold`. The *WRITE* permission must not be revoked on anylevel further down the hierarchy. Consequently it is also sufficient for the authorized subject to haveunrestricted *WRITE* permission at root level or unrestricted *WRITE* permission at `/attributes` and`/features` etc.
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
    
    def to_put_request_information(self,body: NewThing, request_configuration: Optional[RequestConfiguration[WithThingItemRequestBuilderPutQueryParameters]] = None) -> RequestInformation:
        """
        Create or update the thing specified by the `thingId` path parameter and the optional JSON body.* If you set a new `thingId` in the path, a thing will be created.* If you set an existing `thingId` in the path, the thing will be updated.### Create a new thingAt the initial creation of a thing, only a valid `thingId` is required.However, you can create a full-fledged thing all at once.### Example:To create a coffee maker thing, set the `thingId` in the path, e.g. to "com.acme.coffeemaker:BE-42"and the body part, like in the following snippet.``` {   "definition": "com.acme:coffeebrewer:0.1.0",   "attributes": {     "manufacturer": "ACME demo corp.",     "location": "Berlin, main floor",     "serialno": "42",     "model": "Speaking coffee machine"   },   "features": {     "coffee-brewer": {       "definition": [ "com.acme:coffeebrewer:0.1.0" ],       "properties": {         "brewed-coffees": 0       }     },     "water-tank": {       "properties": {         "configuration": {           "smartMode": true,           "brewingTemp": 87,           "tempToHold": 44,           "timeoutSeconds": 6000         },         "status": {           "waterAmount": 731,           "temperature": 44         }       }     }   }  } ```As the example does not set a policy in the request body, but the thing concept requires one,the service will create a default policy. The default policy, has the exactly same idas the thing, and grants ALL permissions to the authorized subject.In case you need to associate the new thing to an already existing policy you can additionallyset a policy e.g. "policyId": "com.acme.coffeemaker:policy-1" as the first element in the body part.Keep in mind, that you can also change the assignment to another policy anytime,with a request on the sub-resource "PUT /things/{thingId}/policyId"The field `_created` is filled automatically with the timestamp of the creation. The field is read-only and canbe retrieved later by explicitly selecting it or used in search filters.### Update an existing thingFor updating an existing thing, the authorized subject needs **WRITE** permission on the thing's root resource.The ID of a thing cannot be changed after creation. Any `thingId`specified in the request body is therefore ignored.
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
    
    def with_url(self,raw_url: str) -> WithThingItemRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: WithThingItemRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return WithThingItemRequestBuilder(self.request_adapter, raw_url)
    
    @property
    def attributes(self) -> AttributesRequestBuilder:
        """
        The attributes property
        """
        from .attributes.attributes_request_builder import AttributesRequestBuilder

        return AttributesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def definition(self) -> DefinitionRequestBuilder:
        """
        The definition property
        """
        from .definition.definition_request_builder import DefinitionRequestBuilder

        return DefinitionRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def features(self) -> FeaturesRequestBuilder:
        """
        The features property
        """
        from .features.features_request_builder import FeaturesRequestBuilder

        return FeaturesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def inbox(self) -> InboxRequestBuilder:
        """
        The inbox property
        """
        from .inbox.inbox_request_builder import InboxRequestBuilder

        return InboxRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def migrate_definition(self) -> MigrateDefinitionRequestBuilder:
        """
        The migrateDefinition property
        """
        from .migrate_definition.migrate_definition_request_builder import MigrateDefinitionRequestBuilder

        return MigrateDefinitionRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def outbox(self) -> OutboxRequestBuilder:
        """
        The outbox property
        """
        from .outbox.outbox_request_builder import OutboxRequestBuilder

        return OutboxRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def policy_id(self) -> PolicyIdRequestBuilder:
        """
        The policyId property
        """
        from .policy_id.policy_id_request_builder import PolicyIdRequestBuilder

        return PolicyIdRequestBuilder(self.request_adapter, self.path_parameters)
    
    @dataclass
    class WithThingItemRequestBuilderDeleteQueryParameters():
        """
        Deletes the thing identified by the `thingId` path parameter.This will not delete the policy, which is used for controlling access to this thing.You can delete the policy afterwards via DELETE `/policies/{policyId}` if you don't need it for other things.
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
    class WithThingItemRequestBuilderDeleteRequestConfiguration(RequestConfiguration[WithThingItemRequestBuilderDeleteQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class WithThingItemRequestBuilderGetQueryParameters():
        """
        Returns the thing identified by the `thingId` path parameter. The response includes details about the thing,including the `policyId`, attributes, definition and features.Optionally, you can use the field selectors (see parameter `fields`) to only get specific fields,which you are interested in.### Example:Use the field selector `_policy` to retrieve the content of the policy.
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
        
        # Defines to which channel to route the command: `twin` (digital twin) or `live` (the device).* If setting the channel parameter is omitted, the `twin` channel is set by default and the command is routed to the persisted representation of a thing in Eclipse Ditto.* When using the `live` channel, the command/message is sent towards the device.The option `live` is not available when a new thing should be created, only for updating anexisting thing.
        channel: Optional[GetChannelQueryParameterType] = None

        # Defines that the request should only be processed if the given condition is met. The condition can be specified using RQL syntax.#### ExamplesE.g. if the temperature is not 23.9 update it to 23.9:* ```PUT /api/2/things/{thingId}/features/temperature/properties/value?condition=ne(features/temperature/properties/value,23.9)```   `body: 23.9`Further example conditions:* ```?condition=eq(features/temperature/properties/unit,"Celsius")```* ```?condition=ge(features/temperature/properties/lastModified,"2021-08-22T19:45:00Z")```* ```?condition=gt(_modified,"2021-08-05T12:17:00Z")```* ```?condition=exists(features/temperature/properties/value)```* ```?condition=and(gt(features/temperature/properties/value,18.5),lt(features/temperature/properties/value,25.2))```* ```?condition=or(gt(features/temperature/properties/value,18.5),not(exists(features/temperature/properties/value))```
        condition: Optional[str] = None

        # Contains a comma-separated list of fields to be included in the returnedJSON. attributes can be selected in the same manner.#### Selectable fields* `thingId`* `policyId`* `definition`* `attributes`   Supports selecting arbitrary sub-fields by using a comma-separated list:    * several attribute paths can be passed as a comma-separated list of JSON pointers (RFC-6901)      For example:        * `?fields=attributes/model` would select only `model` attribute value (if present)        * `?fields=attributes/model,attributes/location` would select only `model` and           `location` attribute values (if present)  Supports selecting arbitrary sub-fields of objects by wrapping sub-fields inside parentheses `( )`:    * a comma-separated list of sub-fields (a sub-field is a JSON pointer (RFC-6901)      separated with `/`) to select    * sub-selectors can be used to request only specific sub-fields by placing expressions      in parentheses `( )` after a selected subfield      For example:       * `?fields=attributes(model,location)` would select only `model`          and `location` attribute values (if present)       * `?fields=attributes(coffeemaker/serialno)` would select the `serialno` value          inside the `coffeemaker` object       * `?fields=attributes/address/postal(city,street)` would select the `city` and          `street` values inside the `postal` object inside the `address` object* `features`  Supports selecting arbitrary fields in features similar to `attributes` (see also features documentation for more details)* `_namespace`  Specifically selects the namespace also contained in the `thingId`* `_revision`  Specifically selects the revision of the thing. The revision is a counter, which is incremented on each modification of a thing.* `_created`  Specifically selects the created timestamp of the thing in ISO-8601 UTC format. The timestamp is set on creation of a thing.* `_modified`  Specifically selects the modified timestamp of the thing in ISO-8601 UTC format. The timestamp is set on each modification of a thing.* `_metadata`  Specifically selects the Metadata of the thing. The content is a JSON object having the Thing's JSON structure with the difference that the JSON leaves of the Thing are JSON objects containing the metadata.* `_policy`  Specifically selects the content of the policy associated to the thing. (By default, only the policyId is returned.)#### Examples* `?fields=thingId,attributes,features`* `?fields=attributes(model,manufacturer),features`
        fields: Optional[str] = None

        # Defines that the request should fetch thing data via `live` channel if the given condition is met. The condition can be specified using RQL syntax.#### Examples  * ```?live-channel-condition=lt(_modified,"2021-12-24T12:23:42Z")```  * ```?live-channel-condition=ge(features/ConnectionStatus/properties/status/readyUntil,time:now)```
        live_channel_condition: Optional[str] = None

        # Defines a strategy how to handle timeouts of a live response to a request sent via `channel=live` or with a matching  live-channel-condition.
        live_channel_timeout_strategy: Optional[GetLiveChannelTimeoutStrategyQueryParameterType] = None

        # Defines how long the backend should wait for completion of the request, e.g. applied when waiting for requestedacknowledgements via the `requested-acks` param. Can be specified without unit (then seconds are assumed) ortogether with `s`, `ms` or `m` unit. Example: `42s`, `1m`.The default (if omitted) and maximum timeout is `60s`. A value of `0` applies fire and forget semantics forthe command resulting in setting `response-required=false`.
        timeout: Optional[str] = None

    
    @dataclass
    class WithThingItemRequestBuilderGetRequestConfiguration(RequestConfiguration[WithThingItemRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class WithThingItemRequestBuilderPatchQueryParameters():
        """
        Create or patch an existing thing specified by the `thingId` path parameter.If the thing did not yet exist, it will be created.For an existing thing, patching a thing will merge the provided request body with the existing thing values.This makes it possible to change only some parts of a thing in single request without providing the full thingstructure in the request body.### Patch a thingWith this resource it is possible to add, update or delete parts of an existing thing or to create the thing if itdoes not yet exist.The request body provided in *JSON merge patch* (RFC-7396) format will be merged with the existing thing.Notice that the `null` value in the JSON body will delete the specified JSON key from the thing.For further documentation of JSON merge patch see [RFC 7396](https://tools.ietf.org/html/rfc7396).### ExampleA Thing already exists with the following content:```{  "definition": "com.acme:coffeebrewer:0.1.0",  "attributes": {    "manufacturer": "ACME demo corp.",    "location": "Berlin, main floor",    "serialno": "42",    "model": "Speaking coffee machine"  },  "features": {    "coffee-brewer": {      "definition": ["com.acme:coffeebrewer:0.1.0"],      "properties": {        "brewed-coffees": 0      }    },    "water-tank": {      "properties": {        "configuration": {          "smartMode": true,          "brewingTemp": 87,          "tempToHold": 44,          "timeoutSeconds": 6000        },        "status": {          "waterAmount": 731,          "temperature": 44        }      }    }  }}```To make changes that only affect parts of the existing thing, e.g. add some attribute and delete aspecific feature property, the content of the request body could look like this:```{  "attributes": {    "manufacturingYear": "2020"  },  "features": {    "water-tank": {      "properties": {        "configuration": {          "smartMode": null,          "tempToHold": 50,        }      }    }  }}```The request body will be merged with the existing thing and the result will be the following thing:```{  "definition": "com.acme:coffeebrewer:0.1.0",  "attributes": {    "manufacturer": "ACME demo corp.",    "manufacturingYear": "2020",    "location": "Berlin, main floor",    "serialno": "42",    "model": "Speaking coffee machine"  },  "features": {    "coffee-brewer": {      "definition": ["com.acme:coffeebrewer:0.1.0"],      "properties": {        "brewed-coffees": 0      }    },    "water-tank": {      "properties": {        "configuration": {          "brewingTemp": 87,          "tempToHold": 50,          "timeoutSeconds": 6000        },        "status": {          "waterAmount": 731,          "temperature": 44        }      }    }  }}```### Permissions for patching an existing ThingFor updating an existing thing, the authorized subject needs **WRITE** permission on those parts of the thingthat are affected by the merge update.For example, to successfully execute the above example the authorized subject needs to have unrestricted*WRITE* permissions on all affected paths of the JSON merge patch: `attributes/manufacturingYear`,`features/water-tank/properties/configuration/smartMode`,`features/water-tank/properties/configuration/tempToHold`. The *WRITE* permission must not be revoked on anylevel further down the hierarchy. Consequently it is also sufficient for the authorized subject to haveunrestricted *WRITE* permission at root level or unrestricted *WRITE* permission at `/attributes` and`/features` etc.
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
    class WithThingItemRequestBuilderPatchRequestConfiguration(RequestConfiguration[WithThingItemRequestBuilderPatchQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class WithThingItemRequestBuilderPutQueryParameters():
        """
        Create or update the thing specified by the `thingId` path parameter and the optional JSON body.* If you set a new `thingId` in the path, a thing will be created.* If you set an existing `thingId` in the path, the thing will be updated.### Create a new thingAt the initial creation of a thing, only a valid `thingId` is required.However, you can create a full-fledged thing all at once.### Example:To create a coffee maker thing, set the `thingId` in the path, e.g. to "com.acme.coffeemaker:BE-42"and the body part, like in the following snippet.``` {   "definition": "com.acme:coffeebrewer:0.1.0",   "attributes": {     "manufacturer": "ACME demo corp.",     "location": "Berlin, main floor",     "serialno": "42",     "model": "Speaking coffee machine"   },   "features": {     "coffee-brewer": {       "definition": [ "com.acme:coffeebrewer:0.1.0" ],       "properties": {         "brewed-coffees": 0       }     },     "water-tank": {       "properties": {         "configuration": {           "smartMode": true,           "brewingTemp": 87,           "tempToHold": 44,           "timeoutSeconds": 6000         },         "status": {           "waterAmount": 731,           "temperature": 44         }       }     }   }  } ```As the example does not set a policy in the request body, but the thing concept requires one,the service will create a default policy. The default policy, has the exactly same idas the thing, and grants ALL permissions to the authorized subject.In case you need to associate the new thing to an already existing policy you can additionallyset a policy e.g. "policyId": "com.acme.coffeemaker:policy-1" as the first element in the body part.Keep in mind, that you can also change the assignment to another policy anytime,with a request on the sub-resource "PUT /things/{thingId}/policyId"The field `_created` is filled automatically with the timestamp of the creation. The field is read-only and canbe retrieved later by explicitly selecting it or used in search filters.### Update an existing thingFor updating an existing thing, the authorized subject needs **WRITE** permission on the thing's root resource.The ID of a thing cannot be changed after creation. Any `thingId`specified in the request body is therefore ignored.
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
    class WithThingItemRequestBuilderPutRequestConfiguration(RequestConfiguration[WithThingItemRequestBuilderPutQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

