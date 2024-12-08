from typing import List, Dict, Optional
from .database import FoodDatabase
from .categories import FoodCategories
from .grok_api import GrokAPI
from .recipe_assistant import RecipeAssistant
import json

class InventoryChat:
    def __init__(self, db: FoodDatabase, grok: GrokAPI, recipe_assistant: Optional['RecipeAssistant'] = None):
        """Initialize the inventory chat interface."""
        self.db = db
        self.grok = grok
        self.recipe_assistant = recipe_assistant or RecipeAssistant(db)
        self.chat_prompt = """You are Gordon Ramsay managing a kitchen and helping with cooking.
Be helpful while maintaining your signature style - passionate, direct, and encouraging.

Understand the user's intent:
1. Adding items: "I bought...", "Just got...", "Need to add..."
2. Removing items: "Remove...", "Delete...", "Take out...", "Used up..."
3. Recipe requests: "What can I cook?", "Recipe ideas?", "What should I make?"
4. Viewing inventory: "What do I have?", "Show inventory", "What's in stock?"
5. General cooking advice: Any cooking questions

Format your responses as JSON:
{
    "intent": "add_items/remove_items/get_recipes/view_inventory/cooking_advice",
    "items": [  # For add/remove intents
        {
            "name": "item name",
            "type": "category",
            "quantity": "amount",
            "brand": "brand name if mentioned",
            "action": "add/remove"
        }
    ],
    "response": "your response in Gordon's style",
    "follow_up": "any follow-up question"
}"""

    def handle_intent(self, result: Dict) -> bool:
        """Handle different conversation intents."""
        intent = result.get('intent', 'cooking_advice')
        
        if intent == 'add_items':
            return self._handle_add_items(result.get('items', []))
        
        elif intent == 'remove_items':
            return self._handle_remove_items(result.get('items', []))
        
        elif intent == 'get_recipes':
            return self._handle_recipe_request()  # Use the recipe handler
        
        elif intent == 'view_inventory':
            self._show_inventory()
            return True
        
        return True  # For cooking_advice, just show the response

    def _handle_add_items(self, items: List[Dict]) -> bool:
        """Handle adding items to inventory."""
        if not items:
            return False
            
        # Validate categories
        valid_items = []
        for item in items:
            # Suggest category if needed
            if not FoodCategories.is_valid_category(item['type']):
                suggested = FoodCategories.suggest_category(item['name'])
                print(f"\nGordon: For {item['name']}, I suggest the '{suggested}' category.")
                confirm = input("Use this category? (y/n): ").lower()
                if confirm == 'y':
                    item['type'] = suggested
                else:
                    print("\nGordon: Right then, what category should it be?")
                    print("Available categories:")
                    for cat in FoodCategories.get_categories():
                        desc = FoodCategories.get_category_description(cat)
                        print(f"- {cat}: {desc}")
                    new_cat = input("Category: ").strip().lower()
                    if FoodCategories.is_valid_category(new_cat):
                        item['type'] = new_cat
                    else:
                        print(f"\nGordon: That's not a valid category! We'll use '{suggested}'.")
                        item['type'] = suggested
            
            valid_items.append(item)
        
        # Add items to inventory
        if valid_items:
            success = self.db.add_inventory_items(valid_items)
            if success:
                print("\nGordon: Beautiful! Added to inventory:")
                for item in valid_items:
                    quantity = f" - {item['quantity']}" if item.get('quantity') else ""
                    brand = f" ({item['brand']})" if item.get('brand') else ""
                    print(f"✓ {item['name']}{brand}{quantity}")
                return True
            else:
                print("\nGordon: Bloody hell! Something went wrong adding the items!")
        
        return False

    def _handle_remove_items(self, items: List[Dict]) -> bool:
        """Handle removing items from inventory."""
        if not items:
            return False
        
        inventory = self.db.get_inventory()
        for item in items:
            # Try to find matching items
            matches = [
                inv_item for inv_item in inventory
                if inv_item['name'].lower() == item['name'].lower()
            ]
            
            if not matches:
                print(f"\nGordon: I can't find {item['name']} in the inventory!")
                continue
            
            if len(matches) == 1:
                # Single match, confirm deletion
                match = matches[0]
                print(f"\nGordon: Found {match['name']}")
                if match['brand']:
                    print(f"Brand: {match['brand']}")
                if match['quantity']:
                    print(f"Quantity: {match['quantity']}")
                
                if input("Remove this item? (y/n): ").lower() == 'y':
                    if self.db.delete_inventory_item(match['id']):
                        print(f"Gordon: Removed {match['name']} from inventory.")
                    else:
                        print("Gordon: Something went wrong removing the item!")
            else:
                # Multiple matches, let user choose
                print(f"\nGordon: Found multiple {item['name']}. Which one?")
                for i, match in enumerate(matches, 1):
                    brand = f" ({match['brand']})" if match['brand'] else ""
                    quantity = f" - {match['quantity']}" if match['quantity'] else ""
                    print(f"{i}. {match['name']}{brand}{quantity}")
                
                try:
                    choice = int(input("Enter number (0 to skip): "))
                    if 1 <= choice <= len(matches):
                        match = matches[choice - 1]
                        if self.db.delete_inventory_item(match['id']):
                            print(f"Gordon: Removed {match['name']} from inventory.")
                        else:
                            print("Gordon: Something went wrong removing the item!")
                except ValueError:
                    print("Gordon: That's not a valid number!")
        
        return True

    def _handle_recipe_request(self) -> bool:
        """Handle recipe suggestions one at a time."""
        inventory = self.db.get_inventory()
        if not inventory:
            print("\nGordon: Your inventory is empty! Let's get some ingredients in there first, yeah?")
            return False
        
        print("\nGordon: Right then, let me see what we can make with what you've got...")
        
        while True:
            # Generate the prompt for a single recipe
            prompt = self.recipe_assistant.generate_recipe_prompt(inventory)
            prompt = prompt.replace("suggest 3 different dishes", "suggest 1 dish")  # Modify for single recipe
            
            try:
                # Get suggestion from Grok
                messages = [{"role": "user", "content": prompt}]
                response = self.grok.client.chat.completions.create(
                    model="grok-beta",
                    messages=messages,
                    temperature=0.7,
                    stream=False
                )
                
                # Parse the response
                response_text = response.choices[0].message.content
                recipes_data = self.recipe_assistant.suggest_recipes(response_text)
                
                if "error" in recipes_data:
                    print(f"\nGordon: {recipes_data['error']}")
                    return False
                
                # Display the single recipe
                if recipes_data.get("recipes"):
                    recipe = recipes_data["recipes"][0]
                    print("\nGordon's Recipe Suggestion")
                    print("=" * 50)
                    print(f"\nRecipe: {recipe['name'].upper()}")
                    print(f"Difficulty: {recipe['difficulty']}")
                    
                    print("\nYou've Got (beautiful ingredients!):")
                    for ing in recipe['have_ingredients']:
                        print(f"✓ {ing}")
                    
                    print("\nYou'll Need (get these sorted!):")
                    for ing in recipe['need_ingredients']:
                        print(f"• {ing}")
                    
                    print("\nMethod (follow this carefully, yeah?):")
                    for i, step in enumerate(recipe['instructions'], 1):
                        print(f"{i}. {step}")
                    
                    print("\nChef's Tips (these make the difference!):")
                    for tip in recipe['chef_tips']:
                        print(f"• {tip}")
                    
                    # Ask what to do with this recipe
                    while True:
                        choice = input("\nGordon: What shall we do? (save/next/quit): ").lower()
                        if choice == 'save':
                            recipe_id = self.db.save_recipe(recipe)
                            if recipe_id:
                                print("\nGordon: Beautiful! Recipe saved to your collection.")
                            else:
                                print("\nGordon: Something went wrong saving the recipe!")
                            break
                        elif choice == 'next':
                            print("\nGordon: Right then, let me think of something else...")
                            break
                        elif choice == 'quit':
                            return True
                        else:
                            print("\nGordon: Come on! Just type 'save', 'next', or 'quit'!")
                    
                    if choice == 'quit':
                        break
                
            except Exception as e:
                print(f"\nGordon: Oh for heaven's sake! Something went wrong: {str(e)}")
                return False
        
        return True

    def chat(self):
        """Start a chat session with Gordon."""
        print("\nGordon's Kitchen Assistant")
        print("=" * 50)
        print("(Type 'quit' to exit, 'help' for assistance)")
        print("\nGordon: Right then, what can I help you with today?")
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() == 'quit':
                    print("\nGordon: Take care of those ingredients, yeah? Goodbye!")
                    break
                    
                if user_input.lower() == 'help':
                    self._show_help()
                    continue
                
                if user_input.lower() == 'show':
                    self._show_inventory()
                    continue
                
                # Process the input with Grok
                prompt = f"{self.chat_prompt}\n\nUser message: {user_input}\n\nRespond as Gordon Ramsay."
                
                response = self.grok.client.chat.completions.create(
                    model="grok-beta",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    stream=False
                )
                
                # Parse the response
                response_text = response.choices[0].message.content
                
                try:
                    # Extract JSON from response
                    start = response_text.find('{')
                    end = response_text.rfind('}') + 1
                    json_text = response_text[start:end]
                    result = json.loads(json_text)
                    
                    # Print Gordon's response
                    print(f"\nGordon: {result['response']}")
                    
                    # Handle the intent
                    self.handle_intent(result)
                    
                    # Ask follow-up if provided
                    if result.get('follow_up'):
                        print(f"\nGordon: {result['follow_up']}")
                    
                except json.JSONDecodeError:
                    print("\nGordon: Sorry, I didn't quite get that. Can you be more specific?")
                
            except Exception as e:
                print(f"\nGordon: Bloody hell! Something went wrong: {str(e)}")

    def _show_help(self):
        """Show help information."""
        print("\nGordon's Kitchen Chat Help")
        print("=" * 50)
        print("Just chat naturally! You can:")
        print("1. Add items:")
        print("   - 'I bought some tomatoes and pasta'")
        print("   - 'Just got olive oil from the store'")
        print("2. Remove items:")
        print("   - 'Remove the old lettuce'")
        print("   - 'Used up all the pasta'")
        print("3. Get recipe ideas:")
        print("   - 'What can I cook?'")
        print("   - 'Any dinner suggestions?'")
        print("4. View inventory:")
        print("   - 'What do I have?'")
        print("   - 'Show me my ingredients'")
        print("5. Get cooking advice:")
        print("   - Ask any cooking question!")
        print("\nCommands:")
        print("- 'show': View current inventory")
        print("- 'help': Show this help message")
        print("- 'quit': Exit the chat")
    
    def _show_inventory(self):
        """Show current inventory."""
        inventory = self.db.get_inventory()
        if not inventory:
            print("\nGordon: The inventory is empty! Let's get some ingredients in there!")
            return
        
        print("\nGordon: Right, here's what we've got:")
        print("=" * 50)
        
        # Group by category
        by_category = {}
        for item in inventory:
            category = item.get('type', 'other')
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(item)
        
        # Print by category
        for category, items in by_category.items():
            print(f"\n{category.upper()}:")
            for item in items:
                name = item['name']
                brand = f" ({item['brand']})" if item['brand'] else ""
                quantity = f" - {item['quantity']}" if item['quantity'] else ""
                print(f"  • {name}{brand}{quantity}") 