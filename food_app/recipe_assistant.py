from typing import List, Dict, Optional
from .database import FoodDatabase
import json

class RecipeAssistant:
    def __init__(self, db: FoodDatabase):
        """Initialize the recipe assistant."""
        self.db = db
        self.style_prompt = """You are a cooking assistant inspired by Chef Gordon Ramsay. 
Use his passionate, direct style while being helpful and encouraging. Focus on:
- Fresh, quality ingredients ("fresh is best!")
- Proper seasoning and technique ("taste, taste, TASTE!")
- Simple but elegant presentations ("we eat with our eyes first")
- Professional kitchen tips ("let the pan get smoking hot!")
- Honest feedback about ingredient combinations

Use Gordon's signature phrases like:
- "Beautiful!"
- "Perfectly cooked"
- "Let it rest, you donut!"
- "Season it properly!"
- "Fresh herbs make all the difference"
- "Keep it simple, let the ingredients shine"

Keep suggestions practical for home cooks while maintaining high standards.
Be passionate about food but encouraging to the cook."""

    def generate_recipe_prompt(self, inventory_items: List[Dict]) -> str:
        """Generate a prompt for recipe suggestions based on inventory."""
        items_by_category = {}
        for item in inventory_items:
            category = item.get('type', 'other')
            if category not in items_by_category:
                items_by_category[category] = []
            items_by_category[category].append({
                'name': item.get('name', ''),
                'quantity': item.get('quantity', '')
            })

        prompt = f"{self.style_prompt}\n\n"
        prompt += "Based on these available ingredients:\n\n"
        
        for category, items in items_by_category.items():
            prompt += f"{category.upper()}:\n"
            for item in items:
                quantity = f" ({item['quantity']})" if item['quantity'] else ""
                prompt += f"- {item['name']}{quantity}\n"
        
        prompt += """
Right then, you gorgeous lot of ingredients! Let me suggest 3 different dishes you could make, yeah?

Consider:
1. What you've got in your inventory
2. What key ingredients you might be missing (don't worry, we'll sort that)
3. Basic pantry items you should have (olive oil, salt, pepper - the essentials!)

For each recipe, give me:
1. A proper name that'll make them go 'wow'
2. Ingredients list (what they've got vs what they need to get)
3. Step-by-step instructions (keep it clear and precise)
4. My personal chef's tips (the secret to making it restaurant quality)
5. Difficulty level (Easy/Medium/Hard)

Format your response as JSON like this (and make it perfect, yeah?):
{
    "recipes": [
        {
            "name": "Recipe Name (make it sound appetizing!)",
            "difficulty": "Easy/Medium/Hard",
            "have_ingredients": ["ingredient1", "ingredient2"],
            "need_ingredients": ["ingredient3", "ingredient4"],
            "instructions": ["step1", "step2", "step3"],
            "chef_tips": ["tip1", "tip2"]
        }
    ],
    "general_tips": ["tip1", "tip2"]
}

Make it sound like me - passionate, direct, and always pushing for excellence!"""

        return prompt

    def suggest_recipes(self, grok_response: str) -> Dict:
        """Parse and process recipe suggestions from Grok."""
        try:
            # Try to extract JSON from the response
            if '{' in grok_response and '}' in grok_response:
                start = grok_response.find('{')
                end = grok_response.rfind('}') + 1
                json_text = grok_response[start:end]
                return json.loads(json_text)
            else:
                return {
                    "error": "Come on! I couldn't generate proper recipe suggestions. Let's try that again, yeah?"
                }
        except json.JSONDecodeError:
            return {
                "error": "Bloody hell! Something went wrong with the recipe format. One more time!"
            }
        except Exception as e:
            return {
                "error": f"Oh for heaven's sake! Something went wrong: {str(e)}"
            }

    def format_recipe_output(self, recipes_data: Dict) -> str:
        """Format recipe suggestions for display."""
        if "error" in recipes_data:
            return f"\nChef's Note: {recipes_data['error']}"

        output = "\nGordon's Recipe Suggestions"
        output += "\n" + "=" * 50 + "\n"

        for i, recipe in enumerate(recipes_data["recipes"], 1):
            output += f"\nRecipe {i}: {recipe['name'].upper()}"
            output += f"\nDifficulty: {recipe['difficulty']}"
            
            output += "\n\nYou've Got (beautiful ingredients!):"
            for ing in recipe['have_ingredients']:
                output += f"\n✓ {ing}"
            
            output += "\n\nYou'll Need (get these sorted!):"
            for ing in recipe['need_ingredients']:
                output += f"\n• {ing}"
            
            output += "\n\nMethod (follow this carefully, yeah?):"
            for j, step in enumerate(recipe['instructions'], 1):
                output += f"\n{j}. {step}"
            
            output += "\n\nChef's Tips (these make the difference!):"
            for tip in recipe['chef_tips']:
                output += f"\n• {tip}"
            
            output += "\n" + "-" * 50

        if recipes_data.get("general_tips"):
            output += "\n\nGeneral Kitchen Tips (listen up!):"
            for tip in recipes_data["general_tips"]:
                output += f"\n• {tip}"

        return output

    def save_recipe(self, recipe_data: Dict) -> bool:
        """Save a recipe to the user's collection."""
        # TODO: Implement recipe storage
        pass

    def get_saved_recipes(self) -> List[Dict]:
        """Get user's saved recipes."""
        # TODO: Implement recipe retrieval
        pass 