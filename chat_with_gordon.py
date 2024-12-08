from food_app.database import FoodDatabase
from food_app.grok_api import GrokAPI
from food_app.recipe_assistant import RecipeAssistant
from food_app.inventory_chat import InventoryChat

def main():
    """Start chatting with Gordon directly."""
    print("\nInitializing Gordon's Kitchen Assistant...")
    
    try:
        # Initialize components
        db = FoodDatabase()
        grok = GrokAPI()
        recipe_assistant = RecipeAssistant(db)
        
        # Create chat interface with all components connected
        chat = InventoryChat(db, grok, recipe_assistant)
        
        # Start chatting
        chat.chat()
        
    except Exception as e:
        print(f"\nOh bloody hell! Something went wrong starting up: {str(e)}")
        print("Make sure you have all the required components set up properly!")

if __name__ == "__main__":
    main() 