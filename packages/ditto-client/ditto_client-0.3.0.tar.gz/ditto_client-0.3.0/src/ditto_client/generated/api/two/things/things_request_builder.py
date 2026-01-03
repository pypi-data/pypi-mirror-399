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
    from ....models.new_thing import NewThing
    from ....models.thing import Thing
    from ....models.thing424_error import Thing424Error
    from .item.with_thing_item_request_builder import WithThingItemRequestBuilder

class ThingsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/2/things
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new ThingsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/2/things{?allow%2Dpolicy%2Dlockout*,fields*,ids*,namespace*,requested%2Dacks*,response%2Drequired*,timeout*}", path_parameters)
    
    def by_thing_id(self,thing_id: str) -> WithThingItemRequestBuilder:
        """
        Gets an item from the ApiSdk.api.Two.things.item collection
        param thing_id: The ID of a thing needs to follow the namespaced entity ID notation (see [Ditto documentation on namespaced entity IDs](https://www.eclipse.dev/ditto/basic-namespaces-and-names.html#namespaced-id)).
        Returns: WithThingItemRequestBuilder
        """
        if thing_id is None:
            raise TypeError("thing_id cannot be null.")
        from .item.with_thing_item_request_builder import WithThingItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["thingId"] = thing_id
        return WithThingItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[ThingsRequestBuilderGetQueryParameters]] = None) -> Optional[list[Thing]]:
        """
        Returns all visible things or things passed in by the required parameter `ids`, which you (the authorized subject) are allowed to read.Optionally, if you want to retrieve only some of the thing's fields, you can use the specific field selectors (see parameter `fields`) .Tip: In order to formulate a `filter` which things to search for, take a look at the `/search` resource.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[list[Thing]]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ....models.advanced_error import AdvancedError
        from ....models.thing424_error import Thing424Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ....models.thing import Thing

        return await self.request_adapter.send_collection_async(request_info, Thing, error_mapping)
    
    async def post(self,body: NewThing, request_configuration: Optional[RequestConfiguration[ThingsRequestBuilderPostQueryParameters]] = None) -> Optional[Thing]:
        """
        Creates a thing with a default `thingId` and a default `policyId`.The thing will be empty, i.e. no features, definition, attributes etc. by default.The default `thingId` consists of your default namespace and a UUID.The default `policyId` is identical with the default `thingId`, and allows the currently authorized subject all permissions.In case you need to create a thing with a specific ID, use a *PUT* request instead, as any `thingId` specified in the request body will be ignored.The field `_created` is filled automatically with the timestamp of the creation. The field is read-only and canbe retrieved later by explicitly selecting it or used in search filters.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[Thing]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        from ....models.advanced_error import AdvancedError
        from ....models.thing424_error import Thing424Error

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
        from ....models.thing import Thing

        return await self.request_adapter.send_async(request_info, Thing, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[ThingsRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Returns all visible things or things passed in by the required parameter `ids`, which you (the authorized subject) are allowed to read.Optionally, if you want to retrieve only some of the thing's fields, you can use the specific field selectors (see parameter `fields`) .Tip: In order to formulate a `filter` which things to search for, take a look at the `/search` resource.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_post_request_information(self,body: NewThing, request_configuration: Optional[RequestConfiguration[ThingsRequestBuilderPostQueryParameters]] = None) -> RequestInformation:
        """
        Creates a thing with a default `thingId` and a default `policyId`.The thing will be empty, i.e. no features, definition, attributes etc. by default.The default `thingId` consists of your default namespace and a UUID.The default `policyId` is identical with the default `thingId`, and allows the currently authorized subject all permissions.In case you need to create a thing with a specific ID, use a *PUT* request instead, as any `thingId` specified in the request body will be ignored.The field `_created` is filled automatically with the timestamp of the creation. The field is read-only and canbe retrieved later by explicitly selecting it or used in search filters.
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
    
    def with_url(self,raw_url: str) -> ThingsRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: ThingsRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return ThingsRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class ThingsRequestBuilderGetQueryParameters():
        """
        Returns all visible things or things passed in by the required parameter `ids`, which you (the authorized subject) are allowed to read.Optionally, if you want to retrieve only some of the thing's fields, you can use the specific field selectors (see parameter `fields`) .Tip: In order to formulate a `filter` which things to search for, take a look at the `/search` resource.
        """
        # Contains a comma-separated list of fields to be included in the returnedJSON. attributes can be selected in the same manner.#### Selectable fields* `thingId`* `policyId`* `definition`* `attributes`   Supports selecting arbitrary sub-fields by using a comma-separated list:    * several attribute paths can be passed as a comma-separated list of JSON pointers (RFC-6901)      For example:        * `?fields=attributes/model` would select only `model` attribute value (if present)        * `?fields=attributes/model,attributes/location` would select only `model` and           `location` attribute values (if present)  Supports selecting arbitrary sub-fields of objects by wrapping sub-fields inside parentheses `( )`:    * a comma-separated list of sub-fields (a sub-field is a JSON pointer (RFC-6901)      separated with `/`) to select    * sub-selectors can be used to request only specific sub-fields by placing expressions      in parentheses `( )` after a selected subfield      For example:       * `?fields=attributes(model,location)` would select only `model`          and `location` attribute values (if present)       * `?fields=attributes(coffeemaker/serialno)` would select the `serialno` value          inside the `coffeemaker` object       * `?fields=attributes/address/postal(city,street)` would select the `city` and          `street` values inside the `postal` object inside the `address` object* `features`  Supports selecting arbitrary fields in features similar to `attributes` (see also features documentation for more details)* `_namespace`  Specifically selects the namespace also contained in the `thingId`* `_revision`  Specifically selects the revision of the thing. The revision is a counter, which is incremented on each modification of a thing.* `_created`  Specifically selects the created timestamp of the thing in ISO-8601 UTC format. The timestamp is set on creation of a thing.* `_modified`  Specifically selects the modified timestamp of the thing in ISO-8601 UTC format. The timestamp is set on each modification of a thing.* `_metadata`  Specifically selects the Metadata of the thing. The content is a JSON object having the Thing's JSON structure with the difference that the JSON leaves of the Thing are JSON objects containing the metadata.* `_policy`  Specifically selects the content of the policy associated to the thing. (By default, only the policyId is returned.)#### Examples* `?fields=thingId,attributes,features`* `?fields=attributes(model,manufacturer),features`
        fields: Optional[str] = None

        # Contains a comma-separated list of `thingId`s to retrieve in one single request.
        ids: Optional[str] = None

        # Defines how long the backend should wait for completion of the request, e.g. applied when waiting for requestedacknowledgements via the `requested-acks` param. Can be specified without unit (then seconds are assumed) ortogether with `s`, `ms` or `m` unit. Example: `42s`, `1m`.The default (if omitted) and maximum timeout is `60s`. A value of `0` applies fire and forget semantics forthe command resulting in setting `response-required=false`.
        timeout: Optional[str] = None

    
    @dataclass
    class ThingsRequestBuilderGetRequestConfiguration(RequestConfiguration[ThingsRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class ThingsRequestBuilderPostQueryParameters():
        """
        Creates a thing with a default `thingId` and a default `policyId`.The thing will be empty, i.e. no features, definition, attributes etc. by default.The default `thingId` consists of your default namespace and a UUID.The default `policyId` is identical with the default `thingId`, and allows the currently authorized subject all permissions.In case you need to create a thing with a specific ID, use a *PUT* request instead, as any `thingId` specified in the request body will be ignored.The field `_created` is filled automatically with the timestamp of the creation. The field is read-only and canbe retrieved later by explicitly selecting it or used in search filters.
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "allow_policy_lockout":
                return "allow%2Dpolicy%2Dlockout"
            if original_name == "requested_acks":
                return "requested%2Dacks"
            if original_name == "response_required":
                return "response%2Drequired"
            if original_name == "namespace":
                return "namespace"
            if original_name == "timeout":
                return "timeout"
            return original_name
        
        # Defines whether a subject is allowed to create a policy without having WRITE permission on the policyresource of the created policy.The default (if ommited) is `false`.
        allow_policy_lockout: Optional[bool] = None

        # Defines a custom namespace for the thing while generating a new thing ID.
        namespace: Optional[str] = None

        # Contains the "requested acknowledgements" for this modifying request as comma separated list. The HTTP call willblock until all requested acknowledgements were aggregated or will time out based on the specified `timeout`parameter.The default (if omitted) requested acks is `requested-acks=twin-persisted` which will block theHTTP call until the change was persited to the twin.
        requested_acks: Optional[str] = None

        # Defines whether a response is required to the API call or not - if set to `false` the response will directlysent back with a status code of `202` (Accepted).The default (if ommited) response is `true`.
        response_required: Optional[bool] = None

        # Defines how long the backend should wait for completion of the request, e.g. applied when waiting for requestedacknowledgements via the `requested-acks` param. Can be specified without unit (then seconds are assumed) ortogether with `s`, `ms` or `m` unit. Example: `42s`, `1m`.The default (if omitted) and maximum timeout is `60s`. A value of `0` applies fire and forget semantics forthe command resulting in setting `response-required=false`.
        timeout: Optional[str] = None

    
    @dataclass
    class ThingsRequestBuilderPostRequestConfiguration(RequestConfiguration[ThingsRequestBuilderPostQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

