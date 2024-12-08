from typing import Dict, List, Optional

class FoodCategories:
    # Main categories with descriptions
    CATEGORIES = {
        # Fresh produce and ingredients
        'fresh_fruits': 'Fresh fruits and berries',
        'fresh_vegetables': 'Fresh vegetables and greens',
        'fresh_herbs': 'Fresh herbs and aromatics',
        'fresh_meat': 'Fresh uncooked meat and poultry',
        'fresh_seafood': 'Fresh fish and seafood',
        'fresh_dairy': 'Fresh milk, cheese, and dairy products',
        
        # Frozen foods
        'frozen_produce': 'Frozen fruits and vegetables',
        'frozen_meat': 'Frozen meat and poultry',
        'frozen_seafood': 'Frozen fish and seafood',
        'frozen_meals': 'Frozen ready-to-eat meals',
        'frozen_dessert': 'Ice cream and frozen desserts',
        
        # Pantry items
        'canned': 'Canned and preserved foods',
        'condiment': 'Sauces, oils, spices, and seasonings',
        'dried_herbs': 'Dried herbs and spices',
        'grain': 'Rice, pasta, cereals, and grains',
        'baking': 'Baking ingredients and supplies',
        
        # Prepared foods
        'deli': 'Deli meats, cheeses, and prepared salads',
        'prepared': 'Ready-to-eat dishes and meals',
        'bakery': 'Bread, pastries, and baked goods',
        
        # Snacks and sweets
        'snack': 'Chips, crackers, and savory snacks',
        'sweets': 'Desserts, candies, and sweet treats',
        'nuts': 'Nuts, seeds, and dried fruits',
        
        # Beverages
        'beverage': 'Drinks and beverages',
        'alcohol': 'Alcoholic beverages',
        
        # Special categories
        'organic': 'Certified organic products',
        'gluten_free': 'Gluten-free products',
        'vegan': 'Vegan and plant-based products',
        'international': 'International and ethnic food items',
        'breakfast': 'Breakfast cereals, spreads, and items',
        'baby': 'Baby food and formula',
        'pet': 'Pet food and treats',
        'health': 'Health foods and supplements',
        
        # Other
        'other': 'Miscellaneous food items'
    }

    # Common items and their default categories
    COMMON_ITEMS = {
        # Fresh fruits
        'apple': 'fresh_fruits',
        'banana': 'fresh_fruits',
        'orange': 'fresh_fruits',
        'lemon': 'fresh_fruits',
        'lime': 'fresh_fruits',
        'grape': 'fresh_fruits',
        'strawberry': 'fresh_fruits',
        'blueberry': 'fresh_fruits',
        'raspberry': 'fresh_fruits',
        'blackberry': 'fresh_fruits',
        'pear': 'fresh_fruits',
        'peach': 'fresh_fruits',
        'plum': 'fresh_fruits',
        'mango': 'fresh_fruits',
        'pineapple': 'fresh_fruits',
        'kiwi': 'fresh_fruits',
        'melon': 'fresh_fruits',
        'watermelon': 'fresh_fruits',
        
        # Fresh vegetables
        'lettuce': 'fresh_vegetables',
        'spinach': 'fresh_vegetables',
        'kale': 'fresh_vegetables',
        'carrot': 'fresh_vegetables',
        'potato': 'fresh_vegetables',
        'onion': 'fresh_vegetables',
        'garlic': 'fresh_vegetables',
        'tomato': 'fresh_vegetables',
        'cucumber': 'fresh_vegetables',
        'pepper': 'fresh_vegetables',
        'broccoli': 'fresh_vegetables',
        'cauliflower': 'fresh_vegetables',
        'celery': 'fresh_vegetables',
        'asparagus': 'fresh_vegetables',
        'zucchini': 'fresh_vegetables',
        'eggplant': 'fresh_vegetables',
        'mushroom': 'fresh_vegetables',
        'corn': 'fresh_vegetables',
        'peas': 'fresh_vegetables',
        'green beans': 'fresh_vegetables',
        
        # Fresh meat and seafood
        'chicken': 'fresh_meat',
        'beef': 'fresh_meat',
        'pork': 'fresh_meat',
        'fish': 'fresh_seafood',
        'salmon': 'fresh_seafood',
        'shrimp': 'fresh_seafood',
        
        # Frozen items
        'frozen vegetables': 'frozen_produce',
        'frozen fruit': 'frozen_produce',
        'frozen chicken': 'frozen_meat',
        'frozen fish': 'frozen_seafood',
        'frozen pizza': 'frozen_meals',
        'ice cream': 'frozen_dessert',
        
        # Dairy
        'milk': 'fresh_dairy',
        'cheese': 'fresh_dairy',
        'yogurt': 'fresh_dairy',
        'butter': 'fresh_dairy',
        'eggs': 'fresh_dairy',
        
        # Pantry
        'pasta': 'grain',
        'rice': 'grain',
        'cereal': 'breakfast',
        'bread': 'bakery',
        'flour': 'baking',
        'sugar': 'baking',
        'olive oil': 'condiment',
        'sauce': 'condiment',
        'spices': 'condiment',
        'canned soup': 'canned',
        'canned beans': 'canned',
        'canned tomatoes': 'canned',
        
        # Snacks and sweets
        'chips': 'snack',
        'crackers': 'snack',
        'cookies': 'sweets',
        'candy': 'sweets',
        'chocolate': 'sweets',
        'nuts': 'nuts',
        'dried fruit': 'nuts',
        
        # Beverages
        'juice': 'beverage',
        'soda': 'beverage',
        'water': 'beverage',
        'coffee': 'beverage',
        'tea': 'beverage',
        'wine': 'alcohol',
        'beer': 'alcohol',
        
        # Deli
        'ham': 'deli',
        'turkey': 'deli',
        'deli meat': 'deli',
        'deli cheese': 'deli',
        'potato salad': 'deli',
        
        # International
        'sushi': 'international',
        'kimchi': 'international',
        'curry': 'international',
        'salsa': 'international',
        'hummus': 'international'
    }

    # Add common item variations mapping
    ITEM_VARIATIONS = {
        'salt': ['sea salt', 'table salt', 'kosher salt', 'himalayan salt'],
        'sugar': ['white sugar', 'granulated sugar', 'caster sugar'],
        'olive oil': ['extra virgin olive oil', 'evoo'],
        'onion': ['yellow onion', 'white onion', 'red onion'],
        'garlic': ['fresh garlic', 'garlic cloves'],
        'tomato': ['tomatoes', 'cherry tomatoes', 'roma tomatoes'],
        'potato': ['potatoes', 'russet potato', 'sweet potato'],
        'carrot': ['carrots', 'baby carrots'],
        'chicken': ['chicken breast', 'chicken thigh', 'chicken wings'],
        'beef': ['ground beef', 'beef steak', 'beef roast'],
        'rice': ['white rice', 'brown rice', 'jasmine rice', 'basmati rice'],
        'basil': ['fresh basil', 'sweet basil', 'thai basil'],
        'oregano': ['fresh oregano', 'dried oregano'],
        'thyme': ['fresh thyme', 'dried thyme'],
        'rosemary': ['fresh rosemary', 'dried rosemary'],
        'mint': ['fresh mint', 'peppermint', 'spearmint'],
        'cilantro': ['fresh cilantro', 'coriander'],
        'parsley': ['fresh parsley', 'italian parsley', 'flat-leaf parsley'],
        'sage': ['fresh sage', 'dried sage'],
        'dill': ['fresh dill', 'dried dill'],
        'chives': ['fresh chives']
    }

    # Category learning data
    CATEGORY_LEARNING = {}  # Will store {item_name: {category: count}}

    @classmethod
    def get_categories(cls) -> List[str]:
        """Get list of all valid categories."""
        return list(cls.CATEGORIES.keys())

    @classmethod
    def get_category_description(cls, category: str) -> Optional[str]:
        """Get description for a category."""
        return cls.CATEGORIES.get(category.lower())

    @classmethod
    def is_valid_category(cls, category: str) -> bool:
        """Check if a category is valid."""
        return category.lower() in cls.CATEGORIES

    @classmethod
    def normalize_item_name(cls, item_name: str) -> str:
        """Normalize item name to prevent duplicates."""
        item_lower = item_name.lower().strip()
        
        # Check direct variations
        for base_item, variations in cls.ITEM_VARIATIONS.items():
            if item_lower == base_item or item_lower in variations:
                return base_item
        
        # Check if it's a plural form
        if item_lower.endswith('s') and item_lower[:-1] in cls.COMMON_ITEMS:
            return item_lower[:-1]
        
        return item_lower

    @classmethod
    def learn_category(cls, item_name: str, category: str):
        """Learn category association for an item."""
        normalized_name = cls.normalize_item_name(item_name)
        if normalized_name not in cls.CATEGORY_LEARNING:
            cls.CATEGORY_LEARNING[normalized_name] = {}
        
        if category not in cls.CATEGORY_LEARNING[normalized_name]:
            cls.CATEGORY_LEARNING[normalized_name][category] = 0
        
        cls.CATEGORY_LEARNING[normalized_name][category] += 1

    @classmethod
    def suggest_category(cls, item_name: str) -> str:
        """Suggest a category for an item based on its name and learning history."""
        normalized_name = cls.normalize_item_name(item_name)
        item_lower = normalized_name
        
        # Check learning history first
        if normalized_name in cls.CATEGORY_LEARNING:
            categories = cls.CATEGORY_LEARNING[normalized_name]
            if categories:
                # Return most commonly used category
                return max(categories.items(), key=lambda x: x[1])[0]
        
        # Check for herbs
        herb_keywords = ['basil', 'oregano', 'thyme', 'rosemary', 'mint', 'cilantro', 
                        'parsley', 'sage', 'dill', 'chives', 'herb', 'herbs']
        if any(keyword in item_lower for keyword in herb_keywords):
            if 'dried' in item_lower or 'ground' in item_lower:
                return 'dried_herbs'
            if 'fresh' in item_lower or not any(word in item_lower for word in ['dried', 'ground', 'powdered']):
                return 'fresh_herbs'
            return 'dried_herbs'
        
        # Check for fruits
        fruit_keywords = ['apple', 'banana', 'orange', 'berry', 'berries', 'melon', 'fruit',
                         'grape', 'citrus', 'pear', 'peach', 'plum', 'mango', 'pineapple']
        if any(keyword in item_lower for keyword in fruit_keywords):
            if 'frozen' in item_lower:
                return 'frozen_produce'
            return 'fresh_fruits'
        
        # Check for vegetables
        vegetable_keywords = ['lettuce', 'spinach', 'kale', 'carrot', 'potato', 'onion',
                            'garlic', 'tomato', 'cucumber', 'pepper', 'broccoli', 'vegetable',
                            'cauliflower', 'celery', 'asparagus', 'zucchini', 'eggplant',
                            'mushroom', 'corn', 'peas', 'beans', 'greens']
        if any(keyword in item_lower for keyword in vegetable_keywords):
            if 'frozen' in item_lower:
                return 'frozen_produce'
            return 'fresh_vegetables'
        
        # Check for frozen items
        if 'frozen' in item_lower:
            if any(word in item_lower for word in ['chicken', 'beef', 'pork', 'meat']):
                return 'frozen_meat'
            if any(word in item_lower for word in ['fish', 'seafood', 'shrimp']):
                return 'frozen_seafood'
            if 'pizza' in item_lower or 'dinner' in item_lower or 'meal' in item_lower:
                return 'frozen_meals'
            if any(word in item_lower for word in ['ice cream', 'dessert']):
                return 'frozen_dessert'
            return 'frozen_meals'
        
        # Check for fresh items
        if 'fresh' in item_lower:
            if any(word in item_lower for word in ['meat', 'chicken', 'beef', 'pork', 'lamb']):
                return 'fresh_meat'
            if any(word in item_lower for word in ['fish', 'seafood', 'shrimp', 'salmon']):
                return 'fresh_seafood'
            if any(word in item_lower for word in ['milk', 'cheese', 'dairy']):
                return 'fresh_dairy'
        
        # Check exact matches
        if item_lower in cls.COMMON_ITEMS:
            return cls.COMMON_ITEMS[item_lower]
        
        # Check if item name contains any common item keywords
        for common_item, category in cls.COMMON_ITEMS.items():
            if common_item in item_lower:
                return category
        
        # Additional meat keywords
        meat_keywords = ['meat', 'chicken', 'beef', 'pork', 'lamb', 'steak', 'roast', 'chop', 'ground']
        if any(keyword in item_lower for keyword in meat_keywords):
            return 'fresh_meat'
        
        # Default to 'other' if no match found
        return 'other'

    @classmethod
    def format_category(cls, category: str) -> str:
        """Format a category name for display."""
        if not category:
            return 'uncategorized'
        
        category = category.lower()
        if category in cls.CATEGORIES:
            return category
        return 'other' 

    @classmethod
    def get_similar_items(cls, item_name: str) -> List[str]:
        """Get list of similar items to prevent duplicates."""
        normalized_name = cls.normalize_item_name(item_name)
        
        similar_items = []
        # Check variations
        for base_item, variations in cls.ITEM_VARIATIONS.items():
            if normalized_name == base_item or normalized_name in variations:
                similar_items.extend([base_item] + variations)
        
        # Check plurals
        if normalized_name.endswith('s'):
            similar_items.append(normalized_name[:-1])
        else:
            similar_items.append(normalized_name + 's')
        
        return list(set(similar_items))