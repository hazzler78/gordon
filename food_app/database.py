import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import json

class FoodDatabase:
    def __init__(self, db_path: str = "food_app.db"):
        """Initialize the database connection."""
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """Get a database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Initialize the database tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Inventory table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    type TEXT,
                    brand TEXT,
                    quantity TEXT,
                    quantity_number REAL,
                    unit TEXT,
                    expiry_date TEXT,
                    added_date TEXT NOT NULL,
                    last_updated TEXT NOT NULL
                )
            ''')
            
            # Categories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            ''')
            
            # Saved recipes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS saved_recipes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    difficulty TEXT,
                    instructions TEXT,
                    chef_tips TEXT,
                    added_date TEXT NOT NULL,
                    last_cooked TEXT,
                    rating INTEGER,
                    notes TEXT
                )
            ''')
            
            # Recipe ingredients table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS recipe_ingredients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recipe_id INTEGER,
                    name TEXT NOT NULL,
                    quantity TEXT,
                    optional BOOLEAN DEFAULT 0,
                    FOREIGN KEY (recipe_id) REFERENCES saved_recipes (id)
                )
            ''')
            
            # Shopping lists table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS shopping_lists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    created_date TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    completed_date TEXT
                )
            ''')
            
            # Shopping list items table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS shopping_list_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    list_id INTEGER,
                    name TEXT NOT NULL,
                    quantity TEXT,
                    recipe_id INTEGER,
                    checked BOOLEAN DEFAULT 0,
                    added_to_inventory BOOLEAN DEFAULT 0,
                    FOREIGN KEY (list_id) REFERENCES shopping_lists (id),
                    FOREIGN KEY (recipe_id) REFERENCES saved_recipes (id)
                )
            ''')
            
            # Insert default categories
            default_categories = [
                'fresh_produce', 'fresh_meat', 'fresh_seafood', 'fresh_dairy',
                'frozen_produce', 'frozen_meat', 'frozen_seafood', 'frozen_meals',
                'frozen_dessert', 'canned', 'condiment', 'grain', 'baking',
                'deli', 'prepared', 'bakery', 'snack', 'sweets', 'nuts',
                'beverage', 'alcohol', 'organic', 'gluten_free', 'vegan',
                'international', 'breakfast', 'baby', 'pet', 'health', 'other'
            ]
            for category in default_categories:
                cursor.execute(
                    'INSERT OR IGNORE INTO categories (name) VALUES (?)',
                    (category,)
                )
            
            conn.commit()

    def add_inventory_items(self, items: List[Dict]) -> bool:
        """
        Add multiple items to inventory.
        
        Args:
            items: List of dictionaries containing item details
                  Each dict should have: name, type, brand (optional), quantity (optional)
        
        Returns:
            bool: Success status
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                
                for item in items:
                    # Parse quantity into number and unit if possible
                    quantity_number = None
                    unit = None
                    if 'quantity' in item and item['quantity']:
                        try:
                            # Try to extract number and unit from quantity string
                            import re
                            match = re.match(r'(\d+(?:\.\d+)?)\s*(\w+)?', item['quantity'])
                            if match:
                                quantity_number = float(match.group(1))
                                unit = match.group(2)
                        except:
                            pass
                    
                    cursor.execute('''
                        INSERT INTO inventory (
                            name, type, brand, quantity,
                            quantity_number, unit,
                            added_date, last_updated
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        item.get('name', ''),
                        item.get('type', ''),
                        item.get('brand', ''),
                        item.get('quantity', ''),
                        quantity_number,
                        unit,
                        now,
                        now
                    ))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error adding inventory items: {str(e)}")
            return False

    def get_inventory(self) -> List[Dict]:
        """
        Get all inventory items.
        
        Returns:
            List[Dict]: List of inventory items
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM inventory ORDER BY name')
                
                items = []
                for row in cursor.fetchall():
                    items.append(dict(row))
                
                return items
                
        except Exception as e:
            print(f"Error getting inventory: {str(e)}")
            return []

    def search_inventory(self, query: str) -> List[Dict]:
        """
        Search inventory items by name or brand.
        
        Args:
            query: Search query string
            
        Returns:
            List[Dict]: Matching inventory items
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM inventory 
                    WHERE name LIKE ? OR brand LIKE ?
                    ORDER BY name
                ''', (f'%{query}%', f'%{query}%'))
                
                items = []
                for row in cursor.fetchall():
                    items.append(dict(row))
                
                return items
                
        except Exception as e:
            print(f"Error searching inventory: {str(e)}")
            return []

    def update_inventory_item(self, item_id: int, updates: Dict) -> bool:
        """
        Update an inventory item.
        
        Args:
            item_id: ID of the item to update
            updates: Dictionary of fields to update
            
        Returns:
            bool: Success status
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Build the update query dynamically
                allowed_fields = {'name', 'type', 'brand', 'quantity', 
                                'quantity_number', 'unit', 'expiry_date'}
                updates = {k: v for k, v in updates.items() if k in allowed_fields}
                
                if not updates:
                    return False
                
                # Add last_updated timestamp
                updates['last_updated'] = datetime.now().isoformat()
                
                query = 'UPDATE inventory SET ' + \
                        ', '.join(f'{k} = ?' for k in updates.keys()) + \
                        ' WHERE id = ?'
                
                values = list(updates.values()) + [item_id]
                cursor.execute(query, values)
                conn.commit()
                
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error updating inventory item: {str(e)}")
            return False

    def delete_inventory_item(self, item_id: int) -> bool:
        """
        Delete an inventory item.
        
        Args:
            item_id: ID of the item to delete
            
        Returns:
            bool: Success status
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM inventory WHERE id = ?', (item_id,))
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error deleting inventory item: {str(e)}")
            return False 

    def save_recipe(self, recipe_data: Dict) -> int:
        """
        Save a recipe to the database.
        
        Args:
            recipe_data: Dictionary containing recipe information
            
        Returns:
            int: ID of the saved recipe
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                
                # Insert recipe
                cursor.execute('''
                    INSERT INTO saved_recipes (
                        name, difficulty, instructions, chef_tips,
                        added_date, last_cooked, rating, notes
                    ) VALUES (?, ?, ?, ?, ?, NULL, NULL, NULL)
                ''', (
                    recipe_data['name'],
                    recipe_data['difficulty'],
                    json.dumps(recipe_data['instructions']),
                    json.dumps(recipe_data['chef_tips']),
                    now
                ))
                
                recipe_id = cursor.lastrowid
                
                # Insert ingredients
                for ingredient in recipe_data.get('have_ingredients', []):
                    cursor.execute('''
                        INSERT INTO recipe_ingredients (
                            recipe_id, name, quantity, optional
                        ) VALUES (?, ?, ?, 0)
                    ''', (recipe_id, ingredient, None))
                
                for ingredient in recipe_data.get('need_ingredients', []):
                    cursor.execute('''
                        INSERT INTO recipe_ingredients (
                            recipe_id, name, quantity, optional
                        ) VALUES (?, ?, ?, 0)
                    ''', (recipe_id, ingredient, None))
                
                conn.commit()
                return recipe_id
                
        except Exception as e:
            print(f"Error saving recipe: {str(e)}")
            return None

    def get_saved_recipes(self) -> List[Dict]:
        """Get all saved recipes."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get recipes
                cursor.execute('''
                    SELECT id, name, difficulty, instructions, chef_tips,
                           added_date, last_cooked, rating, notes
                    FROM saved_recipes
                    ORDER BY name
                ''')
                
                recipes = []
                for row in cursor.fetchall():
                    recipe = dict(row)
                    
                    # Get ingredients
                    cursor.execute('''
                        SELECT name, quantity, optional
                        FROM recipe_ingredients
                        WHERE recipe_id = ?
                    ''', (recipe['id'],))
                    
                    recipe['ingredients'] = [dict(row) for row in cursor.fetchall()]
                    
                    # Parse JSON fields
                    recipe['instructions'] = json.loads(recipe['instructions'])
                    recipe['chef_tips'] = json.loads(recipe['chef_tips'])
                    
                    recipes.append(recipe)
                
                return recipes
                
        except Exception as e:
            print(f"Error getting recipes: {str(e)}")
            return []

    def create_shopping_list(self, name: str, recipe_ids: List[int]) -> int:
        """
        Create a shopping list from selected recipes.
        
        Args:
            name: Name of the shopping list
            recipe_ids: List of recipe IDs to include
            
        Returns:
            int: ID of the created shopping list
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                
                # Create shopping list
                cursor.execute('''
                    INSERT INTO shopping_lists (name, created_date, status)
                    VALUES (?, ?, 'active')
                ''', (name, now))
                
                list_id = cursor.lastrowid
                
                # Add items from recipes
                for recipe_id in recipe_ids:
                    cursor.execute('''
                        SELECT name, quantity
                        FROM recipe_ingredients
                        WHERE recipe_id = ?
                    ''', (recipe_id,))
                    
                    for row in cursor.fetchall():
                        cursor.execute('''
                            INSERT INTO shopping_list_items (
                                list_id, name, quantity, recipe_id, checked
                            ) VALUES (?, ?, ?, ?, 0)
                        ''', (list_id, row['name'], row['quantity'], recipe_id))
                
                conn.commit()
                return list_id
                
        except Exception as e:
            print(f"Error creating shopping list: {str(e)}")
            return None

    def get_shopping_list(self, list_id: int) -> Dict:
        """Get a shopping list by ID."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get shopping list
                cursor.execute('''
                    SELECT id, name, created_date, status
                    FROM shopping_lists
                    WHERE id = ?
                ''', (list_id,))
                
                shopping_list = dict(cursor.fetchone())
                
                # Get items
                cursor.execute('''
                    SELECT name, quantity, recipe_id, checked
                    FROM shopping_list_items
                    WHERE list_id = ?
                    ORDER BY name
                ''', (list_id,))
                
                shopping_list['items'] = [dict(row) for row in cursor.fetchall()]
                return shopping_list
                
        except Exception as e:
            print(f"Error getting shopping list: {str(e)}")
            return None

    def get_shopping_lists(self) -> List[Dict]:
        """Get all shopping lists."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, name, created_date, status
                    FROM shopping_lists
                    ORDER BY created_date DESC
                ''')
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting shopping lists: {str(e)}")
            return []

    def get_shopping_list(self, list_id: int) -> Optional[Dict]:
        """Get a specific shopping list with its items."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get list info
                cursor.execute('''
                    SELECT id, name, created_date, status
                    FROM shopping_lists
                    WHERE id = ?
                ''', (list_id,))
                
                list_info = cursor.fetchone()
                if not list_info:
                    return None
                
                shopping_list = dict(list_info)
                
                # Get items
                cursor.execute('''
                    SELECT id, name, quantity, recipe_id, checked
                    FROM shopping_list_items
                    WHERE list_id = ?
                    ORDER BY recipe_id, name
                ''', (list_id,))
                
                shopping_list['items'] = [dict(row) for row in cursor.fetchall()]
                return shopping_list
                
        except Exception as e:
            print(f"Error getting shopping list: {str(e)}")
            return None

    def toggle_shopping_list_item(self, item_id: int) -> bool:
        """Toggle the checked status of a shopping list item."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Toggle the checked status
                cursor.execute('''
                    UPDATE shopping_list_items
                    SET checked = NOT checked
                    WHERE id = ?
                ''', (item_id,))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error toggling shopping list item: {str(e)}")
            return False

    def update_shopping_list_item(self, item_id: int, updates: Dict) -> bool:
        """Update a shopping list item."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Build update query
                update_fields = []
                values = []
                for field, value in updates.items():
                    if field in ['quantity', 'checked']:
                        update_fields.append(f"{field} = ?")
                        values.append(value)
                
                if not update_fields:
                    return False
                
                values.append(item_id)
                
                # Update the item
                cursor.execute(f'''
                    UPDATE shopping_list_items
                    SET {", ".join(update_fields)}
                    WHERE id = ?
                ''', values)
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error updating shopping list item: {str(e)}")
            return False

    def update_shopping_list_status(self, list_id: int, status: str) -> bool:
        """Update the status of a shopping list."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE shopping_lists
                    SET status = ?
                    WHERE id = ?
                ''', (status, list_id))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error updating shopping list status: {str(e)}")
            return False

    def delete_shopping_list(self, list_id: int) -> bool:
        """Delete a shopping list and its items."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Delete items first (due to foreign key constraint)
                cursor.execute('''
                    DELETE FROM shopping_list_items
                    WHERE list_id = ?
                ''', (list_id,))
                
                # Delete the list
                cursor.execute('''
                    DELETE FROM shopping_lists
                    WHERE id = ?
                ''', (list_id,))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error deleting shopping list: {str(e)}")
            return False

    def add_shopping_list_item(self, list_id: int, item: Dict) -> bool:
        """Add a new item to a shopping list."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO shopping_list_items (
                        list_id, name, quantity, recipe_id, checked
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (
                    list_id,
                    item['name'],
                    item.get('quantity'),
                    item.get('recipe_id'),
                    item.get('checked', False)
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error adding shopping list item: {str(e)}")
            return False

    def delete_shopping_list_item(self, item_id: int) -> bool:
        """Delete an item from a shopping list."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM shopping_list_items
                    WHERE id = ?
                ''', (item_id,))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error deleting shopping list item: {str(e)}")
            return False