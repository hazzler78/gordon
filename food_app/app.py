from food_app.database import FoodDatabase
from food_app.grok_api import GrokAPI
from typing import List, Dict, Optional, Tuple
import os

class FoodApp:
    def __init__(self, db_path: str = "food_app.db"):
        """Initialize the Food App with database and Grok API."""
        self.db = FoodDatabase(db_path)
        self.grok = GrokAPI()
    
    def scan_and_add_items(self, image_source: str) -> Tuple[bool, List[str]]:
        """
        Scan an image for food items and add them to inventory.
        
        Args:
            image_source: Path to local image file or URL
            
        Returns:
            Tuple[bool, List[str]]: (success, list of added items)
        """
        try:
            # Analyze the image using Grok Vision
            contains_food, food_items, description = self.grok.analyze_food_image(image_source)
            
            if not contains_food or not food_items:
                print("\nNo food items were detected or could be added to the inventory.")
                return False, []
            
            # Add items to database
            success = self.db.add_inventory_items(food_items)
            
            if success:
                item_names = [item.get('name', '') for item in food_items if item.get('name')]
                print(f"\nSuccessfully added {len(item_names)} items to inventory:")
                for name in item_names:
                    print(f"- {name}")
                return True, item_names
            else:
                print("\nFailed to add items to inventory.")
                return False, []
            
        except Exception as e:
            print(f"\nError scanning and adding items: {str(e)}")
            return False, []
    
    def get_inventory_summary(self) -> Dict:
        """
        Get a summary of current inventory.
        
        Returns:
            Dict: Summary of inventory by category
        """
        inventory = self.db.get_inventory()
        
        summary = {
            'total_items': len(inventory),
            'categories': {}
        }
        
        for item in inventory:
            category = item.get('type', 'uncategorized')
            if category not in summary['categories']:
                summary['categories'][category] = []
            summary['categories'][category].append({
                'name': item['name'],
                'brand': item['brand'],
                'quantity': item['quantity']
            })
        
        return summary
    
    def print_inventory_summary(self):
        """Print a formatted summary of the inventory."""
        summary = self.get_inventory_summary()
        
        print("\nInventory Summary")
        print("=" * 50)
        print(f"Total Items: {summary['total_items']}")
        print("\nItems by Category:")
        print("-" * 50)
        
        for category, items in summary['categories'].items():
            print(f"\n{category.upper()}:")
            for item in items:
                brand = f" ({item['brand']})" if item['brand'] else ""
                quantity = f" - {item['quantity']}" if item['quantity'] else ""
                print(f"  • {item['name']}{brand}{quantity}")

def main():
    """Main function for testing the app."""
    app = FoodApp()
    
    # Test with both local file and URL
    test_cases = [
        r"C:\Users\Micke\Pictures\image (2).jpg",  # Local file
        "https://ibb.co/QYmmWcY"  # URL
    ]
    
    for image_source in test_cases:
        print(f"\nTesting with image: {image_source}")
        print("-" * 50)
        
        success, items = app.scan_and_add_items(image_source)
        
        if success:
            print("\nCurrent Inventory:")
            app.print_inventory_summary()

if __name__ == "__main__":
    main() 