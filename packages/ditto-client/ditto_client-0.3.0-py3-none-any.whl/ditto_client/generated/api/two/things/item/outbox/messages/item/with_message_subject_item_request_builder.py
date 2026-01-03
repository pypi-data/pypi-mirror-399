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
    from ........models.with_message_subject424_error import WithMessageSubject424Error

class WithMessageSubjectItemRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/2/things/{thingId}/outbox/messages/{messageSubject}
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new WithMessageSubjectItemRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/2/things/{thingId}/outbox/messages/{messageSubject}{?condition*,requested%2Dacks*,timeout*}", path_parameters)
    
    async def post(self,body: str, request_configuration: Optional[RequestConfiguration[WithMessageSubjectItemRequestBuilderPostQueryParameters]] = None) -> None:
        """
        Send a message with the subject `messageSubject` **from** the thingidentified by the `thingId` path parameter. The request body containsthe message payload and the `Content-Type` header defines its type.The HTTP request blocks until all acknowledgement requests are fulfilled.By default, it blocks until a response to the message is availableor until the `timeout` is expired. If many clients respond tothe issued message, the first response will complete the HTTP request.In order to handle the message in a fire and forget manner, adda query-parameter `timeout=0` to the request.Note that the client chooses which HTTP status code it wants to return. Dittowill forward the status code to you. (Also note that '204 - No Content' status codewill never return a body, even if the client responded with a body).### WhoYou will need `WRITE` permission on the root "message:/" resource, or at leastthe resource `message:/outbox/messages/messageSubject`.Such permission is managed  within the policy which controls the access on the thing.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: None
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        from ........models.advanced_error import AdvancedError
        from ........models.with_message_subject424_error import WithMessageSubject424Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
            "403": AdvancedError,
            "404": AdvancedError,
            "408": AdvancedError,
            "412": AdvancedError,
            "413": AdvancedError,
            "424": WithMessageSubject424Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_no_response_content_async(request_info, error_mapping)
    
    def to_post_request_information(self,body: str, request_configuration: Optional[RequestConfiguration[WithMessageSubjectItemRequestBuilderPostQueryParameters]] = None) -> RequestInformation:
        """
        Send a message with the subject `messageSubject` **from** the thingidentified by the `thingId` path parameter. The request body containsthe message payload and the `Content-Type` header defines its type.The HTTP request blocks until all acknowledgement requests are fulfilled.By default, it blocks until a response to the message is availableor until the `timeout` is expired. If many clients respond tothe issued message, the first response will complete the HTTP request.In order to handle the message in a fire and forget manner, adda query-parameter `timeout=0` to the request.Note that the client chooses which HTTP status code it wants to return. Dittowill forward the status code to you. (Also note that '204 - No Content' status codewill never return a body, even if the client responded with a body).### WhoYou will need `WRITE` permission on the root "message:/" resource, or at leastthe resource `message:/outbox/messages/messageSubject`.Such permission is managed  within the policy which controls the access on the thing.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = RequestInformation(Method.POST, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        request_info.set_content_from_scalar(self.request_adapter, "application/json", body)
        return request_info
    
    def with_url(self,raw_url: str) -> WithMessageSubjectItemRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: WithMessageSubjectItemRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return WithMessageSubjectItemRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class WithMessageSubjectItemRequestBuilderPostQueryParameters():
        """
        Send a message with the subject `messageSubject` **from** the thingidentified by the `thingId` path parameter. The request body containsthe message payload and the `Content-Type` header defines its type.The HTTP request blocks until all acknowledgement requests are fulfilled.By default, it blocks until a response to the message is availableor until the `timeout` is expired. If many clients respond tothe issued message, the first response will complete the HTTP request.In order to handle the message in a fire and forget manner, adda query-parameter `timeout=0` to the request.Note that the client chooses which HTTP status code it wants to return. Dittowill forward the status code to you. (Also note that '204 - No Content' status codewill never return a body, even if the client responded with a body).### WhoYou will need `WRITE` permission on the root "message:/" resource, or at leastthe resource `message:/outbox/messages/messageSubject`.Such permission is managed  within the policy which controls the access on the thing.
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
            if original_name == "condition":
                return "condition"
            if original_name == "timeout":
                return "timeout"
            return original_name
        
        # Defines that the request should only be processed if the given condition is met. The condition can be specified using RQL syntax.#### ExamplesE.g. if the temperature is not 23.9 update it to 23.9:* ```PUT /api/2/things/{thingId}/features/temperature/properties/value?condition=ne(features/temperature/properties/value,23.9)```   `body: 23.9`Further example conditions:* ```?condition=eq(features/temperature/properties/unit,"Celsius")```* ```?condition=ge(features/temperature/properties/lastModified,"2021-08-22T19:45:00Z")```* ```?condition=gt(_modified,"2021-08-05T12:17:00Z")```* ```?condition=exists(features/temperature/properties/value)```* ```?condition=and(gt(features/temperature/properties/value,18.5),lt(features/temperature/properties/value,25.2))```* ```?condition=or(gt(features/temperature/properties/value,18.5),not(exists(features/temperature/properties/value))```
        condition: Optional[str] = None

        # Contains the "requested acknowledgements" for this request as comma separated list. The HTTP call willblock until all requested acknowledgements were aggregated or will time out based on the specified `timeout`parameter.The default (if omitted) requested acks is `requested-acks=live-response` which will block theHTTP call until a subscriber of the live message sends a response.
        requested_acks: Optional[str] = None

        # Contains an optional timeout (in seconds) of how long to wait for the message response and therefore block theHTTP request. Default value (if omitted): 10 seconds. Maximum value: 60 seconds. A value of 0 seconds appliesfire and forget semantics for the message.
        timeout: Optional[int] = None

    
    @dataclass
    class WithMessageSubjectItemRequestBuilderPostRequestConfiguration(RequestConfiguration[WithMessageSubjectItemRequestBuilderPostQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

