from food_app.app import FoodApp

def main():
    app = FoodApp()
    
    # Test with an image
    image_source = r"C:\Users\Micke\Downloads\image (4).jpg"
    
    print(f"\nAnalyzing image: {image_source}")
    print("-" * 50)
    
    success, items = app.scan_and_add_items(image_source)
    
    if success:
        print("\nCurrent Inventory:")
        app.print_inventory_summary()

if __name__ == "__main__":
    main() 