# Gordon's Kitchen Assistant

A smart kitchen management system with an AI-powered chat interface featuring Gordon Ramsay's personality. Manage your inventory, get recipe suggestions, and organize your shopping with style!

## Features

- **Chat with Gordon**: Interact naturally with an AI assistant that has Gordon Ramsay's personality
- **Smart Inventory Management**: 
  - Add and track ingredients with automatic categorization
  - Organize items by categories (fresh fruits, vegetables, meats, etc.)
  - Edit and update quantities easily
- **Recipe Suggestions**: 
  - Get recipe ideas based on your current inventory
  - Save favorite recipes
  - Receive cooking tips in Gordon's style
- **Shopping Lists**:
  - Create shopping lists from recipes
  - Mark items as purchased
  - Automatically add purchased items to inventory
  - Track shopping list status

## Requirements

- Python 3.8+
- Grok API key (for AI chat functionality)
- SQLite3 (included with Python)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/gordons-kitchen.git
cd gordons-kitchen
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment:
```bash
cp .env.example .env
# Edit .env with your Grok API key
```

## Usage

### Start Chatting with Gordon
```bash
python chat_with_gordon.py
```

### Manage Inventory
```bash
python manage_inventory.py
```

### Get Recipe Suggestions
```bash
python suggest_recipes.py
```

## Project Structure

```
food_app/
├── __init__.py
├── app.py              # Main application logic
├── categories.py       # Food categorization system
├── database.py         # SQLite database handling
├── grok_api.py        # Grok API integration
├── inventory_chat.py   # Chat interface
├── inventory_manager.py # Inventory management
└── recipe_assistant.py # Recipe suggestion system

chat_with_gordon.py     # Chat entry point
manage_inventory.py     # Inventory management entry point
suggest_recipes.py      # Recipe suggestions entry point
```

## Features in Detail

### Categories
- Fresh Fruits & Vegetables
- Fresh Herbs & Spices
- Fresh Meat & Seafood
- Dairy Products
- Frozen Foods
- Pantry Items
- And more...

### Smart Categorization
- Automatic category suggestions
- Learning from user preferences
- Handles variations (e.g., "sea salt" → "salt")
- Prevents duplicate items

### Shopping List Management
- Create lists from recipes
- Add custom items
- Track purchased items
- Convert to inventory

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/) 