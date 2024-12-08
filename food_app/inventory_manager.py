from typing import Dict, List, Optional, Tuple
from .database import FoodDatabase
from .categories import FoodCategories

class InventoryManager:
    def __init__(self, db: FoodDatabase):
        """Initialize the inventory manager."""
        self.db = db

    def edit_item(self, item_id: int, updates: Dict) -> bool:
        """
        Edit an inventory item with validation.
        
        Args:
            item_id: ID of the item to edit
            updates: Dictionary of fields to update
            
        Returns:
            bool: Success status
        """
        # Get current item
        inventory = self.db.get_inventory()
        current_item = next((item for item in inventory if item['id'] == item_id), None)
        
        if not current_item:
            print(f"Error: Item with ID {item_id} not found.")
            return False
        
        # Validate and clean updates
        clean_updates = {}
        
        if 'name' in updates:
            name = updates['name'].strip()
            if name:
                clean_updates['name'] = name
                # Suggest category if type is being changed
                if 'type' not in updates:
                    suggested_category = FoodCategories.suggest_category(name)
                    if suggested_category != current_item['type']:
                        print(f"Suggested category for '{name}': {suggested_category}")
                        if input("Use suggested category? (y/n): ").lower() == 'y':
                            clean_updates['type'] = suggested_category
        
        if 'type' in updates:
            category = updates['type'].strip().lower()
            if FoodCategories.is_valid_category(category):
                clean_updates['type'] = category
            else:
                print(f"Invalid category: {category}")
                print("Valid categories:", ", ".join(FoodCategories.get_categories()))
                return False
        
        if 'brand' in updates:
            brand = updates['brand'].strip()
            clean_updates['brand'] = brand if brand.lower() != 'unknown' else ''
        
        if 'quantity' in updates:
            quantity = updates['quantity'].strip()
            if quantity:
                clean_updates['quantity'] = quantity
        
        if not clean_updates:
            print("No valid updates provided.")
            return False
        
        # Apply updates
        success = self.db.update_inventory_item(item_id, clean_updates)
        
        if success:
            print(f"Successfully updated item {item_id}:")
            for field, value in clean_updates.items():
                print(f"- {field}: {value}")
        else:
            print("Failed to update item.")
        
        return success

    def delete_item(self, item_id: int) -> bool:
        """
        Delete an inventory item.
        
        Args:
            item_id: ID of the item to delete
            
        Returns:
            bool: Success status
        """
        # Get current item
        inventory = self.db.get_inventory()
        item = next((item for item in inventory if item['id'] == item_id), None)
        
        if not item:
            print(f"Error: Item with ID {item_id} not found.")
            return False
        
        # Confirm deletion
        print(f"\nAbout to delete:")
        print(f"- {item['name']}")
        if item['brand']:
            print(f"  Brand: {item['brand']}")
        if item['type']:
            print(f"  Type: {item['type']}")
        if item['quantity']:
            print(f"  Quantity: {item['quantity']}")
        
        if input("\nConfirm deletion? (y/n): ").lower() != 'y':
            print("Deletion cancelled.")
            return False
        
        # Delete item
        success = self.db.delete_inventory_item(item_id)
        
        if success:
            print(f"Successfully deleted item {item_id}.")
        else:
            print("Failed to delete item.")
        
        return success

    def print_item(self, item_id: int):
        """Print details of a specific item."""
        inventory = self.db.get_inventory()
        item = next((item for item in inventory if item['id'] == item_id), None)
        
        if not item:
            print(f"Error: Item with ID {item_id} not found.")
            return
        
        print("\nItem Details:")
        print("-" * 40)
        print(f"ID: {item['id']}")
        print(f"Name: {item['name']}")
        if item['brand']:
            print(f"Brand: {item['brand']}")
        print(f"Category: {item['type']}")
        if item['quantity']:
            print(f"Quantity: {item['quantity']}")
        print(f"Added: {item['added_date']}")
        print(f"Last Updated: {item['last_updated']}")
        
        # Show category description
        if item['type']:
            desc = FoodCategories.get_category_description(item['type'])
            if desc:
                print(f"\nCategory Description: {desc}")

    def suggest_category_changes(self) -> List[Tuple[int, str, str]]:
        """
        Suggest category changes for items based on their names.
        
        Returns:
            List[Tuple[int, str, str]]: List of (item_id, current_category, suggested_category)
        """
        inventory = self.db.get_inventory()
        suggestions = []
        
        for item in inventory:
            suggested = FoodCategories.suggest_category(item['name'])
            current = item['type'] or 'uncategorized'
            
            if suggested != current:
                suggestions.append((item['id'], current, suggested))
        
        return suggestions

    def print_category_suggestions(self):
        """Print suggested category changes for items."""
        suggestions = self.suggest_category_changes()
        
        if not suggestions:
            print("\nNo category changes suggested.")
            return
        
        print("\nSuggested Category Changes:")
        print("-" * 50)
        
        for item_id, current, suggested in suggestions:
            inventory = self.db.get_inventory()
            item = next((item for item in inventory if item['id'] == item_id), None)
            if item:
                print(f"\nItem: {item['name']}")
                print(f"Current category: {current}")
                print(f"Suggested category: {suggested}")
                
                if input("Apply this change? (y/n): ").lower() == 'y':
                    success = self.edit_item(item_id, {'type': suggested})
                    if success:
                        print("Category updated.")
                    else:
                        print("Failed to update category.") 