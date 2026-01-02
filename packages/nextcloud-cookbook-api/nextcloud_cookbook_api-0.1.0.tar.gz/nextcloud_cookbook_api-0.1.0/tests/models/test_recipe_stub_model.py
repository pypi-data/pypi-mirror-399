import unittest
from datetime import datetime

from pydantic_core import TzInfo

from nextcloud_cookbook_api.models import RecipeStub


class TestRecipeModel(unittest.TestCase):
    def test_serialization(self) -> None:
        r = RecipeStub.model_construct(
            id=1,
            name="Test Recipe",
            keywords=["test", "recipe"],
            date_created="2021-01-01T00:00:00+00:00",
            date_modified="2021-01-01T00:00:00+00:00",
            image_url="https://example.com/image.jpg",
            image_placeholder_url="https://example.com/placeholder.jpg",
        )
        json = {
            "id": 1,
            "name": "Test Recipe",
            "keywords": "test,recipe",
            "dateCreated": "2021-01-01T00:00:00+00:00",
            "dateModified": "2021-01-01T00:00:00+00:00",
            "imageUrl": "https://example.com/image.jpg",
            "imagePlaceholderUrl": "https://example.com/placeholder.jpg",
        }
        assert json == r.model_dump(mode="json", by_alias=True)

    def test_deserialization(self) -> None:
        json = {
            "id": "1",
            "name": "Test Recipe",
            "keywords": "test,recipe",
            "dateCreated": "2021-01-01T00:00:00+00:00",
            "dateModified": "2021-01-02T00:00:00+00:00",
            "imageUrl": "https://example.com/image.jpg",
            "imagePlaceholderUrl": "https://example.com/placeholder.jpg",
        }
        v = RecipeStub.model_validate(json)
        assert v.id == "1"
        assert v.name == "Test Recipe"
        assert v.keywords == ["test", "recipe"]
        assert datetime(2021, 1, 1, 0, 0, tzinfo=TzInfo(0)) == v.date_created
        assert datetime(2021, 1, 2, 0, 0, tzinfo=TzInfo(0)) == v.date_modified
        assert v.image_url == "https://example.com/image.jpg"
        assert v.image_placeholder_url == "https://example.com/placeholder.jpg"


if __name__ == "__main__":
    unittest.main()
