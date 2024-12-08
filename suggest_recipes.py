import json
from food_app.database import FoodDatabase
from food_app.recipe_assistant import RecipeAssistant
from food_app.grok_api import GrokAPI
from food_app.inventory_chat import InventoryChat
from food_app.categories import FoodCategories
from typing import List, Dict

def print_menu():
    """Print the main menu."""
    print("\nGordon's Kitchen Assistant")
    print("=" * 50)
    print("1. Chat with Gordon (add items to inventory)")
    print("2. What should I cook? (Get recipe suggestions)")
    print("3. View saved recipes and create shopping list")
    print("4. View current inventory")
    print("0. Exit")

def handle_recipe_suggestion(grok: GrokAPI, assistant: RecipeAssistant, db: FoodDatabase):
    """Handle recipe suggestions one at a time."""
    inventory = db.get_inventory()
    if not inventory:
        print("\nBloody hell! Your inventory is empty! Let's get some ingredients in there first, yeah?")
        return
    
    print("\nRight then, let's see what we've got...")
    print("Give me a moment to work my magic...")
    
    while True:
        # Generate the prompt
        prompt = assistant.generate_recipe_prompt(inventory)
        
        try:
            # Get suggestion from Grok
            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            response = grok.client.chat.completions.create(
                model="grok-beta",
                messages=messages,
                temperature=0.7,
                stream=False
            )
            
            # Parse the response
            response_text = response.choices[0].message.content
            recipes_data = assistant.suggest_recipes(response_text)
            
            if "error" in recipes_data:
                print(f"\n{recipes_data['error']}")
                break
            
            # Take only the first recipe
            if recipes_data["recipes"]:
                recipe = recipes_data["recipes"][0]
                print("\nHere's what I suggest:")
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
                
                # Ask to save or discard
                while True:
                    choice = input("\nShall we save this recipe? (y/n/q to quit): ").lower()
                    if choice == 'y':
                        recipe_id = db.save_recipe(recipe)
                        if recipe_id:
                            print("\nBeautiful! Recipe saved. Let's find another one, yeah?")
                        else:
                            print("\nBloody hell, something went wrong saving the recipe!")
                        break
                    elif choice == 'n':
                        print("\nNo worries, let's find something else!")
                        break
                    elif choice == 'q':
                        return
                    else:
                        print("\nCome on! Just 'y' or 'n' or 'q' to quit!")
            
        except Exception as e:
            print(f"\nOh come on! Something went wrong: {str(e)}")
            print("Let's try that again, shall we?")
            break

def handle_saved_recipes(db: FoodDatabase):
    """Handle viewing saved recipes and creating shopping lists."""
    while True:
        recipes = db.get_saved_recipes()
        if not recipes:
            print("\nNo saved recipes yet! Let's find some recipes first, yeah?")
            return
        
        print("\nYour Saved Recipes:")
        print("=" * 50)
        for i, recipe in enumerate(recipes, 1):
            print(f"\n{i}. {recipe['name']}")
            print(f"   Difficulty: {recipe['difficulty']}")
            if recipe.get('last_cooked'):
                print(f"   Last cooked: {recipe['last_cooked']}")
            if recipe.get('rating'):
                print(f"   Rating: {'⭐' * recipe['rating']}")
        
        print("\nWhat would you like to do?")
        print("1. View recipe details")
        print("2. Create shopping list")
        print("3. View shopping lists")
        print("0. Back to main menu")
        
        choice = input("\nEnter choice: ")
        
        if choice == "1":
            recipe_num = input("\nWhich recipe number? ")
            try:
                recipe_idx = int(recipe_num) - 1
                if 0 <= recipe_idx < len(recipes):
                    recipe = recipes[recipe_idx]
                    print(f"\n{recipe['name'].upper()}")
                    print("=" * 50)
                    print(f"Difficulty: {recipe['difficulty']}")
                    
                    print("\nIngredients:")
                    for ing in recipe['ingredients']:
                        print(f"• {ing['name']}")
                    
                    print("\nMethod:")
                    for i, step in enumerate(recipe['instructions'], 1):
                        print(f"{i}. {step}")
                    
                    print("\nChef's Tips:")
                    for tip in recipe['chef_tips']:
                        print(f"• {tip}")
                else:
                    print("\nThat's not a valid recipe number!")
            except ValueError:
                print("\nCome on! Enter a number!")
        
        elif choice == "2":
            print("\nSelect recipes for your shopping list (comma-separated numbers):")
            selection = input("Recipe numbers: ")
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(",")]
                selected_recipes = [recipes[i] for i in indices if 0 <= i < len(recipes)]
                
                if selected_recipes:
                    list_name = input("\nName for this shopping list: ")
                    recipe_ids = [recipe['id'] for recipe in selected_recipes]
                    list_id = db.create_shopping_list(list_name, recipe_ids)
                    
                    if list_id:
                        handle_shopping_list(db, list_id)
                    else:
                        print("\nSomething went wrong creating the shopping list!")
                else:
                    print("\nNo valid recipes selected!")
            except (ValueError, IndexError):
                print("\nInvalid selection! Use numbers separated by commas.")
        
        elif choice == "3":
            handle_shopping_lists(db)
        
        elif choice == "0":
            break
        
        else:
            print("\nInvalid choice. Please try again.")

def handle_shopping_lists(db: FoodDatabase):
    """Handle viewing and managing shopping lists."""
    while True:
        lists = db.get_shopping_lists()
        if not lists:
            print("\nNo shopping lists yet!")
            return
        
        print("\nYour Shopping Lists:")
        print("=" * 50)
        for i, lst in enumerate(lists, 1):
            print(f"\n{i}. {lst['name']}")
            print(f"   Created: {lst['created_date']}")
            print(f"   Status: {lst['status']}")
        
        print("\nWhat would you like to do?")
        print("1. View/edit list")
        print("2. Delete list")
        print("0. Back")
        
        choice = input("\nEnter choice: ")
        
        if choice == "1":
            list_num = input("\nWhich list number? ")
            try:
                list_idx = int(list_num) - 1
                if 0 <= list_idx < len(lists):
                    handle_shopping_list(db, lists[list_idx]['id'])
                else:
                    print("\nThat's not a valid list number!")
            except ValueError:
                print("\nCome on! Enter a number!")
        
        elif choice == "2":
            list_num = input("\nWhich list number to delete? ")
            try:
                list_idx = int(list_num) - 1
                if 0 <= list_idx < len(lists):
                    if db.delete_shopping_list(lists[list_idx]['id']):
                        print("\nShopping list deleted!")
                    else:
                        print("\nFailed to delete shopping list!")
                else:
                    print("\nThat's not a valid list number!")
            except ValueError:
                print("\nCome on! Enter a number!")
        
        elif choice == "0":
            break

def handle_shopping_list(db: FoodDatabase, list_id: int):
    """Handle viewing and managing a specific shopping list."""
    while True:
        shopping_list = db.get_shopping_list(list_id)
        if not shopping_list:
            print("\nShopping list not found!")
            return
        
        print(f"\nShopping List: {shopping_list['name']}")
        print("=" * 50)
        
        # Group items by recipe
        items_by_recipe = {}
        for item in shopping_list['items']:
            recipe_id = item['recipe_id']
            if recipe_id not in items_by_recipe:
                recipe = next((r for r in db.get_saved_recipes() if r['id'] == recipe_id), None)
                items_by_recipe[recipe_id] = {
                    'name': recipe['name'] if recipe else 'Custom Items',
                    'items': []
                }
            items_by_recipe[recipe_id]['items'].append(item)
        
        # Print items grouped by recipe
        for recipe_id, recipe_items in items_by_recipe.items():
            print(f"\nFor {recipe_items['name']}:")
            for item in recipe_items['items']:
                check = "✓" if item['checked'] else " "
                quantity = f" - {item['quantity']}" if item['quantity'] else ""
                print(f"[{check}] {item['name']}{quantity}")
        
        print("\nWhat would you like to do?")
        print("1. Mark/unmark items")
        print("2. Add marked items to inventory")
        print("3. Add quantities")
        print("4. Add new item")
        print("5. Remove item")
        print("0. Back")
        
        choice = input("\nEnter choice: ")
        
        if choice == "1":
            item_name = input("\nWhich item to toggle? (type the name): ").lower()
            matching_items = [
                item for item in shopping_list['items']
                if item['name'].lower() == item_name
            ]
            
            if matching_items:
                for item in matching_items:
                    db.toggle_shopping_list_item(item['id'])
                print("\nItem toggled!")
            else:
                print("\nItem not found in list!")
        
        elif choice == "2":
            # Get all checked items
            checked_items = [
                item for item in shopping_list['items']
                if item['checked']
            ]
            
            if not checked_items:
                print("\nNo items are marked as purchased!")
                continue
            
            print("\nThe following items will be added to inventory:")
            for item in checked_items:
                quantity = f" - {item['quantity']}" if item['quantity'] else ""
                print(f"• {item['name']}{quantity}")
            
            if input("\nAdd these items to inventory? (y/n): ").lower() == 'y':
                # Convert shopping list items to inventory items
                inventory_items = []
                for item in checked_items:
                    inventory_item = {
                        'name': item['name'],
                        'quantity': item['quantity'],
                        'type': FoodCategories.suggest_category(item['name']),
                        'brand': ''
                    }
                    inventory_items.append(inventory_item)
                
                if db.add_inventory_items(inventory_items):
                    print("\nItems added to inventory!")
                    # Mark list as completed if all items are checked
                    all_checked = all(item['checked'] for item in shopping_list['items'])
                    if all_checked:
                        db.update_shopping_list_status(list_id, 'completed')
                else:
                    print("\nFailed to add items to inventory!")
        
        elif choice == "3":
            item_name = input("\nWhich item to add quantity? (type the name): ").lower()
            matching_items = [
                item for item in shopping_list['items']
                if item['name'].lower() == item_name
            ]
            
            if matching_items:
                quantity = input("Enter quantity (e.g., '2 lbs', '500g'): ")
                for item in matching_items:
                    db.update_shopping_list_item(item['id'], {'quantity': quantity})
                print("\nQuantity updated!")
            else:
                print("\nItem not found in list!")

        elif choice == "4":
            # Add new item
            name = input("\nEnter item name: ")
            if not name:
                print("\nNo item name provided!")
                continue
            
            # Normalize item name and check for duplicates
            normalized_name = FoodCategories.normalize_item_name(name)
            similar_items = FoodCategories.get_similar_items(name)
            
            # Check if similar items exist in list
            existing_items = [
                item for item in shopping_list['items']
                if FoodCategories.normalize_item_name(item['name']) in similar_items
            ]
            
            if existing_items:
                print("\nSimilar items already in list:")
                for item in existing_items:
                    quantity = f" - {item['quantity']}" if item['quantity'] else ""
                    print(f"• {item['name']}{quantity}")
                if input("\nAdd anyway? (y/n): ").lower() != 'y':
                    continue
            
            quantity = input("Enter quantity (optional, press Enter to skip): ")
            
            # Get category suggestion
            category = FoodCategories.suggest_category(normalized_name)
            print(f"\nSuggested category: {category}")
            if input("Use this category? (y/n): ").lower() != 'y':
                print("\nAvailable categories:")
                for cat in FoodCategories.get_categories():
                    desc = FoodCategories.get_category_description(cat)
                    print(f"- {cat}: {desc}")
                category = input("\nEnter category: ").strip().lower()
                if not FoodCategories.is_valid_category(category):
                    print(f"\nInvalid category! Using '{category}'")
            
            # Learn the category choice
            FoodCategories.learn_category(normalized_name, category)
            
            if db.add_shopping_list_item(list_id, {
                'name': normalized_name,
                'quantity': quantity if quantity else None,
                'recipe_id': None,  # Custom item
                'checked': False
            }):
                print(f"\nAdded {normalized_name} to shopping list!")
            else:
                print("\nFailed to add item!")

        elif choice == "5":
            # Remove item
            item_name = input("\nWhich item to remove? (type the name): ").lower()
            normalized_name = FoodCategories.normalize_item_name(item_name)
            similar_items = FoodCategories.get_similar_items(item_name)
            
            # Find items matching the normalized name or similar items
            matching_items = [
                item for item in shopping_list['items']
                if FoodCategories.normalize_item_name(item['name']) in similar_items
            ]
            
            if matching_items:
                if len(matching_items) > 1:
                    print("\nMultiple items found:")
                    for i, item in enumerate(matching_items, 1):
                        quantity = f" - {item['quantity']}" if item['quantity'] else ""
                        recipe = next((r for r in db.get_saved_recipes() if r['id'] == item['recipe_id']), None)
                        recipe_name = f" (from {recipe['name']})" if recipe else ""
                        print(f"{i}. {item['name']}{quantity}{recipe_name}")
                    
                    try:
                        idx = int(input("\nWhich one to remove? (number): ")) - 1
                        if 0 <= idx < len(matching_items):
                            if db.delete_shopping_list_item(matching_items[idx]['id']):
                                print("\nItem removed!")
                            else:
                                print("\nFailed to remove item!")
                        else:
                            print("\nInvalid selection!")
                    except ValueError:
                        print("\nInvalid input!")
                else:
                    if db.delete_shopping_list_item(matching_items[0]['id']):
                        print("\nItem removed!")
                    else:
                        print("\nFailed to remove item!")
            else:
                print("\nItem not found in list!")
        
        elif choice == "0":
            break

def main():
    """Main function for recipe suggestions."""
    db = FoodDatabase()
    assistant = RecipeAssistant(db)
    grok = GrokAPI()
    chat = InventoryChat(db, grok)
    
    while True:
        print_menu()
        choice = input("\nWhat'll it be? Choose a number: ")
        
        if choice == "1":
            # Chat with Gordon to add items
            chat.chat()
        
        elif choice == "2":
            handle_recipe_suggestion(grok, assistant, db)
        
        elif choice == "3":
            handle_saved_recipes(db)
        
        elif choice == "4":
            # View current inventory
            inventory = db.get_inventory()
            if not inventory:
                print("\nYour inventory is empty! Let's get some fresh ingredients in there!")
                continue
            
            print("\nRight, let's see what we've got:")
            print("=" * 50)
            
            # Group items by category
            items_by_category = {}
            for item in inventory:
                category = item.get('type', 'other')
                if category not in items_by_category:
                    items_by_category[category] = []
                items_by_category[category].append(item)
            
            # Print items by category
            for category, items in items_by_category.items():
                print(f"\n{category.upper()}:")
                for item in items:
                    name = item['name']
                    brand = f" ({item['brand']})" if item['brand'] else ""
                    quantity = f" - {item['quantity']}" if item['quantity'] else ""
                    print(f"  • {name}{brand}{quantity}")
        
        elif choice == "0":
            print("\nTake care, and keep cooking with passion!")
            break
        
        else:
            print("\nCome on! That's not a valid choice. Try again!")
        
        if choice != "1":  # Don't show this for chat mode
            input("\nPress Enter when you're ready to continue...")

if __name__ == "__main__":
    main() 