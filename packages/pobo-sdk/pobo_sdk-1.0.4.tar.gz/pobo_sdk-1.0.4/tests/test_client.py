"""Tests for PoboClient."""

import pytest
import responses

from pobo import PoboClient, Product, Blog, LocalizedString, ValidationError, ApiError


class TestPoboClient:
    @pytest.fixture
    def client(self):
        return PoboClient(api_token="test-token")

    @responses.activate
    def test_import_products(self, client):
        responses.add(
            responses.POST,
            "https://api.pobo.space/api/v2/rest/products",
            json={"success": True, "imported": 1, "updated": 0, "skipped": 0, "errors": []},
            status=200,
        )

        product = Product(
            id="PROD-001",
            is_visible=True,
            name=LocalizedString.create("Product"),
            url=LocalizedString.create("https://example.com"),
        )

        result = client.import_products([product])

        assert result.success is True
        assert result.imported == 1

    def test_import_products_empty_payload(self, client):
        with pytest.raises(ValidationError, match="Payload cannot be empty"):
            client.import_products([])

    def test_import_products_too_many_items(self, client):
        products = [
            {"id": f"PROD-{i}", "is_visible": True, "name": {"default": f"Product {i}"}, "url": {"default": "https://example.com"}}
            for i in range(101)
        ]

        with pytest.raises(ValidationError, match="Too many items"):
            client.import_products(products)

    @responses.activate
    def test_get_products(self, client):
        responses.add(
            responses.GET,
            "https://api.pobo.space/api/v2/rest/products",
            json={
                "data": [
                    {"id": "PROD-001", "is_visible": True, "name": {"default": "Product"}, "url": {"default": "https://example.com"}}
                ],
                "meta": {"current_page": 1, "per_page": 50, "total": 1},
            },
            status=200,
        )

        response = client.get_products(page=1, per_page=50)

        assert len(response.data) == 1
        assert response.data[0].id == "PROD-001"
        assert response.current_page == 1
        assert response.total == 1

    @responses.activate
    def test_import_blogs(self, client):
        responses.add(
            responses.POST,
            "https://api.pobo.space/api/v2/rest/blogs",
            json={"success": True, "imported": 1, "updated": 0, "skipped": 0, "errors": []},
            status=200,
        )

        blog = Blog(
            id="BLOG-001",
            is_visible=True,
            name=LocalizedString.create("Blog"),
            url=LocalizedString.create("https://example.com/blog"),
            category="news",
        )

        result = client.import_blogs([blog])

        assert result.success is True
        assert result.imported == 1

    @responses.activate
    def test_unauthorized_error(self, client):
        responses.add(
            responses.GET,
            "https://api.pobo.space/api/v2/rest/products",
            json={"error": "Unauthorized"},
            status=401,
        )

        with pytest.raises(ApiError, match="Authorization token required"):
            client.get_products()

    @responses.activate
    def test_server_error(self, client):
        responses.add(
            responses.GET,
            "https://api.pobo.space/api/v2/rest/products",
            json={"error": "Server error"},
            status=500,
        )

        with pytest.raises(ApiError, match="Server error"):
            client.get_products()
