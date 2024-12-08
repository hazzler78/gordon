from food_app.database import FoodDatabase
from food_app.inventory_manager import InventoryManager
from food_app.categories import FoodCategories

def print_menu():
    """Print the main menu."""
    print("\nInventory Management")
    print("=" * 50)
    print("1. View/Edit items")
    print("2. View item details")
    print("3. Edit item")
    print("4. Delete item")
    print("5. Check category suggestions")
    print("6. View categories")
    print("0. Exit")

def get_item_id() -> int:
    """Get item ID from user input."""
    while True:
        try:
            item_id = int(input("Enter item ID: "))
            return item_id
        except ValueError:
            print("Please enter a valid number.")

def edit_item_menu(manager: InventoryManager):
    """Menu for editing an item."""
    item_id = get_item_id()
    
    print("\nWhat would you like to edit?")
    print("1. Name")
    print("2. Category")
    print("3. Brand")
    print("4. Quantity")
    print("0. Cancel")
    
    choice = input("Enter choice: ")
    
    updates = {}
    if choice == "1":
        name = input("Enter new name: ")
        updates['name'] = name
    elif choice == "2":
        print("\nValid categories:")
        for cat in FoodCategories.get_categories():
            desc = FoodCategories.get_category_description(cat)
            print(f"- {cat}: {desc}")
        category = input("\nEnter new category: ")
        updates['type'] = category
    elif choice == "3":
        brand = input("Enter new brand (or 'unknown'): ")
        updates['brand'] = brand
    elif choice == "4":
        quantity = input("Enter new quantity: ")
        updates['quantity'] = quantity
    elif choice == "0":
        return
    
    if updates:
        manager.edit_item(item_id, updates)

def view_categories():
    """View all available categories and their descriptions."""
    print("\nAvailable Categories:")
    print("=" * 50)
    for category in FoodCategories.get_categories():
        desc = FoodCategories.get_category_description(category)
        print(f"\n{category.upper()}")
        print(f"Description: {desc}")

def view_and_edit_inventory(db: FoodDatabase, manager: InventoryManager):
    """View inventory with option to edit items directly."""
    while True:
        inventory = db.get_inventory()
        if not inventory:
            print("\nInventory is empty!")
            return
            
        print("\nCurrent Inventory:")
        print("=" * 50)
        
        # Group items by category
        items_by_category = {}
        for item in inventory:
            category = item.get('type', 'other')
            if category not in items_by_category:
                items_by_category[category] = []
            items_by_category[category].append(item)
        
        # Print items by category with numbers
        item_number = 1
        numbered_items = {}  # Store mapping of numbers to items
        
        for category, items in sorted(items_by_category.items()):
            print(f"\n{category.upper()}:")
            for item in sorted(items, key=lambda x: x['name'].lower()):
                print(f"{item_number}. {item['name']}", end='')
                if item['brand']:
                    print(f" ({item['brand']})", end='')
                if item['quantity']:
                    print(f" - {item['quantity']}", end='')
                print()  # New line
                numbered_items[item_number] = item
                item_number += 1
        
        print("\nWhat would you like to do?")
        print("1. Edit item (enter item number)")
        print("2. Delete item (enter item number)")
        print("0. Back to main menu")
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == "0":
            break
        
        if choice in ["1", "2"]:
            try:
                item_num = int(input("Enter item number: "))
                if item_num not in numbered_items:
                    print("\nInvalid item number!")
                    continue
                
                selected_item = numbered_items[item_num]
                
                if choice == "1":
                    # Edit item
                    print(f"\nEditing: {selected_item['name']}")
                    print("What would you like to edit?")
                    print("1. Name")
                    print("2. Category")
                    print("3. Brand")
                    print("4. Quantity")
                    print("0. Cancel")
                    
                    edit_choice = input("Enter choice: ")
                    updates = {}
                    
                    if edit_choice == "1":
                        name = input("Enter new name: ")
                        updates['name'] = name
                    elif edit_choice == "2":
                        print("\nValid categories:")
                        for cat in FoodCategories.get_categories():
                            desc = FoodCategories.get_category_description(cat)
                            print(f"- {cat}: {desc}")
                        category = input("\nEnter new category: ")
                        updates['type'] = category
                    elif edit_choice == "3":
                        brand = input("Enter new brand (or 'unknown'): ")
                        updates['brand'] = brand
                    elif edit_choice == "4":
                        quantity = input("Enter new quantity: ")
                        updates['quantity'] = quantity
                    
                    if updates:
                        manager.edit_item(selected_item['id'], updates)
                
                elif choice == "2":
                    # Delete item - Show full details before deletion
                    print(f"\nAbout to delete item #{item_num}:")
                    print("-" * 40)
                    print(f"Name: {selected_item['name']}")
                    if selected_item['brand']:
                        print(f"Brand: {selected_item['brand']}")
                    print(f"Category: {selected_item['type']}")
                    if selected_item['quantity']:
                        print(f"Quantity: {selected_item['quantity']}")
                    
                    if input("\nConfirm deletion? (y/n): ").lower() == 'y':
                        if manager.delete_item(selected_item['id']):
                            print(f"\nSuccessfully deleted {selected_item['name']}")
                        else:
                            print("\nFailed to delete item!")
            
            except ValueError:
                print("\nPlease enter a valid number!")
        else:
            print("\nInvalid choice!")
        
        input("\nPress Enter to continue...")

def main():
    """Main function for inventory management."""
    db = FoodDatabase()
    manager = InventoryManager(db)
    
    while True:
        print_menu()
        choice = input("\nEnter choice: ")
        
        if choice == "1":
            view_and_edit_inventory(db, manager)
        
        elif choice == "2":
            # View item details
            item_id = get_item_id()
            manager.print_item(item_id)
        
        elif choice == "3":
            # Edit item
            edit_item_menu(manager)
        
        elif choice == "4":
            # Delete item
            item_id = get_item_id()
            manager.delete_item(item_id)
        
        elif choice == "5":
            # Check category suggestions
            manager.print_category_suggestions()
        
        elif choice == "6":
            # View categories
            view_categories()
        
        elif choice == "0":
            print("\nGoodbye!")
            break
        
        else:
            print("\nInvalid choice. Please try again.")
        
        if choice != "1":  # Don't show this for view/edit mode
            input("\nPress Enter when you're ready to continue...")

if __name__ == "__main__":
    main() 