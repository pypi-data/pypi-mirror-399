import unittest

from nextcloud_cookbook_api.models import Config


class TestConfigModel(unittest.TestCase):
    def test_serialization(self) -> None:
        c = Config.model_construct(
            folder="Test1",
            update_interval=42,
            print_image=True,
            visible_info_blocks={
                "preparation-time": True,
                "cooking-time": False,
                "total-time": True,
                "nutrition-information": False,
                "tools": True,
            },
        )
        json = {
            "folder": "Test1",
            "update_interval": 42,
            "print_image": True,
            "visibleInfoBlocks": {
                "preparation-time": True,
                "cooking-time": False,
                "total-time": True,
                "nutrition-information": False,
                "tools": True,
            },
        }
        assert json == c.model_dump(mode="json", by_alias=True)

    def test_deserialization(self) -> None:
        json = {
            "folder": "Test1",
            "update_interval": 42,
            "print_image": True,
            "visibleInfoBlocks": {
                "preparation-time": True,
                "cooking-time": False,
                "total-time": True,
                "nutrition-information": False,
                "tools": True,
            },
        }
        c = Config.model_validate(json)
        assert c.folder == "Test1"
        assert c.update_interval == 42
        assert c.print_image
        assert c.visible_info_blocks.preparation_time
        assert not c.visible_info_blocks.cooking_time
        assert c.visible_info_blocks.total_time
        assert not c.visible_info_blocks.nutrition_information
        assert c.visible_info_blocks.tools


if __name__ == "__main__":
    unittest.main()
