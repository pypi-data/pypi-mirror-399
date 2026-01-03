from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .item.with_message_subject_item_request_builder import WithMessageSubjectItemRequestBuilder

class MessagesRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/2/things/{thingId}/outbox/messages
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new MessagesRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/2/things/{thingId}/outbox/messages", path_parameters)
    
    def by_message_subject(self,message_subject: str) -> WithMessageSubjectItemRequestBuilder:
        """
        Gets an item from the ApiSdk.api.Two.things.item.outbox.messages.item collection
        param message_subject: The subject of the Message - has to conform to RFC-3986 (URI)
        Returns: WithMessageSubjectItemRequestBuilder
        """
        if message_subject is None:
            raise TypeError("message_subject cannot be null.")
        from .item.with_message_subject_item_request_builder import WithMessageSubjectItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["messageSubject"] = message_subject
        return WithMessageSubjectItemRequestBuilder(self.request_adapter, url_tpl_params)
    

