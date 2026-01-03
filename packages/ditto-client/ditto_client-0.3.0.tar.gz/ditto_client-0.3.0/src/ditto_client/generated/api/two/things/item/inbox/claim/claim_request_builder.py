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
    from .......models.claim424_error import Claim424Error

class ClaimRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/2/things/{thingId}/inbox/claim
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new ClaimRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/2/things/{thingId}/inbox/claim{?requested%2Dacks*,timeout*}", path_parameters)
    
    async def post(self,body: str, request_configuration: Optional[RequestConfiguration[ClaimRequestBuilderPostQueryParameters]] = None) -> None:
        """
        ### WhyA claiming process may enable an end-user to claim things and proof ownership thereof.Such a process is initially triggered via a claim message.This message can be sent to the things service with the HTTP API or the things-client.### HowAt this resource you can send a "claim" message to the thing identifiedby the `thingId` path parameter in order to gain access to it. The "claim" message is forwardedtogether with the request body and `Content-Type` header to client(s)which registered for Claim messages of the specific thing.The decision whether to grant access (by setting permissions) iscompletely up to the client(s) which handle the "claim" message.The HTTP request blocks until all acknowledgement requests are fulfilled.By default, it blocks until a response to the issued "claim" message isavailable or until the `timeout` is expired. If many clients respond tothe issued message, the first response will complete the HTTP request.Note that the client chooses which HTTP status code it wants to return. Dittowill forward the status code to you. (Also note that '204 - No Content' status codewill never return a body, even if the client responded with a body).### WhoNo special permission is required to issue a claim message.### ExampleSee [Claiming](https://www.eclipse.dev/ditto/protocol-specification-things-messages.html#sending-and-handling-claim-messages) concept in detail and example in GitHub.However, in that scenario, the policy should grant you READ and WRITE permission onthe "message:/" resource in order to be able to send the message and read the response.Further, the things-client which handles the "claim" message, needs permission to change the policy itself(i.e. READ and WRITE permission on the "policy:/" resource).
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: None
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        from .......models.advanced_error import AdvancedError
        from .......models.claim424_error import Claim424Error

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
            "404": AdvancedError,
            "408": AdvancedError,
            "413": AdvancedError,
            "424": Claim424Error,
            "429": AdvancedError,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_no_response_content_async(request_info, error_mapping)
    
    def to_post_request_information(self,body: str, request_configuration: Optional[RequestConfiguration[ClaimRequestBuilderPostQueryParameters]] = None) -> RequestInformation:
        """
        ### WhyA claiming process may enable an end-user to claim things and proof ownership thereof.Such a process is initially triggered via a claim message.This message can be sent to the things service with the HTTP API or the things-client.### HowAt this resource you can send a "claim" message to the thing identifiedby the `thingId` path parameter in order to gain access to it. The "claim" message is forwardedtogether with the request body and `Content-Type` header to client(s)which registered for Claim messages of the specific thing.The decision whether to grant access (by setting permissions) iscompletely up to the client(s) which handle the "claim" message.The HTTP request blocks until all acknowledgement requests are fulfilled.By default, it blocks until a response to the issued "claim" message isavailable or until the `timeout` is expired. If many clients respond tothe issued message, the first response will complete the HTTP request.Note that the client chooses which HTTP status code it wants to return. Dittowill forward the status code to you. (Also note that '204 - No Content' status codewill never return a body, even if the client responded with a body).### WhoNo special permission is required to issue a claim message.### ExampleSee [Claiming](https://www.eclipse.dev/ditto/protocol-specification-things-messages.html#sending-and-handling-claim-messages) concept in detail and example in GitHub.However, in that scenario, the policy should grant you READ and WRITE permission onthe "message:/" resource in order to be able to send the message and read the response.Further, the things-client which handles the "claim" message, needs permission to change the policy itself(i.e. READ and WRITE permission on the "policy:/" resource).
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
    
    def with_url(self,raw_url: str) -> ClaimRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: ClaimRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return ClaimRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class ClaimRequestBuilderPostQueryParameters():
        """
        ### WhyA claiming process may enable an end-user to claim things and proof ownership thereof.Such a process is initially triggered via a claim message.This message can be sent to the things service with the HTTP API or the things-client.### HowAt this resource you can send a "claim" message to the thing identifiedby the `thingId` path parameter in order to gain access to it. The "claim" message is forwardedtogether with the request body and `Content-Type` header to client(s)which registered for Claim messages of the specific thing.The decision whether to grant access (by setting permissions) iscompletely up to the client(s) which handle the "claim" message.The HTTP request blocks until all acknowledgement requests are fulfilled.By default, it blocks until a response to the issued "claim" message isavailable or until the `timeout` is expired. If many clients respond tothe issued message, the first response will complete the HTTP request.Note that the client chooses which HTTP status code it wants to return. Dittowill forward the status code to you. (Also note that '204 - No Content' status codewill never return a body, even if the client responded with a body).### WhoNo special permission is required to issue a claim message.### ExampleSee [Claiming](https://www.eclipse.dev/ditto/protocol-specification-things-messages.html#sending-and-handling-claim-messages) concept in detail and example in GitHub.However, in that scenario, the policy should grant you READ and WRITE permission onthe "message:/" resource in order to be able to send the message and read the response.Further, the things-client which handles the "claim" message, needs permission to change the policy itself(i.e. READ and WRITE permission on the "policy:/" resource).
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
            if original_name == "timeout":
                return "timeout"
            return original_name
        
        # Contains the "requested acknowledgements" for this request as comma separated list. The HTTP call willblock until all requested acknowledgements were aggregated or will time out based on the specified `timeout`parameter.The default (if omitted) requested acks is `requested-acks=live-response` which will block theHTTP call until a subscriber of the live message sends a response.
        requested_acks: Optional[str] = None

        # Contains an optional timeout (in seconds) of how long to wait for the Claim response and therefore block theHTTP request. Default value (if omitted): 60 seconds. Maximum value: 600 seconds. A value of 0 seconds appliesfire and forget semantics for the message.
        timeout: Optional[int] = None

    
    @dataclass
    class ClaimRequestBuilderPostRequestConfiguration(RequestConfiguration[ClaimRequestBuilderPostQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

