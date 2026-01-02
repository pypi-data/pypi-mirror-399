import unittest

from nextcloud_cookbook_api.models.config import VisibleInfoBlocks


class TestVisibleInfoBlocksModel(unittest.TestCase):
    def test_serialization(self) -> None:
        v = VisibleInfoBlocks.model_construct(
            preparation_time=True,
            cooking_time=False,
            total_time=True,
            nutrition_information=False,
            tools=True,
        )
        json = {
            "preparation-time": True,
            "cooking-time": False,
            "total-time": True,
            "nutrition-information": False,
            "tools": True,
        }
        assert json == v.model_dump(mode="json", by_alias=True)

    def test_deserialization(self) -> None:
        json = {
            "preparation-time": True,
            "cooking-time": False,
            "total-time": True,
            "nutrition-information": False,
            "tools": True,
        }
        v = VisibleInfoBlocks.model_validate(json)
        assert v.preparation_time
        assert not v.cooking_time
        assert v.total_time
        assert not v.nutrition_information
        assert v.tools


if __name__ == "__main__":
    unittest.main()
