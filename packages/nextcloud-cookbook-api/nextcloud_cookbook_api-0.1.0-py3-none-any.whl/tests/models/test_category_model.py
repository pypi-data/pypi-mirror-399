import unittest

from nextcloud_cookbook_api.models import Category


class TestCategoryModel(unittest.TestCase):
    def test_serialization(self) -> None:
        c = Category.model_construct(name="Test Category", recipe_count=42)
        json = {"name": "Test Category", "recipe_count": 42}
        assert json == c.model_dump(mode="json", by_alias=True)

    def test_deserialization(self) -> None:
        json = {"name": "Test Category", "recipe_count": 42}
        c = Category.model_validate(json)
        assert c.name == "Test Category"
        assert c.recipe_count == 42


if __name__ == "__main__":
    unittest.main()
