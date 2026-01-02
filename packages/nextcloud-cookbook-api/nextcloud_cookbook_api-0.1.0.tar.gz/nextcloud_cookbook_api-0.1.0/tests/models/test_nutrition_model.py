import unittest

from nextcloud_cookbook_api.models import Nutrition


class TestNutritionModel(unittest.TestCase):
    def test_serialization(self) -> None:
        n = Nutrition.model_construct(
            type="NutritionInformation",
            calories="42 kcal",
            carbohydrate_content="1 g",
            cholesterol_content="2 g",
            fat_content="3 g",
            fiber_content="4 g",
            protein_content="5 g",
            saturated_fat_content="6 g",
            serving_size="7 g",
            sodium_content="8 g",
            sugar_content="9 g",
            trans_fat_content="10 g",
            unsaturated_fat_content="11 g",
        )
        json = {
            "@type": "NutritionInformation",
            "calories": "42 kcal",
            "carbohydrateContent": "1 g",
            "cholesterolContent": "2 g",
            "fatContent": "3 g",
            "fiberContent": "4 g",
            "proteinContent": "5 g",
            "saturatedFatContent": "6 g",
            "servingSize": "7 g",
            "sodiumContent": "8 g",
            "sugarContent": "9 g",
            "transFatContent": "10 g",
            "unsaturatedFatContent": "11 g",
        }
        assert json == n.model_dump(mode="json", by_alias=True)

    def test_deserialization(self) -> None:
        json = {
            "@type": "NutritionInformation",
            "calories": "42 kcal",
            "carbohydrateContent": "1 g",
            "cholesterolContent": "2 g",
            "fatContent": "3 g",
            "fiberContent": "4 g",
            "proteinContent": "5 g",
            "saturatedFatContent": "6 g",
            "servingSize": "7 g",
            "sodiumContent": "8 g",
            "sugarContent": "9 g",
            "transFatContent": "10 g",
            "unsaturatedFatContent": "11 g",
        }
        v = Nutrition.model_validate(json)
        assert v.calories == "42 kcal"
        assert v.carbohydrate_content == "1 g"
        assert v.cholesterol_content == "2 g"
        assert v.fat_content == "3 g"
        assert v.fiber_content == "4 g"
        assert v.protein_content == "5 g"
        assert v.saturated_fat_content == "6 g"
        assert v.serving_size == "7 g"
        assert v.sodium_content == "8 g"
        assert v.sugar_content == "9 g"
        assert v.trans_fat_content == "10 g"
        assert v.unsaturated_fat_content == "11 g"


if __name__ == "__main__":
    unittest.main()
