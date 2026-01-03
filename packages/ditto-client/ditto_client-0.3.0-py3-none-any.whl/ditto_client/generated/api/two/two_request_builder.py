from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .check_permissions.check_permissions_request_builder import CheckPermissionsRequestBuilder
    from .cloudevents.cloudevents_request_builder import CloudeventsRequestBuilder
    from .connections.connections_request_builder import ConnectionsRequestBuilder
    from .policies.policies_request_builder import PoliciesRequestBuilder
    from .search.search_request_builder import SearchRequestBuilder
    from .things.things_request_builder import ThingsRequestBuilder
    from .whoami.whoami_request_builder import WhoamiRequestBuilder

class TwoRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/2
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new TwoRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/2", path_parameters)
    
    @property
    def check_permissions(self) -> CheckPermissionsRequestBuilder:
        """
        The checkPermissions property
        """
        from .check_permissions.check_permissions_request_builder import CheckPermissionsRequestBuilder

        return CheckPermissionsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def cloudevents(self) -> CloudeventsRequestBuilder:
        """
        The cloudevents property
        """
        from .cloudevents.cloudevents_request_builder import CloudeventsRequestBuilder

        return CloudeventsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def connections(self) -> ConnectionsRequestBuilder:
        """
        The connections property
        """
        from .connections.connections_request_builder import ConnectionsRequestBuilder

        return ConnectionsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def policies(self) -> PoliciesRequestBuilder:
        """
        The policies property
        """
        from .policies.policies_request_builder import PoliciesRequestBuilder

        return PoliciesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def search(self) -> SearchRequestBuilder:
        """
        The search property
        """
        from .search.search_request_builder import SearchRequestBuilder

        return SearchRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def things(self) -> ThingsRequestBuilder:
        """
        The things property
        """
        from .things.things_request_builder import ThingsRequestBuilder

        return ThingsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def whoami(self) -> WhoamiRequestBuilder:
        """
        The whoami property
        """
        from .whoami.whoami_request_builder import WhoamiRequestBuilder

        return WhoamiRequestBuilder(self.request_adapter, self.path_parameters)
    

