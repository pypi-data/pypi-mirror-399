"""Pobo API client."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterator, List, Optional, Type, TypeVar, Union

import requests

from pobo.dto.blog import Blog
from pobo.dto.category import Category
from pobo.dto.import_result import ImportResult
from pobo.dto.paginated_response import PaginatedResponse
from pobo.dto.parameter import Parameter
from pobo.dto.product import Product
from pobo.exceptions import ApiError, ValidationError

T = TypeVar("T", Product, Category, Blog)

DEFAULT_BASE_URL = "https://api.pobo.space"
MAX_BULK_ITEMS = 100
DEFAULT_TIMEOUT = 30


class PoboClient:
    """Client for Pobo API V2."""

    def __init__(
        self,
        api_token: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        self.api_token = api_token
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {api_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        })

    # Import methods

    def import_products(self, products: List[Union[Product, Dict[str, Any]]]) -> ImportResult:
        """Bulk import products. Maximum 100 items per request."""
        self._validate_bulk_size(products)
        payload = [p.to_api_dict() if isinstance(p, Product) else p for p in products]
        response = self._request("POST", "/api/v2/rest/products", payload)
        return ImportResult.model_validate(response)

    def import_categories(self, categories: List[Union[Category, Dict[str, Any]]]) -> ImportResult:
        """Bulk import categories. Maximum 100 items per request."""
        self._validate_bulk_size(categories)
        payload = [c.to_api_dict() if isinstance(c, Category) else c for c in categories]
        response = self._request("POST", "/api/v2/rest/categories", payload)
        return ImportResult.model_validate(response)

    def import_parameters(self, parameters: List[Union[Parameter, Dict[str, Any]]]) -> ImportResult:
        """Bulk import parameters. Maximum 100 items per request."""
        self._validate_bulk_size(parameters)
        payload = [p.to_api_dict() if isinstance(p, Parameter) else p for p in parameters]
        response = self._request("POST", "/api/v2/rest/parameters", payload)
        return ImportResult.model_validate(response)

    def import_blogs(self, blogs: List[Union[Blog, Dict[str, Any]]]) -> ImportResult:
        """Bulk import blogs. Maximum 100 items per request."""
        self._validate_bulk_size(blogs)
        payload = [b.to_api_dict() if isinstance(b, Blog) else b for b in blogs]
        response = self._request("POST", "/api/v2/rest/blogs", payload)
        return ImportResult.model_validate(response)

    # Export methods

    def get_products(
        self,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        last_update_from: Optional[datetime] = None,
        is_edited: Optional[bool] = None,
    ) -> PaginatedResponse[Product]:
        """Get paginated list of products."""
        params = self._build_query_params(page, per_page, last_update_from, is_edited)
        response = self._request("GET", "/api/v2/rest/products", params=params)
        return self._parse_paginated_response(response, Product)

    def get_categories(
        self,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        last_update_from: Optional[datetime] = None,
        is_edited: Optional[bool] = None,
    ) -> PaginatedResponse[Category]:
        """Get paginated list of categories."""
        params = self._build_query_params(page, per_page, last_update_from, is_edited)
        response = self._request("GET", "/api/v2/rest/categories", params=params)
        return self._parse_paginated_response(response, Category)

    def get_blogs(
        self,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        last_update_from: Optional[datetime] = None,
        is_edited: Optional[bool] = None,
    ) -> PaginatedResponse[Blog]:
        """Get paginated list of blogs."""
        params = self._build_query_params(page, per_page, last_update_from, is_edited)
        response = self._request("GET", "/api/v2/rest/blogs", params=params)
        return self._parse_paginated_response(response, Blog)

    # Iterator methods

    def iter_products(
        self,
        last_update_from: Optional[datetime] = None,
        is_edited: Optional[bool] = None,
    ) -> Iterator[Product]:
        """Iterate through all products, handling pagination automatically."""
        yield from self._iterate(self.get_products, last_update_from, is_edited)

    def iter_categories(
        self,
        last_update_from: Optional[datetime] = None,
        is_edited: Optional[bool] = None,
    ) -> Iterator[Category]:
        """Iterate through all categories, handling pagination automatically."""
        yield from self._iterate(self.get_categories, last_update_from, is_edited)

    def iter_blogs(
        self,
        last_update_from: Optional[datetime] = None,
        is_edited: Optional[bool] = None,
    ) -> Iterator[Blog]:
        """Iterate through all blogs, handling pagination automatically."""
        yield from self._iterate(self.get_blogs, last_update_from, is_edited)

    # Private methods

    def _iterate(
        self,
        get_method: Any,
        last_update_from: Optional[datetime],
        is_edited: Optional[bool],
    ) -> Iterator[Any]:
        """Generic iterator for paginated responses."""
        page = 1
        while True:
            response = get_method(
                page=page,
                per_page=MAX_BULK_ITEMS,
                last_update_from=last_update_from,
                is_edited=is_edited,
            )
            yield from response.data
            if not response.has_more_pages():
                break
            page += 1

    def _validate_bulk_size(self, items: List[Any]) -> None:
        """Validate bulk import size."""
        if not items:
            raise ValidationError.empty_payload()
        if len(items) > MAX_BULK_ITEMS:
            raise ValidationError.too_many_items(len(items), MAX_BULK_ITEMS)

    def _build_query_params(
        self,
        page: Optional[int],
        per_page: Optional[int],
        last_update_from: Optional[datetime],
        is_edited: Optional[bool],
    ) -> Dict[str, Any]:
        """Build query parameters for GET requests."""
        params: Dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = min(per_page, MAX_BULK_ITEMS)
        if last_update_from is not None:
            params["last_update_time_from"] = last_update_from.strftime("%Y-%m-%d %H:%M:%S")
        if is_edited is not None:
            params["is_edited"] = "true" if is_edited else "false"
        return params

    def _parse_paginated_response(
        self,
        response: Dict[str, Any],
        item_class: Type[T],
    ) -> PaginatedResponse[T]:
        """Parse paginated response into typed objects."""
        data = [item_class.model_validate(item) for item in response.get("data", [])]
        meta = response.get("meta", {})
        return PaginatedResponse(
            data=data,
            current_page=meta.get("current_page", 1),
            per_page=meta.get("per_page", 100),
            total=meta.get("total", 0),
        )

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Any = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request to the API."""
        url = f"{self.base_url}{endpoint}"

        try:
            response = self._session.request(
                method=method,
                url=url,
                json=data if method == "POST" else None,
                params=params,
                timeout=self.timeout,
            )
        except requests.RequestException as e:
            raise ApiError(f"Request failed: {e}")

        return self._handle_response(response)

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response."""
        try:
            body = response.json() if response.text else {}
        except ValueError:
            body = {}

        if response.status_code == 401:
            raise ApiError.unauthorized()
        if response.status_code >= 400:
            raise ApiError.from_response(response.status_code, body)

        return body
