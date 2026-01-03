from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .activate_token_integration.activate_token_integration_request_builder import ActivateTokenIntegrationRequestBuilder
    from .deactivate_token_integration.deactivate_token_integration_request_builder import DeactivateTokenIntegrationRequestBuilder

class ActionsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/2/policies/{policyId}/actions
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new ActionsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/2/policies/{policyId}/actions", path_parameters)
    
    @property
    def activate_token_integration(self) -> ActivateTokenIntegrationRequestBuilder:
        """
        The activateTokenIntegration property
        """
        from .activate_token_integration.activate_token_integration_request_builder import ActivateTokenIntegrationRequestBuilder

        return ActivateTokenIntegrationRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def deactivate_token_integration(self) -> DeactivateTokenIntegrationRequestBuilder:
        """
        The deactivateTokenIntegration property
        """
        from .deactivate_token_integration.deactivate_token_integration_request_builder import DeactivateTokenIntegrationRequestBuilder

        return DeactivateTokenIntegrationRequestBuilder(self.request_adapter, self.path_parameters)
    

