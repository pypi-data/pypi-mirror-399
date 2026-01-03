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
    from .....models.new_policy import NewPolicy
    from .....models.policy import Policy
    from .actions.actions_request_builder import ActionsRequestBuilder
    from .entries.entries_request_builder import EntriesRequestBuilder
    from .imports.imports_request_builder import ImportsRequestBuilder

class WithPolicyItemRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/2/policies/{policyId}
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new WithPolicyItemRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/2/policies/{policyId}{?allow%2Dpolicy%2Dlockout*,fields*,response%2Drequired*,timeout*}", path_parameters)
    
    async def delete(self,request_configuration: Optional[RequestConfiguration[WithPolicyItemRequestBuilderDeleteQueryParameters]] = None) -> None:
        """
        Deletes the policy identified by the `policyId` path parameter. Deletinga policy does not implicitly delete other entities (e.g. things) whichuse this policy.Note: Delete the respective things **before** deleting thepolicy, otherwise nobody has permission to read, update, or delete the things.If you accidentally run into such a scenario, re-create the policy viaPUT `/policies/{policyId}`.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: None
        """
        request_info = self.to_delete_request_information(
            request_configuration
        )
        from .....models.advanced_error import AdvancedError

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
            "403": AdvancedError,
            "404": AdvancedError,
            "412": AdvancedError,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_no_response_content_async(request_info, error_mapping)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[WithPolicyItemRequestBuilderGetQueryParameters]] = None) -> Optional[Policy]:
        """
        Returns the complete policy identified by the `policyId` path parameter. Theresponse contains the policy as JSON object.Tip: If you don't know the policy ID of a thing, request it via GET `/things/{thingId}`.Optionally, you can use the field selectors (see parameter `fields`) to only get specific fields,which you are interested in.### Example:Use the field selector `_revision` to retrieve the revision of the policy.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[Policy]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from .....models.advanced_error import AdvancedError

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
            "404": AdvancedError,
            "412": AdvancedError,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from .....models.policy import Policy

        return await self.request_adapter.send_async(request_info, Policy, error_mapping)
    
    async def put(self,body: NewPolicy, request_configuration: Optional[RequestConfiguration[WithPolicyItemRequestBuilderPutQueryParameters]] = None) -> Optional[NewPolicy]:
        """
        Create or update the policy specified by the policyId path parameter.* If you set a new policyId in the path, a new policy will be created.* If you set an existing policyId in the path, the policy will be updated.### Create a new policyAt the initial creation of a policy, at least one valid entry is required. However, you can create a full-fledged policy all at once.By default the authorized subject needs WRITE permission on the root resource of the created policy. You canhowever omit this check by setting the parameter `allow-policy-lockout` to `true`.Example: To create a policy for multiple coffee maker things,which gives **yourself** all permissions on all resources, set the policyId in the path,e.g. to "com.acme.coffeemaker:policy-01" and the body part, like in the following snippet.```{  "entries": {    "DEFAULT": {      "subjects": {        "{{ request:subjectId }}": {          "type": "the creator"        }      },      "resources": {        "policy:/": {          "grant": [            "READ",            "WRITE"          ],          "revoke": []        },        "thing:/": {          "grant": [            "READ",            "WRITE"          ],          "revoke": []        },        "message:/": {          "grant": [            "READ",            "WRITE"          ],          "revoke": []        }      }    }  },  "imports": {    "com.acme:importedPolicy" : {      "entries": [ "IMPORTED" ]    }  }}```### Update an existing policyFor updating an existing policy, the authorized subject needs WRITE permission on the policy's root resource.The ID of a policy cannot be changed after creation. Any `policyId` specified in the request body is therefore ignored.### Partially update an existing policyPartial updates are not supported.If you need to create or update a specific label, resource, or subject, please use the respective sub-resources.
        param body: Policy consisting of policy entries
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[NewPolicy]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_put_request_information(
            body, request_configuration
        )
        from .....models.advanced_error import AdvancedError

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": AdvancedError,
            "401": AdvancedError,
            "403": AdvancedError,
            "404": AdvancedError,
            "412": AdvancedError,
            "413": AdvancedError,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from .....models.new_policy import NewPolicy

        return await self.request_adapter.send_async(request_info, NewPolicy, error_mapping)
    
    def to_delete_request_information(self,request_configuration: Optional[RequestConfiguration[WithPolicyItemRequestBuilderDeleteQueryParameters]] = None) -> RequestInformation:
        """
        Deletes the policy identified by the `policyId` path parameter. Deletinga policy does not implicitly delete other entities (e.g. things) whichuse this policy.Note: Delete the respective things **before** deleting thepolicy, otherwise nobody has permission to read, update, or delete the things.If you accidentally run into such a scenario, re-create the policy viaPUT `/policies/{policyId}`.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.DELETE, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[WithPolicyItemRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Returns the complete policy identified by the `policyId` path parameter. Theresponse contains the policy as JSON object.Tip: If you don't know the policy ID of a thing, request it via GET `/things/{thingId}`.Optionally, you can use the field selectors (see parameter `fields`) to only get specific fields,which you are interested in.### Example:Use the field selector `_revision` to retrieve the revision of the policy.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_put_request_information(self,body: NewPolicy, request_configuration: Optional[RequestConfiguration[WithPolicyItemRequestBuilderPutQueryParameters]] = None) -> RequestInformation:
        """
        Create or update the policy specified by the policyId path parameter.* If you set a new policyId in the path, a new policy will be created.* If you set an existing policyId in the path, the policy will be updated.### Create a new policyAt the initial creation of a policy, at least one valid entry is required. However, you can create a full-fledged policy all at once.By default the authorized subject needs WRITE permission on the root resource of the created policy. You canhowever omit this check by setting the parameter `allow-policy-lockout` to `true`.Example: To create a policy for multiple coffee maker things,which gives **yourself** all permissions on all resources, set the policyId in the path,e.g. to "com.acme.coffeemaker:policy-01" and the body part, like in the following snippet.```{  "entries": {    "DEFAULT": {      "subjects": {        "{{ request:subjectId }}": {          "type": "the creator"        }      },      "resources": {        "policy:/": {          "grant": [            "READ",            "WRITE"          ],          "revoke": []        },        "thing:/": {          "grant": [            "READ",            "WRITE"          ],          "revoke": []        },        "message:/": {          "grant": [            "READ",            "WRITE"          ],          "revoke": []        }      }    }  },  "imports": {    "com.acme:importedPolicy" : {      "entries": [ "IMPORTED" ]    }  }}```### Update an existing policyFor updating an existing policy, the authorized subject needs WRITE permission on the policy's root resource.The ID of a policy cannot be changed after creation. Any `policyId` specified in the request body is therefore ignored.### Partially update an existing policyPartial updates are not supported.If you need to create or update a specific label, resource, or subject, please use the respective sub-resources.
        param body: Policy consisting of policy entries
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
    
    def with_url(self,raw_url: str) -> WithPolicyItemRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: WithPolicyItemRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return WithPolicyItemRequestBuilder(self.request_adapter, raw_url)
    
    @property
    def actions(self) -> ActionsRequestBuilder:
        """
        The actions property
        """
        from .actions.actions_request_builder import ActionsRequestBuilder

        return ActionsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def entries(self) -> EntriesRequestBuilder:
        """
        The entries property
        """
        from .entries.entries_request_builder import EntriesRequestBuilder

        return EntriesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def imports(self) -> ImportsRequestBuilder:
        """
        The imports property
        """
        from .imports.imports_request_builder import ImportsRequestBuilder

        return ImportsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @dataclass
    class WithPolicyItemRequestBuilderDeleteQueryParameters():
        """
        Deletes the policy identified by the `policyId` path parameter. Deletinga policy does not implicitly delete other entities (e.g. things) whichuse this policy.Note: Delete the respective things **before** deleting thepolicy, otherwise nobody has permission to read, update, or delete the things.If you accidentally run into such a scenario, re-create the policy viaPUT `/policies/{policyId}`.
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "response_required":
                return "response%2Drequired"
            if original_name == "timeout":
                return "timeout"
            return original_name
        
        # Defines whether a response is required to the API call or not - if set to `false` the response will directlysent back with a status code of `202` (Accepted).The default (if ommited) response is `true`.
        response_required: Optional[bool] = None

        # Defines how long the backend should wait for completion of the request, e.g. applied when waiting for requestedacknowledgements via the `requested-acks` param. Can be specified without unit (then seconds are assumed) ortogether with `s`, `ms` or `m` unit. Example: `42s`, `1m`.The default (if omitted) and maximum timeout is `60s`. A value of `0` applies fire and forget semantics forthe command resulting in setting `response-required=false`.
        timeout: Optional[str] = None

    
    @dataclass
    class WithPolicyItemRequestBuilderDeleteRequestConfiguration(RequestConfiguration[WithPolicyItemRequestBuilderDeleteQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class WithPolicyItemRequestBuilderGetQueryParameters():
        """
        Returns the complete policy identified by the `policyId` path parameter. Theresponse contains the policy as JSON object.Tip: If you don't know the policy ID of a thing, request it via GET `/things/{thingId}`.Optionally, you can use the field selectors (see parameter `fields`) to only get specific fields,which you are interested in.### Example:Use the field selector `_revision` to retrieve the revision of the policy.
        """
        # Contains a comma-separated list of fields to be included in the returnedJSON.#### Selectable fields* `policyId`* `entries`   Supports selecting arbitrary sub-fields by using a comma-separated list:    * several entry paths can be passed as a comma-separated list of JSON pointers (RFC-6901)      For example:        * `?fields=entries/ditto` would select only the `ditto` entry value(if present)        * `?fields=entries/ditto,entries/user` would select only `ditto` and           `user` entry values (if present)  Supports selecting arbitrary sub-fields of objects by wrapping sub-fields inside parentheses `( )`:    * a comma-separated list of sub-fields (a sub-field is a JSON pointer (RFC-6901)      separated with `/`) to select    * sub-selectors can be used to request only specific sub-fields by placing expressions      in parentheses `( )` after a selected subfield      For example:       * `?fields=entries(ditto,user)` would select only `ditto`          and `user` entry values (if present)       * `?fields=entries(ditto/subjects)` would select the `subjects` value          inside the `ditto` entry       * `?fields=entries/ditto/subjects(issuer:google,issuer:azure)` would select the `issuer:google` and          `issuer:azure` values inside the `subjects` object inside the `entries` object* `_namespace`  Specifically selects the namespace also contained in the `policyId`* `_revision`  Specifically selects the revision of the policy. The revision is a counter, which is incremented on each modification of a policy.* `_created`  Specifically selects the created timestamp of the policy in ISO-8601 UTC format. The timestamp is set on creation of a policy.* `_modified`  Specifically selects the modified timestamp of the policy in ISO-8601 UTC format. The timestamp is set on each modification of a policy.* `_metadata`  Specifically selects the Metadata of the policy. The content is a JSON object having the policy's JSON structure with the difference that the JSON leaves of the policy are JSON objects containing the metadata.#### Examples* `?fields=policyId,entries,_revision`* `?fields=entries(ditto,user),_namespace`
        fields: Optional[str] = None

        # Defines how long the backend should wait for completion of the request, e.g. applied when waiting for requestedacknowledgements via the `requested-acks` param. Can be specified without unit (then seconds are assumed) ortogether with `s`, `ms` or `m` unit. Example: `42s`, `1m`.The default (if omitted) and maximum timeout is `60s`. A value of `0` applies fire and forget semantics forthe command resulting in setting `response-required=false`.
        timeout: Optional[str] = None

    
    @dataclass
    class WithPolicyItemRequestBuilderGetRequestConfiguration(RequestConfiguration[WithPolicyItemRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class WithPolicyItemRequestBuilderPutQueryParameters():
        """
        Create or update the policy specified by the policyId path parameter.* If you set a new policyId in the path, a new policy will be created.* If you set an existing policyId in the path, the policy will be updated.### Create a new policyAt the initial creation of a policy, at least one valid entry is required. However, you can create a full-fledged policy all at once.By default the authorized subject needs WRITE permission on the root resource of the created policy. You canhowever omit this check by setting the parameter `allow-policy-lockout` to `true`.Example: To create a policy for multiple coffee maker things,which gives **yourself** all permissions on all resources, set the policyId in the path,e.g. to "com.acme.coffeemaker:policy-01" and the body part, like in the following snippet.```{  "entries": {    "DEFAULT": {      "subjects": {        "{{ request:subjectId }}": {          "type": "the creator"        }      },      "resources": {        "policy:/": {          "grant": [            "READ",            "WRITE"          ],          "revoke": []        },        "thing:/": {          "grant": [            "READ",            "WRITE"          ],          "revoke": []        },        "message:/": {          "grant": [            "READ",            "WRITE"          ],          "revoke": []        }      }    }  },  "imports": {    "com.acme:importedPolicy" : {      "entries": [ "IMPORTED" ]    }  }}```### Update an existing policyFor updating an existing policy, the authorized subject needs WRITE permission on the policy's root resource.The ID of a policy cannot be changed after creation. Any `policyId` specified in the request body is therefore ignored.### Partially update an existing policyPartial updates are not supported.If you need to create or update a specific label, resource, or subject, please use the respective sub-resources.
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
            if original_name == "response_required":
                return "response%2Drequired"
            if original_name == "timeout":
                return "timeout"
            return original_name
        
        # Defines whether a subject is allowed to create a policy without having WRITE permission on the policyresource of the created policy.The default (if ommited) is `false`.
        allow_policy_lockout: Optional[bool] = None

        # Defines whether a response is required to the API call or not - if set to `false` the response will directlysent back with a status code of `202` (Accepted).The default (if ommited) response is `true`.
        response_required: Optional[bool] = None

        # Defines how long the backend should wait for completion of the request, e.g. applied when waiting for requestedacknowledgements via the `requested-acks` param. Can be specified without unit (then seconds are assumed) ortogether with `s`, `ms` or `m` unit. Example: `42s`, `1m`.The default (if omitted) and maximum timeout is `60s`. A value of `0` applies fire and forget semantics forthe command resulting in setting `response-required=false`.
        timeout: Optional[str] = None

    
    @dataclass
    class WithPolicyItemRequestBuilderPutRequestConfiguration(RequestConfiguration[WithPolicyItemRequestBuilderPutQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

