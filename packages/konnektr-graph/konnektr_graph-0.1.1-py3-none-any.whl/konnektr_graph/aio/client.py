# konnektr_graph/aio/client.py
"""
Konnektr Graph SDK (Azure-free) - Asynchronous Client
"""
import json
from typing import Any, Dict, List, Mapping, Optional, Union, AsyncIterator

import aiohttp

from ..auth.protocol import AsyncTokenProvider, TokenProvider
from ..exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
    ResourceExistsError,
    AuthenticationError,
)
from ..models import (
    DeleteJob,
    DigitalTwinsModelData,
    ImportJob,
    IncomingRelationship,
    PagedResult,
)


class AsyncPagedIterator(AsyncIterator):
    """
    Async iterator for handling paged responses.
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

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self._first_page_fetched:
            await self._fetch_page(is_initial=True)
            self._first_page_fetched = True

        if self._current_page_index < len(self._current_page_items):
            item = self._current_page_items[self._current_page_index]
            self._current_page_index += 1
            return item
        else:
            if not self._next_link and not self._continuation_token:
                raise StopAsyncIteration
            await self._fetch_page()
            if not self._current_page_items:
                raise StopAsyncIteration
            self._current_page_index = 1
            return self._current_page_items[0]

    async def _fetch_page(self, is_initial: bool = False):
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

        # Use a low-level _request_raw to get the full response object for headers
        # Wait, I need headers. Let's modify _request to return (data, headers) or similar?
        # Or just handle it in _request.
        data, resp_headers = await self._client._request_raw(
            self._method,
            request_url,
            headers=headers,
            json=self._json_data,
            params=params,
        )

        # Check for continuation token in headers
        token = resp_headers.get("x-ms-continuation")
        self._continuation_token = token if token else None

        # Check for nextLink in body
        self._next_link = data.get("nextLink")

        # If continuationToken is in body
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
    def __init__(
        self, endpoint: str, credential: Union[AsyncTokenProvider, TokenProvider]
    ):
        """
        :param endpoint: API endpoint (e.g. https://graph.konnektr.io)
        :param credential: AsyncTokenProvider credential
        """
        if not endpoint.startswith("http"):
            endpoint = "https://" + endpoint
        self.endpoint = endpoint.rstrip("/")
        self.credential = credential
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()

    async def close(self):
        """Close the client session."""
        if self._session:
            await self._session.close()
            self._session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _request(
        self, method: str, url: str, headers: Optional[Dict[str, str]] = None, **kwargs
    ) -> Dict[str, Any]:
        data, _ = await self._request_raw(method, url, headers=headers, **kwargs)
        return data

    async def _request_raw(
        self, method: str, url: str, headers: Optional[Dict[str, str]] = None, **kwargs
    ) -> tuple[Dict[str, Any], Mapping[str, str]]:
        session = await self._get_session()

        if headers is None:
            headers = {}

        # Handle async or sync credential
        if hasattr(self.credential, "get_headers"):
            auth_headers = self.credential.get_headers()
            if hasattr(auth_headers, "__await__"):  # Check if awaitable
                auth_headers = await auth_headers
            headers.update(auth_headers)

        # Ensure content type is set
        if "json" in kwargs and "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        async with session.request(method, url, headers=headers, **kwargs) as response:
            if not response.ok:
                await self._handle_error(response)

            # For 204 No Content, return empty dict
            if response.status == 204:
                return {}, response.headers
            try:
                data = await response.json()
                return data, response.headers
            except Exception:
                return {}, response.headers

    async def _handle_error(self, response: aiohttp.ClientResponse):
        try:
            error_data = await response.json()
            message = json.dumps(error_data)
        except Exception:
            text = await response.text()
            message = text

        status_code = response.status
        if status_code == 404:
            raise ResourceNotFoundError(message, status_code)
        elif status_code == 409:
            raise ResourceExistsError(message, status_code)
        elif status_code in (401, 403):
            raise AuthenticationError(message, status_code)
        else:
            raise HttpResponseError(f"Error {status_code}: {message}", status_code)

    # --- Digital Twins ---

    async def get_digital_twin(
        self, digital_twin_id: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """Get a digital twin."""
        url = f"{self.endpoint}/digitaltwins/{digital_twin_id}"
        return await self._request("GET", url, **kwargs)

    async def upsert_digital_twin(
        self, digital_twin_id: str, digital_twin: Dict[str, Any], **kwargs: Any
    ) -> Dict[str, Any]:
        """Create or update a digital twin."""
        url = f"{self.endpoint}/digitaltwins/{digital_twin_id}"
        return await self._request("PUT", url, json=digital_twin, **kwargs)

    async def update_digital_twin(
        self, digital_twin_id: str, json_patch: List[Dict[str, Any]], **kwargs: Any
    ) -> None:
        """Update a digital twin (JSON Patch)."""
        url = f"{self.endpoint}/digitaltwins/{digital_twin_id}"
        headers = kwargs.pop("headers", {})
        headers["Content-Type"] = "application/json-patch+json"
        await self._request("PATCH", url, json=json_patch, headers=headers, **kwargs)

    async def delete_digital_twin(self, digital_twin_id: str, **kwargs: Any) -> None:
        """Delete a digital twin."""
        url = f"{self.endpoint}/digitaltwins/{digital_twin_id}"
        await self._request("DELETE", url, **kwargs)

    # --- Components ---

    async def get_component(
        self, digital_twin_id: str, component_name: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """Get a component."""
        url = f"{self.endpoint}/digitaltwins/{digital_twin_id}/components/{component_name}"
        return await self._request("GET", url, **kwargs)

    async def update_component(
        self,
        digital_twin_id: str,
        component_name: str,
        json_patch: List[Dict[str, Any]],
        **kwargs: Any,
    ) -> None:
        """Update a component."""
        url = f"{self.endpoint}/digitaltwins/{digital_twin_id}/components/{component_name}"
        headers = kwargs.pop("headers", {})
        headers["Content-Type"] = "application/json-patch+json"
        await self._request("PATCH", url, json=json_patch, headers=headers, **kwargs)

    # --- Relationships ---

    async def get_relationship(
        self, digital_twin_id: str, relationship_id: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """Get a relationship."""
        url = f"{self.endpoint}/digitaltwins/{digital_twin_id}/relationships/{relationship_id}"
        return await self._request("GET", url, **kwargs)

    async def upsert_relationship(
        self,
        digital_twin_id: str,
        relationship_id: str,
        relationship: Dict[str, Any],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Create or update a relationship."""
        url = f"{self.endpoint}/digitaltwins/{digital_twin_id}/relationships/{relationship_id}"
        return await self._request("PUT", url, json=relationship, **kwargs)

    async def update_relationship(
        self,
        digital_twin_id: str,
        relationship_id: str,
        json_patch: List[Dict[str, Any]],
        **kwargs: Any,
    ) -> None:
        """Update a relationship."""
        url = f"{self.endpoint}/digitaltwins/{digital_twin_id}/relationships/{relationship_id}"
        headers = kwargs.pop("headers", {})
        headers["Content-Type"] = "application/json-patch+json"
        await self._request("PATCH", url, json=json_patch, headers=headers, **kwargs)

    async def delete_relationship(
        self, digital_twin_id: str, relationship_id: str, **kwargs: Any
    ) -> None:
        """Delete a relationship."""
        url = f"{self.endpoint}/digitaltwins/{digital_twin_id}/relationships/{relationship_id}"
        await self._request("DELETE", url, **kwargs)

    def list_relationships(
        self,
        digital_twin_id: str,
        relationship_name: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncPagedIterator:
        """List relationships."""
        url = f"{self.endpoint}/digitaltwins/{digital_twin_id}/relationships"
        params = kwargs.pop("params", {})
        if relationship_name:
            params["relationshipName"] = relationship_name

        return AsyncPagedIterator(self, url, params=params, **kwargs)

    def list_incoming_relationships(
        self, digital_twin_id: str, **kwargs: Any
    ) -> AsyncPagedIterator:
        """List incoming relationships."""
        url = f"{self.endpoint}/digitaltwins/{digital_twin_id}/incomingrelationships"
        return AsyncPagedIterator(self, url, model_cls=IncomingRelationship, **kwargs)

    # --- Query ---

    def query_twins(
        self,
        query_expression: str,
        max_items_per_page: Optional[int] = None,
        **kwargs: Any,
    ) -> AsyncPagedIterator:
        """Query digital twins."""
        url = f"{self.endpoint}/query"
        headers = kwargs.pop("headers", {})
        if max_items_per_page:
            headers["max-items-per-page"] = str(max_items_per_page)

        body = {"query": query_expression}

        return AsyncPagedIterator(
            self, url, method="POST", json_data=body, headers=headers, **kwargs
        )

    # --- Models ---

    async def get_model(
        self, model_id: str, include_model_definition: bool = False, **kwargs: Any
    ) -> DigitalTwinsModelData:
        """Get a model."""
        url = f"{self.endpoint}/models/{model_id}"
        params = kwargs.pop("params", {})
        params["includeModelDefinition"] = str(include_model_definition).lower()

        data = await self._request("GET", url, params=params, **kwargs)
        return DigitalTwinsModelData.from_dict(data)

    def list_models(
        self,
        dependencies_for: Optional[Union[str, List[str]]] = None,
        include_model_definition: bool = False,
        results_per_page: Optional[int] = None,
        **kwargs: Any,
    ) -> AsyncPagedIterator:
        """List models."""
        url = f"{self.endpoint}/models"
        params = kwargs.pop("params", {})
        params["includeModelDefinition"] = str(include_model_definition).lower()
        if dependencies_for:
            params["dependenciesFor"] = dependencies_for

        headers = kwargs.pop("headers", {})
        if results_per_page:
            headers["max-items-per-page"] = str(results_per_page)

        return AsyncPagedIterator(
            self,
            url,
            params=params,
            headers=headers,
            model_cls=DigitalTwinsModelData,
            **kwargs,
        )

    async def create_models(
        self, dtdl_models: List[Dict[str, Any]], **kwargs: Any
    ) -> List[DigitalTwinsModelData]:
        """Create models."""
        url = f"{self.endpoint}/models"
        data = await self._request("POST", url, json=dtdl_models, **kwargs)
        return [DigitalTwinsModelData.from_dict(m) for m in data]

    async def decommission_model(self, model_id: str, **kwargs: Any) -> None:
        """Decommission a model."""
        url = f"{self.endpoint}/models/{model_id}"
        json_patch = [{"op": "replace", "path": "/decommissioned", "value": True}]
        headers = kwargs.pop("headers", {})
        headers["Content-Type"] = "application/json-patch+json"

        await self._request("PATCH", url, json=json_patch, headers=headers, **kwargs)

    async def delete_model(self, model_id: str, **kwargs: Any) -> None:
        """Delete a model."""
        url = f"{self.endpoint}/models/{model_id}"
        await self._request("DELETE", url, **kwargs)

    # --- Telemetry ---

    async def publish_telemetry(
        self,
        digital_twin_id: str,
        telemetry: Dict[str, Any],
        message_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Publish telemetry."""
        url = f"{self.endpoint}/digitaltwins/{digital_twin_id}/telemetry"
        headers = kwargs.pop("headers", {})
        if message_id:
            headers["Message-Id"] = message_id

        await self._request("POST", url, json=telemetry, headers=headers, **kwargs)

    async def publish_component_telemetry(
        self,
        digital_twin_id: str,
        component_name: str,
        telemetry: Dict[str, Any],
        message_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Publish component telemetry."""
        url = f"{self.endpoint}/digitaltwins/{digital_twin_id}/components/{component_name}/telemetry"
        headers = kwargs.pop("headers", {})
        if message_id:
            headers["Message-Id"] = message_id

        await self._request("POST", url, json=telemetry, headers=headers, **kwargs)

    # --- Import Jobs ---

    def list_import_jobs(self, **kwargs: Any) -> AsyncPagedIterator:
        """List import jobs."""
        url = f"{self.endpoint}/jobs/import"
        return AsyncPagedIterator(self, url, model_cls=ImportJob, **kwargs)

    async def get_import_job(self, job_id: str, **kwargs: Any) -> ImportJob:
        """Get an import job."""
        url = f"{self.endpoint}/jobs/import/{job_id}"
        data = await self._request("GET", url, **kwargs)
        return ImportJob.from_dict(data)

    async def create_import_job(
        self, job_id: str, import_job: Dict[str, Any], **kwargs: Any
    ) -> ImportJob:
        """Create an import job."""
        url = f"{self.endpoint}/jobs/import/{job_id}"
        data = await self._request("PUT", url, json=import_job, **kwargs)
        return ImportJob.from_dict(data)

    async def delete_import_job(self, job_id: str, **kwargs: Any) -> None:
        """Delete an import job."""
        url = f"{self.endpoint}/jobs/import/{job_id}"
        await self._request("DELETE", url, **kwargs)

    async def cancel_import_job(self, job_id: str, **kwargs: Any) -> ImportJob:
        """Cancel an import job."""
        url = f"{self.endpoint}/jobs/import/{job_id}"
        data = await self._request("POST", url, **kwargs)
        return ImportJob.from_dict(data)

    # --- Delete Jobs ---

    def list_delete_jobs(self, **kwargs: Any) -> AsyncPagedIterator:
        """List delete jobs."""
        url = f"{self.endpoint}/jobs/deletion"
        return AsyncPagedIterator(self, url, model_cls=DeleteJob, **kwargs)

    async def get_delete_job(self, job_id: str, **kwargs: Any) -> DeleteJob:
        """Get a delete job."""
        url = f"{self.endpoint}/jobs/deletion/{job_id}"
        data = await self._request("GET", url, **kwargs)
        return DeleteJob.from_dict(data)

    async def create_delete_job(
        self, job_id: str, delete_job: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> DeleteJob:
        """Create a delete job."""
        url = f"{self.endpoint}/jobs/deletion/{job_id}"
        data = await self._request("PUT", url, json=delete_job or {}, **kwargs)
        return DeleteJob.from_dict(data)
