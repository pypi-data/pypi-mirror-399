import unittest

from nextcloud_cookbook_api.models import Keyword


class TestKeywordModel(unittest.TestCase):
    def test_serialization(self) -> None:
        k = Keyword.model_construct(name="Test Keyword", recipe_count=42)
        json = {"name": "Test Keyword", "recipe_count": 42}
        assert json == k.model_dump(mode="json", by_alias=True)

    def test_deserialization(self) -> None:
        json = {"name": "Test Keyword", "recipe_count": 42}
        k = Keyword.model_validate(json)
        assert k.name == "Test Keyword"
        assert k.recipe_count == 42


if __name__ == "__main__":
    unittest.main()
