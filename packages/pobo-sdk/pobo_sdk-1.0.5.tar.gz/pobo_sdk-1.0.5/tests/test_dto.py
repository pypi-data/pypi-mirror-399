"""Tests for DTO classes."""

import pytest

from pobo import LocalizedString, Language, Blog, Product, Category


class TestLocalizedString:
    def test_create_with_default(self):
        string = LocalizedString.create("Default")
        assert string.default == "Default"

    def test_with_translation(self):
        string = LocalizedString.create("Default")
        string_with_cs = string.with_translation(Language.CS, "Czech")

        assert string.get(Language.CS) is None
        assert string_with_cs.get(Language.CS) == "Czech"
        assert string_with_cs.default == "Default"

    def test_to_dict(self):
        string = LocalizedString.create("Default").with_translation(Language.CS, "Czech")
        result = string.to_dict()

        assert result == {"default": "Default", "cs": "Czech"}


class TestBlog:
    def test_from_dict(self):
        data = {
            "id": "BLOG-001",
            "is_visible": True,
            "category": "news",
            "name": {"default": "Blog Title", "cs": "Název blogu"},
            "url": {"default": "https://example.com/blog"},
            "is_loaded": False,
        }

        blog = Blog.model_validate(data)

        assert blog.id == "BLOG-001"
        assert blog.is_visible is True
        assert blog.category == "news"
        assert blog.name.default == "Blog Title"
        assert blog.name.get(Language.CS) == "Název blogu"
        assert blog.is_loaded is False

    def test_to_api_dict(self):
        blog = Blog(
            id="BLOG-001",
            is_visible=True,
            name=LocalizedString.create("Blog Title"),
            url=LocalizedString.create("https://example.com/blog"),
            category="news",
        )

        data = blog.to_api_dict()

        assert data["id"] == "BLOG-001"
        assert data["is_visible"] is True
        assert data["category"] == "news"
        assert data["name"] == {"default": "Blog Title"}

    def test_optional_fields_excluded(self):
        blog = Blog(
            id="BLOG-001",
            is_visible=True,
            name=LocalizedString.create("Blog"),
            url=LocalizedString.create("https://example.com"),
        )

        data = blog.to_api_dict()

        assert "category" not in data
        assert "description" not in data
        assert "images" not in data


class TestProduct:
    def test_from_dict(self):
        data = {
            "id": "PROD-001",
            "is_visible": True,
            "name": {"default": "Product"},
            "url": {"default": "https://example.com/product"},
            "categories_ids": ["CAT-001", "CAT-002"],
            "parameters_ids": [1, 2],
        }

        product = Product.model_validate(data)

        assert product.id == "PROD-001"
        assert product.categories_ids == ["CAT-001", "CAT-002"]
        assert product.parameters_ids == [1, 2]


class TestCategory:
    def test_from_dict(self):
        data = {
            "id": "CAT-001",
            "is_visible": True,
            "name": {"default": "Category"},
            "url": {"default": "https://example.com/category"},
            "guid": "550e8400-e29b-41d4-a716-446655440000",
        }

        category = Category.model_validate(data)

        assert category.id == "CAT-001"
        assert category.guid == "550e8400-e29b-41d4-a716-446655440000"
