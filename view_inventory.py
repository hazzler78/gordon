from food_app.database import FoodDatabase

def view_inventory():
    """View all items in the inventory database."""
    db = FoodDatabase("food_app.db")
    inventory = db.get_inventory()
    
    if not inventory:
        print("\nInventory is empty!")
        return
    
    print("\nCurrent Inventory:")
    print("=" * 60)
    print(f"Total Items: {len(inventory)}")
    print("-" * 60)
    
    # Print each item with all its details
    for item in inventory:
        print(f"\nItem ID: {item['id']}")
        print(f"Name: {item['name']}")
        if item['brand']:
            print(f"Brand: {item['brand']}")
        if item['type']:
            print(f"Type: {item['type']}")
        if item['quantity']:
            print(f"Quantity: {item['quantity']}")
        print(f"Added: {item['added_date']}")
        print(f"Last Updated: {item['last_updated']}")
        print("-" * 30)

if __name__ == "__main__":
    view_inventory() 