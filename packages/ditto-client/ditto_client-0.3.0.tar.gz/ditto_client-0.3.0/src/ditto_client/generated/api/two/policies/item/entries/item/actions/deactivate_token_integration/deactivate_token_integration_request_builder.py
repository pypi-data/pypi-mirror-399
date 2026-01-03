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

class DeactivateTokenIntegrationRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/2/policies/{policyId}/entries/{label}/actions/deactivateTokenIntegration
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new DeactivateTokenIntegrationRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/2/policies/{policyId}/entries/{label}/actions/deactivateTokenIntegration", path_parameters)
    
    async def post(self,request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> None:
        """
        **This action only works when authenticated with a Json Web Token (JWT).**Based on the authenticated token (JWT), **this policy entry** is checked to match those conditions:* the authenticated token is granted the `EXECUTE` permission to perform the `deactivateTokenIntegration` action* one of the subject IDs is contained in the authenticated tokenWhen all conditions match, the calculated subject with information extracted from the authenticated JWT is **removedfrom this policy entry**.The injected subjects expire when the JWT expires. The `expiry` timestamp (a string in ISO-8601 format)specifies how long the specific subject will have access to the resource secured by the policy.The subject will be automatically deleted from the policy once this timestamp is reached.To give the subject a chance to prolong the access he can configure a connection to get announcements.Policy announcements are published to websockets and connections that have the relevant subject ID.The settings under `announcement` control when a policy announcement is published (before expiry or when deleted).If the field `requestedAcks` is set, then the announcements are published with at-least-once delivery untilthe acknowledgement requests under labels are fulfilled.If a "beforeExpiry" announcement was sent without acknowledgement requests, or the a "beforeExpiry"announcement was acknowledged, the "whenDeleted" announcement will not be triggered.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: None
        """
        request_info = self.to_post_request_information(
            request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_no_response_content_async(request_info, None)
    
    def to_post_request_information(self,request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        **This action only works when authenticated with a Json Web Token (JWT).**Based on the authenticated token (JWT), **this policy entry** is checked to match those conditions:* the authenticated token is granted the `EXECUTE` permission to perform the `deactivateTokenIntegration` action* one of the subject IDs is contained in the authenticated tokenWhen all conditions match, the calculated subject with information extracted from the authenticated JWT is **removedfrom this policy entry**.The injected subjects expire when the JWT expires. The `expiry` timestamp (a string in ISO-8601 format)specifies how long the specific subject will have access to the resource secured by the policy.The subject will be automatically deleted from the policy once this timestamp is reached.To give the subject a chance to prolong the access he can configure a connection to get announcements.Policy announcements are published to websockets and connections that have the relevant subject ID.The settings under `announcement` control when a policy announcement is published (before expiry or when deleted).If the field `requestedAcks` is set, then the announcements are published with at-least-once delivery untilthe acknowledgement requests under labels are fulfilled.If a "beforeExpiry" announcement was sent without acknowledgement requests, or the a "beforeExpiry"announcement was acknowledged, the "whenDeleted" announcement will not be triggered.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.POST, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        return request_info
    
    def with_url(self,raw_url: str) -> DeactivateTokenIntegrationRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: DeactivateTokenIntegrationRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return DeactivateTokenIntegrationRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class DeactivateTokenIntegrationRequestBuilderPostRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

