from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .item.with_policy_item_request_builder import WithPolicyItemRequestBuilder

class PoliciesRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/2/policies
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new PoliciesRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/2/policies", path_parameters)
    
    def by_policy_id(self,policy_id: str) -> WithPolicyItemRequestBuilder:
        """
        Gets an item from the ApiSdk.api.Two.policies.item collection
        param policy_id: The ID of the policy needs to follow the namespaced entity ID notation (see [Ditto documentation on namespaced entity IDs](https://www.eclipse.dev/ditto/basic-namespaces-and-names.html#namespaced-id)).The namespace needs to:* conform to the reverse domain name notation
        Returns: WithPolicyItemRequestBuilder
        """
        if policy_id is None:
            raise TypeError("policy_id cannot be null.")
        from .item.with_policy_item_request_builder import WithPolicyItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["policyId"] = policy_id
        return WithPolicyItemRequestBuilder(self.request_adapter, url_tpl_params)
    

