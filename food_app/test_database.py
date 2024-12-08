import unittest
from database import FoodDatabase
import os

class TestFoodDatabase(unittest.TestCase):
    def setUp(self):
        """Set up test database."""
        self.test_db = "test_food_app.db"
        self.db = FoodDatabase(self.test_db)
        
    def tearDown(self):
        """Clean up test database."""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_add_inventory_items(self):
        """Test adding items to inventory."""
        # Test items from vision API format
        items = [
            {
                "name": "Coca-Cola",
                "type": "beverage",
                "brand": "Coca-Cola",
                "quantity": "2 cans"
            },
            {
                "name": "Potato Chips",
                "type": "packaged",
                "brand": "Lay's",
                "quantity": "1 bag"
            }
        ]
        
        # Add items
        success = self.db.add_inventory_items(items)
        self.assertTrue(success)
        
        # Verify items were added
        inventory = self.db.get_inventory()
        self.assertEqual(len(inventory), 2)
        
        # Check first item details
        first_item = inventory[0]  # Items are ordered by name, so Coca-Cola should be first
        self.assertEqual(first_item['name'], "Coca-Cola")
        self.assertEqual(first_item['type'], "beverage")
        self.assertEqual(first_item['brand'], "Coca-Cola")
        self.assertEqual(first_item['quantity'], "2 cans")
        self.assertEqual(first_item['quantity_number'], 2)
        self.assertEqual(first_item['unit'], "cans")
    
    def test_search_inventory(self):
        """Test searching inventory items."""
        # Add test items
        items = [
            {"name": "Apple Juice", "type": "beverage", "brand": "Test Brand"},
            {"name": "Orange Juice", "type": "beverage", "brand": "Test Brand"},
            {"name": "Potato Chips", "type": "snack", "brand": "Test Brand"}
        ]
        self.db.add_inventory_items(items)
        
        # Search for juice
        results = self.db.search_inventory("juice")
        self.assertEqual(len(results), 2)
        
        # Search by brand
        results = self.db.search_inventory("Test Brand")
        self.assertEqual(len(results), 3)
    
    def test_update_inventory_item(self):
        """Test updating inventory items."""
        # Add test item
        items = [{"name": "Test Item", "type": "test", "quantity": "1 piece"}]
        self.db.add_inventory_items(items)
        
        # Get the item ID
        inventory = self.db.get_inventory()
        item_id = inventory[0]['id']
        
        # Update the item
        updates = {
            "name": "Updated Item",
            "quantity": "2 pieces"
        }
        success = self.db.update_inventory_item(item_id, updates)
        self.assertTrue(success)
        
        # Verify update
        updated_inventory = self.db.get_inventory()
        updated_item = updated_inventory[0]
        self.assertEqual(updated_item['name'], "Updated Item")
        self.assertEqual(updated_item['quantity'], "2 pieces")
    
    def test_delete_inventory_item(self):
        """Test deleting inventory items."""
        # Add test item
        items = [{"name": "Test Item", "type": "test"}]
        self.db.add_inventory_items(items)
        
        # Get the item ID
        inventory = self.db.get_inventory()
        item_id = inventory[0]['id']
        
        # Delete the item
        success = self.db.delete_inventory_item(item_id)
        self.assertTrue(success)
        
        # Verify deletion
        inventory = self.db.get_inventory()
        self.assertEqual(len(inventory), 0)

if __name__ == '__main__':
    unittest.main() 