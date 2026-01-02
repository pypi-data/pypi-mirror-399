import unittest
from datetime import datetime

from pydantic_core import TzInfo

from nextcloud_cookbook_api.models import Recipe


class TestRecipeModel(unittest.TestCase):
    def test_serialization(self) -> None:
        r = Recipe.model_construct(
            id=1,
            name="Test Recipe",
            keywords=["test", "recipe"],
            date_created="2021-01-01T00:00:00+00:00",
            date_modified="2021-01-01T00:00:00+00:00",
            image_url="https://example.com/image.jpg",
            image_placeholder_url="https://example.com/placeholder.jpg",
            prep_time="PT1H",
            cook_time="PT1H",
            total_time="PT2H",
            description="Test description",
            url="https://example.com/recipe.html",
            image="https://example.com/image.jpg",
            servings=42,
            category="Dessert",
            tools=["Tool 1", "Tool 2"],
            ingredients=["Ingredient 1", "Ingredient 2"],
            instructions=["Step 1", "Step 2"],
            nutrition={"calories": "4200"},
        )
        json = {
            "id": 1,
            "name": "Test Recipe",
            "keywords": "test,recipe",
            "dateCreated": "2021-01-01T00:00:00+00:00",
            "dateModified": "2021-01-01T00:00:00+00:00",
            "imageUrl": "https://example.com/image.jpg",
            "imagePlaceholderUrl": "https://example.com/placeholder.jpg",
            "prepTime": "PT1H",
            "cookTime": "PT1H",
            "totalTime": "PT2H",
            "description": "Test description",
            "url": "https://example.com/recipe.html",
            "image": "https://example.com/image.jpg",
            "recipeYield": 42,
            "recipeCategory": "Dessert",
            "tools": ["Tool 1", "Tool 2"],
            "recipeIngredient": ["Ingredient 1", "Ingredient 2"],
            "recipeInstructions": ["Step 1", "Step 2"],
            "nutrition": {"calories": "4200"},
        }
        assert json == r.model_dump(mode="json", by_alias=True)

    def test_deserialization(self) -> None:
        json = {
            "@type": "Recipe",
            "id": "1",
            "name": "Test Recipe",
            "keywords": "test,recipe",
            "dateCreated": "2021-01-01T00:00:00+00:00",
            "dateModified": "2021-01-02T00:00:00+00:00",
            "imageUrl": "https://example.com/image.jpg",
            "imagePlaceholderUrl": "https://example.com/placeholder.jpg",
            "prepTime": "PT1H",
            "cookTime": "PT1H",
            "totalTime": "PT2H",
            "description": "Test description",
            "url": "https://example.com/recipe.html",
            "image": "https://example.com/image.jpg",
            "recipeYield": 42,
            "recipeCategory": "Dessert",
            "tools": ["Tool 1", "Tool 2"],
            "recipeIngredient": ["Ingredient 1", "Ingredient 2"],
            "recipeInstructions": ["Step 1", "Step 2"],
            "nutrition": {"@type": "NutritionInformation", "calories": "4200"},
        }
        v = Recipe.model_validate(json)
        assert v.id == "1"
        assert v.name == "Test Recipe"
        assert v.keywords == ["test", "recipe"]
        assert datetime(2021, 1, 1, 0, 0, tzinfo=TzInfo(0)) == v.date_created
        assert datetime(2021, 1, 2, 0, 0, tzinfo=TzInfo(0)) == v.date_modified
        assert v.image_url == "https://example.com/image.jpg"
        assert v.image_placeholder_url == "https://example.com/placeholder.jpg"
        assert v.prep_time == "PT1H"
        assert v.cook_time == "PT1H"
        assert v.total_time == "PT2H"
        assert v.description == "Test description"
        assert v.url == "https://example.com/recipe.html"
        assert v.image == "https://example.com/image.jpg"
        assert v.servings == 42
        assert v.category == "Dessert"
        assert v.tools == ["Tool 1", "Tool 2"]
        assert v.ingredients == ["Ingredient 1", "Ingredient 2"]
        assert v.instructions == ["Step 1", "Step 2"]
        assert v.nutrition.calories == "4200"


if __name__ == "__main__":
    unittest.main()
