# konnektr_graph/client.py
"""
Konnektr Graph SDK (Azure-free) - Synchronous Client
"""
import json
from typing import Any, Dict, Generator, IO, Iterable, List, Optional, Union

import requests

from .auth.protocol import TokenProvider
from .exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
    ResourceExistsError,
    AuthenticationError,
)
from .models import (
    DeleteJob,
    DigitalTwinsModelData,
    ImportJob,
    IncomingRelationship,
)


class PagedIterator(Iterable):
    """
    Iterator for handling paged responses.
    Supports both nextLink in body and x-ms-continuation in headers.
    """

    def __init__(
        self,
        client: "KonnektrGraphClient",
        initial_url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        model_cls: Any = None,
        items_key: str = "value",
    ):
        """
        Initialize the paged iterator.

        Args:
            client: The KonnektrGraphClient instance.
            initial_url: The initial URL for the first page.
            method: The HTTP method to use. Defaults to "GET".
            headers: Optional headers to include in the request.
            json_data: Optional JSON body for the request.
            params: Optional query parameters for the request.
            model_cls: Optional class to instantiate for each item in the results.
            items_key: The key in the JSON response that contains the items list. Defaults to "value".
        """
        self._client = client
        self._url = initial_url
        self._method = method
        self._headers = headers or {}
        self._json_data = json_data
        self._params = params
        self._model_cls = model_cls
        self._items_key = items_key
        self._current_page_items = []
        self._current_page_index = 0
        self._continuation_token = None
        self._next_link = None
        self._first_page_fetched = False

    def __iter__(self):
        return self

    def __next__(self):
        if not self._first_page_fetched:
            self._fetch_page(is_initial=True)
            self._first_page_fetched = True

        if self._current_page_index < len(self._current_page_items):
            item = self._current_page_items[self._current_page_index]
            self._current_page_index += 1
            return item
        else:
            if not self._next_link and not self._continuation_token:
                raise StopIteration
            self._fetch_page()
            if not self._current_page_items:
                raise StopIteration
            self._current_page_index = 1
            return self._current_page_items[0]

    def _fetch_page(self, is_initial: bool = False):
        headers = self._headers.copy()
        params = self._params if is_initial else None

        request_url = self._url
        if not is_initial:
            if self._next_link:
                request_url = self._next_link
                if not request_url.startswith("http"):
                    request_url = f"{self._client.endpoint}/{request_url.lstrip('/')}"
            elif self._continuation_token:
                headers["x-ms-continuation"] = self._continuation_token

        response = self._client._request(
            self._method,
            request_url,
            headers=headers,
            json=self._json_data,
            params=params,
        )
        data = response.json()

        # Check for continuation token in headers
        token = response.headers.get("x-ms-continuation")
        self._continuation_token = token if token else None

        # Check for nextLink in body
        self._next_link = data.get("nextLink")

        # If continuationToken is in body (legacy or specific APIs)
        if not self._continuation_token:
            token = data.get("continuationToken")
            self._continuation_token = token if token else None

        raw_items = data.get(self._items_key, [])
        if self._model_cls and hasattr(self._model_cls, "from_dict"):
            self._current_page_items = [self._model_cls.from_dict(i) for i in raw_items]
        else:
            self._current_page_items = raw_items

        self._current_page_index = 0


class KonnektrGraphClient:

    def __init__(self, endpoint: str, credential: TokenProvider):
        """
        Initialize the Konnektr Graph Client.

        Args:
            endpoint: API endpoint (e.g. https://graph.konnektr.io)
            credential: TokenProvider credential for authentication.
        """
        if not endpoint.startswith("http"):
            endpoint = "https://" + endpoint
        self.endpoint = endpoint.rstrip("/")
        self.credential = credential

    def _request(
        self, method: str, url: str, headers: Optional[Dict[str, str]] = None, **kwargs
    ) -> requests.Response:
        if headers is None:
            headers = {}
        headers.update(self.credential.get_headers())

        # Ensure content type is set if json body is present and not set
        if "json" in kwargs and "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        response = requests.request(method, url, headers=headers, **kwargs)

        if not response.ok:
            self._handle_error(response)

        return response

    def _handle_error(self, response: requests.Response):
        try:
            error_data = response.json()
            message = json.dumps(error_data)
        except ValueError:
            message = response.text

        status_code = response.status_code
        if status_code == 404:
            raise ResourceNotFoundError(message, status_code)
        elif status_code == 409:
            raise ResourceExistsError(message, status_code)
        elif status_code in (401, 403):
            raise AuthenticationError(message, status_code)
        else:
            raise HttpResponseError(f"Error {status_code}: {message}", status_code)

    # --- Digital Twins ---

    def get_digital_twin(self, digital_twin_id: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Get a digital twin.

        Args:
            digital_twin_id: The ID of the digital twin.
            **kwargs: Additional request options.

        Returns:
            The digital twin data.
        """
        url = f"{self.endpoint}/digitaltwins/{digital_twin_id}"
        response = self._request("GET", url, **kwargs)
        return response.json()

    def upsert_digital_twin(
        self, digital_twin_id: str, digital_twin: Dict[str, Any], **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Create or update a digital twin.

        Args:
            digital_twin_id: The ID of the digital twin.
            digital_twin: The digital twin data to create or update.
            **kwargs: Additional request options.

        Returns:
            The created or updated digital twin data.
        """
        url = f"{self.endpoint}/digitaltwins/{digital_twin_id}"
        response = self._request("PUT", url, json=digital_twin, **kwargs)
        return response.json()

    def update_digital_twin(
        self, digital_twin_id: str, json_patch: List[Dict[str, Any]], **kwargs: Any
    ) -> None:
        """
        Update a digital twin (JSON Patch).

        Args:
            digital_twin_id: The ID of the digital twin.
            json_patch: The JSON patch to apply.
            **kwargs: Additional request options.
        """
        url = f"{self.endpoint}/digitaltwins/{digital_twin_id}"
        # Header for patch? usually application/json-patch+json but ADT accepts application/json too mostly?
        # ADT spec requires Content-Type: application/json-patch+json
        headers = kwargs.pop("headers", {})
        headers["Content-Type"] = "application/json-patch+json"
        self._request("PATCH", url, json=json_patch, headers=headers, **kwargs)

    def delete_digital_twin(self, digital_twin_id: str, **kwargs: Any) -> None:
        """
        Delete a digital twin.

        Args:
            digital_twin_id: The ID of the digital twin.
            **kwargs: Additional request options.
        """
        url = f"{self.endpoint}/digitaltwins/{digital_twin_id}"
        self._request("DELETE", url, **kwargs)

    # --- Components ---

    def get_component(
        self, digital_twin_id: str, component_name: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Get a component.

        Args:
            digital_twin_id: The ID of the digital twin.
            component_name: The name of the component.
            **kwargs: Additional request options.

        Returns:
            The component data.
        """
        url = f"{self.endpoint}/digitaltwins/{digital_twin_id}/components/{component_name}"
        response = self._request("GET", url, **kwargs)
        return response.json()

    def update_component(
        self,
        digital_twin_id: str,
        component_name: str,
        json_patch: List[Dict[str, Any]],
        **kwargs: Any,
    ) -> None:
        """
        Update a component.

        Args:
            digital_twin_id: The ID of the digital twin.
            component_name: The name of the component.
            json_patch: The JSON patch to apply.
            **kwargs: Additional request options.
        """
        url = f"{self.endpoint}/digitaltwins/{digital_twin_id}/components/{component_name}"
        headers = kwargs.pop("headers", {})
        headers["Content-Type"] = "application/json-patch+json"
        self._request("PATCH", url, json=json_patch, headers=headers, **kwargs)

    # --- Relationships ---

    def get_relationship(
        self, digital_twin_id: str, relationship_id: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Get a relationship.

        Args:
            digital_twin_id: The ID of the digital twin.
            relationship_id: The ID of the relationship.
            **kwargs: Additional request options.

        Returns:
            The relationship data.
        """
        url = f"{self.endpoint}/digitaltwins/{digital_twin_id}/relationships/{relationship_id}"
        response = self._request("GET", url, **kwargs)
        return response.json()

    def upsert_relationship(
        self,
        digital_twin_id: str,
        relationship_id: str,
        relationship: Dict[str, Any],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Create or update a relationship.

        Args:
            digital_twin_id: The ID of the digital twin.
            relationship_id: The ID of the relationship.
            relationship: The relationship data.
            **kwargs: Additional request options.

        Returns:
            The created or updated relationship data.
        """
        url = f"{self.endpoint}/digitaltwins/{digital_twin_id}/relationships/{relationship_id}"
        response = self._request("PUT", url, json=relationship, **kwargs)
        return response.json()

    def update_relationship(
        self,
        digital_twin_id: str,
        relationship_id: str,
        json_patch: List[Dict[str, Any]],
        **kwargs: Any,
    ) -> None:
        """
        Update a relationship.

        Args:
            digital_twin_id: The ID of the digital twin.
            relationship_id: The ID of the relationship.
            json_patch: The JSON patch to apply.
            **kwargs: Additional request options.
        """
        url = f"{self.endpoint}/digitaltwins/{digital_twin_id}/relationships/{relationship_id}"
        headers = kwargs.pop("headers", {})
        headers["Content-Type"] = "application/json-patch+json"
        self._request("PATCH", url, json=json_patch, headers=headers, **kwargs)

    def delete_relationship(
        self, digital_twin_id: str, relationship_id: str, **kwargs: Any
    ) -> None:
        """
        Delete a relationship.

        Args:
            digital_twin_id: The ID of the digital twin.
            relationship_id: The ID of the relationship.
            **kwargs: Additional request options.
        """
        url = f"{self.endpoint}/digitaltwins/{digital_twin_id}/relationships/{relationship_id}"
        self._request("DELETE", url, **kwargs)

    def list_relationships(
        self,
        digital_twin_id: str,
        relationship_name: Optional[str] = None,
        **kwargs: Any,
    ) -> PagedIterator:
        """
        List relationships for a digital twin.

        Args:
            digital_twin_id: The ID of the digital twin.
            relationship_name: Optional name of the relationship to filter by.
            **kwargs: Additional request options.

        Returns:
            An iterator over the relationships.
        """
        url = f"{self.endpoint}/digitaltwins/{digital_twin_id}/relationships"
        params = kwargs.pop("params", {})
        if relationship_name:
            params["relationshipName"] = relationship_name

        return PagedIterator(self, url, params=params, **kwargs)

    def list_incoming_relationships(
        self, digital_twin_id: str, **kwargs: Any
    ) -> PagedIterator:
        """
        List incoming relationships for a digital twin.

        Args:
            digital_twin_id: The ID of the digital twin.
            **kwargs: Additional request options.

        Returns:
            An iterator over the incoming relationships.
        """
        url = f"{self.endpoint}/digitaltwins/{digital_twin_id}/incomingrelationships"
        return PagedIterator(self, url, model_cls=IncomingRelationship, **kwargs)

    # --- Query ---

    def query_twins(
        self,
        query_expression: str,
        max_items_per_page: Optional[int] = None,
        **kwargs: Any,
    ) -> PagedIterator:
        """
        Query digital twins.

        Args:
            query_expression: The query expression.
            max_items_per_page: Optional maximum items per page.
            **kwargs: Additional request options.

        Returns:
            An iterator over the query results.
        """
        url = f"{self.endpoint}/query"
        headers = kwargs.pop("headers", {})
        if max_items_per_page:
            headers["max-items-per-page"] = str(max_items_per_page)

        body = {"query": query_expression}

        return PagedIterator(
            self, url, method="POST", json_data=body, headers=headers, **kwargs
        )

    # --- Models ---

    def get_model(
        self, model_id: str, include_model_definition: bool = False, **kwargs: Any
    ) -> DigitalTwinsModelData:
        """
        Get a model.

        Args:
            model_id: The ID of the model.
            include_model_definition: Whether to include the model definition.
            **kwargs: Additional request options.

        Returns:
            The model data.
        """
        url = f"{self.endpoint}/models/{model_id}"
        params = kwargs.pop("params", {})
        params["includeModelDefinition"] = str(include_model_definition).lower()

        response = self._request("GET", url, params=params, **kwargs)
        return DigitalTwinsModelData.from_dict(response.json())

    def list_models(
        self,
        dependencies_for: Optional[Union[str, List[str]]] = None,
        include_model_definition: bool = False,
        results_per_page: Optional[int] = None,
        **kwargs: Any,
    ) -> PagedIterator:
        """
        List models.

        Args:
            dependencies_for: Optional model ID or list of model IDs to get dependencies for.
            include_model_definition: Whether to include the model definition.
            results_per_page: Optional maximum items per page.
            **kwargs: Additional request options.

        Returns:
            An iterator over the models.
        """
        url = f"{self.endpoint}/models"
        params = kwargs.pop("params", {})
        params["includeModelDefinition"] = str(include_model_definition).lower()
        if dependencies_for:
            if isinstance(dependencies_for, list):
                # ADT expects multiple dependenciesFor parameters? or CSV?
                # ADT spec says 'dependenciesFor' can be array, but usually passed as multi-value param?
                # Requests handles list as multi-value params.
                params["dependenciesFor"] = dependencies_for
            else:
                params["dependenciesFor"] = dependencies_for

        headers = kwargs.pop("headers", {})
        if results_per_page:
            headers["max-items-per-page"] = str(results_per_page)

        return PagedIterator(
            self,
            url,
            params=params,
            headers=headers,
            model_cls=DigitalTwinsModelData,
            **kwargs,
        )

    def create_models(
        self, dtdl_models: List[Dict[str, Any]], **kwargs: Any
    ) -> List[DigitalTwinsModelData]:
        """
        Create models.

        Args:
            dtdl_models: A list of DTDL model definitions.
            **kwargs: Additional request options.

        Returns:
            A list of created model data.
        """
        url = f"{self.endpoint}/models"
        response = self._request("POST", url, json=dtdl_models, **kwargs)
        return [DigitalTwinsModelData.from_dict(m) for m in response.json()]

    def decommission_model(self, model_id: str, **kwargs: Any) -> None:
        """
        Decommission a model.

        Args:
            model_id: The ID of the model.
            **kwargs: Additional request options.
        """
        url = f"{self.endpoint}/models/{model_id}"
        json_patch = [{"op": "replace", "path": "/decommissioned", "value": True}]
        headers = kwargs.pop("headers", {})
        headers["Content-Type"] = "application/json-patch+json"

        self._request("PATCH", url, json=json_patch, headers=headers, **kwargs)

    def delete_model(self, model_id: str, **kwargs: Any) -> None:
        """
        Delete a model.

        Args:
            model_id: The ID of the model.
            **kwargs: Additional request options.
        """
        url = f"{self.endpoint}/models/{model_id}"
        self._request("DELETE", url, **kwargs)

    def search_models(
        self,
        search_text: str,
        limit: int = 10,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        Search for DTDL models using semantic and keyword search.

        Args:
            search_text: Search query (uses hybrid vector + keyword search).
            limit: Maximum number of results to return. Defaults to 10.
            **kwargs: Additional request options.

        Returns:
            A list of matching model summaries.
        """
        url = f"{self.endpoint}/models/search"
        body = {"searchText": search_text, "limit": limit}
        response = self._request("POST", url, json=body, **kwargs)
        return response.json()

    def search_twins(
        self,
        search_text: str,
        model_id: Optional[str] = None,
        limit: int = 10,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        Search for digital twins using semantic and keyword search.

        Args:
            search_text: Search query.
            model_id: Optional filter by model ID.
            limit: Maximum number of results to return. Defaults to 10.
            **kwargs: Additional request options.

        Returns:
            A list of matching digital twins.
        """
        url = f"{self.endpoint}/digitaltwins/search"
        body = {"searchText": search_text, "limit": limit}
        if model_id:
            body["modelId"] = model_id
        response = self._request("POST", url, json=body, **kwargs)
        return response.json()

    # --- Telemetry ---

    def publish_telemetry(
        self,
        digital_twin_id: str,
        telemetry: Dict[str, Any],
        message_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Publish telemetry for a digital twin.

        Args:
            digital_twin_id: The ID of the digital twin.
            telemetry: The telemetry data.
            message_id: Optional unique identifier for the telemetry message.
            **kwargs: Additional request options.
        """
        url = f"{self.endpoint}/digitaltwins/{digital_twin_id}/telemetry"
        headers = kwargs.pop("headers", {})
        if message_id:
            headers["Message-Id"] = message_id

        self._request("POST", url, json=telemetry, headers=headers, **kwargs)

    def publish_component_telemetry(
        self,
        digital_twin_id: str,
        component_name: str,
        telemetry: Dict[str, Any],
        message_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Publish telemetry for a component.

        Args:
            digital_twin_id: The ID of the digital twin.
            component_name: The name of the component.
            telemetry: The telemetry data.
            message_id: Optional unique identifier for the telemetry message.
            **kwargs: Additional request options.
        """
        url = f"{self.endpoint}/digitaltwins/{digital_twin_id}/components/{component_name}/telemetry"
        headers = kwargs.pop("headers", {})
        if message_id:
            headers["Message-Id"] = message_id

        self._request("POST", url, json=telemetry, headers=headers, **kwargs)

    # --- Import Jobs ---

    def list_import_jobs(self, **kwargs: Any) -> PagedIterator:
        """
        List import jobs.

        Args:
            **kwargs: Additional request options.

        Returns:
            An iterator over the import jobs.
        """
        url = f"{self.endpoint}/jobs/import"
        return PagedIterator(self, url, model_cls=ImportJob, **kwargs)

    def get_import_job(self, job_id: str, **kwargs: Any) -> ImportJob:
        """
        Get an import job.

        Args:
            job_id: The ID of the job.
            **kwargs: Additional request options.

        Returns:
            The import job data.
        """
        url = f"{self.endpoint}/jobs/import/{job_id}"
        response = self._request("GET", url, **kwargs)
        return ImportJob.from_dict(response.json())

    def create_import_job(
        self, job_id: str, import_job: Dict[str, Any], **kwargs: Any
    ) -> ImportJob:
        """
        Create an import job.

        Args:
            job_id: The ID of the job.
            import_job: The import job data.
            **kwargs: Additional request options.

        Returns:
            The created import job data.
        """
        url = f"{self.endpoint}/jobs/import/{job_id}"
        response = self._request("PUT", url, json=import_job, **kwargs)
        return ImportJob.from_dict(response.json())

    def delete_import_job(self, job_id: str, **kwargs: Any) -> None:
        """
        Delete an import job.

        Args:
            job_id: The ID of the job.
            **kwargs: Additional request options.
        """
        url = f"{self.endpoint}/jobs/import/{job_id}"
        self._request("DELETE", url, **kwargs)

    def cancel_import_job(self, job_id: str, **kwargs: Any) -> ImportJob:
        """
        Cancel an import job.

        Args:
            job_id: The ID of the job.
            **kwargs: Additional request options.

        Returns:
            The cancelled import job data.
        """
        url = f"{self.endpoint}/jobs/import/{job_id}"
        response = self._request("POST", url, **kwargs)
        return ImportJob.from_dict(response.json())

    # --- Delete Jobs ---

    def list_delete_jobs(self, **kwargs: Any) -> PagedIterator:
        """
        List delete jobs.

        Args:
            **kwargs: Additional request options.

        Returns:
            An iterator over the delete jobs.
        """
        url = f"{self.endpoint}/jobs/deletion"
        return PagedIterator(self, url, model_cls=DeleteJob, **kwargs)

    def get_delete_job(self, job_id: str, **kwargs: Any) -> DeleteJob:
        """
        Get a delete job.

        Args:
            job_id: The ID of the job.
            **kwargs: Additional request options.

        Returns:
            The delete job data.
        """
        url = f"{self.endpoint}/jobs/deletion/{job_id}"
        response = self._request("GET", url, **kwargs)
        return DeleteJob.from_dict(response.json())

    def create_delete_job(
        self, job_id: str, delete_job: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> DeleteJob:
        """
        Create a delete job.

        Args:
            job_id: The ID of the job.
            delete_job: Optional delete job options.
            **kwargs: Additional request options.

        Returns:
            The created delete job data.
        """
        url = f"{self.endpoint}/jobs/deletion/{job_id}"
        # Delete job creation might have an empty body or specific options?
        # ADT usually takes an empty body or optional params
        response = self._request("PUT", url, json=delete_job or {}, **kwargs)
        return DeleteJob.from_dict(response.json())
