import os
import base64
import requests # type: ignore
import json
from openai import OpenAI
from dotenv import load_dotenv
from typing import Union, List, Dict, Optional, Tuple
from urllib.parse import urlparse

# Load environment variables from .env file
load_dotenv()

class GrokAPI:
    def __init__(self, api_key: Optional[str] = None, imgbb_api_key: Optional[str] = None):
        """
        Initialize the Grok API client.
        
        Args:
            api_key (str, optional): XAI API key. If not provided, will try to get from environment.
            imgbb_api_key (str, optional): ImgBB API key. If not provided, will try to get from environment.
        """
        self.api_key = api_key or os.getenv("XAI_API_KEY")
        self.imgbb_api_key = imgbb_api_key or os.getenv("IMGBB_API_KEY")
        
        if not self.api_key:
            raise ValueError("XAI_API_KEY not provided and not found in environment variables")
        if not self.imgbb_api_key:
            raise ValueError("IMGBB_API_KEY not provided and not found in environment variables")
        
        self.base_url = "https://api.x.ai/v1"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Initialize OpenAI client for vision API
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    def is_url(self, string: str) -> bool:
        """
        Check if a string is a valid URL.
        
        Args:
            string (str): String to check
            
        Returns:
            bool: True if string is a valid URL, False otherwise
        """
        try:
            result = urlparse(string)
            return all([result.scheme, result.netloc])
        except:
            return False

    def get_direct_image_url(self, url: str) -> str:
        """
        Convert various image sharing URLs to direct image URLs.
        
        Args:
            url (str): Original URL
            
        Returns:
            str: Direct image URL
        """
        # Handle ImgBB sharing URLs
        if "ibb.co" in url:
            try:
                # Get the page content
                response = requests.get(url)
                response.raise_for_status()
                
                # Look for the direct image URL in meta tags
                from bs4 import BeautifulSoup # type: ignore
                soup = BeautifulSoup(response.text, 'html.parser')
                meta_tag = soup.find('meta', property='og:image')
                
                if meta_tag and meta_tag.get('content'):
                    return meta_tag['content']
            except Exception as e:
                print(f"Warning: Could not convert ImgBB URL: {str(e)}")
        
        # Add more image sharing services here as needed
        
        # Return original URL if no conversion needed
        return url

    def upload_image(self, image_path: str) -> str:
        """
        Upload an image to ImgBB and return the URL.
        
        Args:
            image_path (str): Path to the local image file
            
        Returns:
            str: URL of the uploaded image
        """
        imgbb_url = "https://api.imgbb.com/1/upload"
        
        try:
            with open(image_path, "rb") as file:
                # Read and encode the image
                image_data = base64.b64encode(file.read()).decode('utf-8')
                
                # Prepare the payload
                payload = {
                    "key": self.imgbb_api_key,
                    "image": image_data,
                    "name": os.path.basename(image_path)
                }
                
                # Upload to ImgBB
                response = requests.post(imgbb_url, data=payload)
                
                if response.status_code != 200:
                    print(f"Error response from ImgBB: {response.text}")
                    raise Exception(f"ImgBB API returned status code {response.status_code}")
                
                # Get the direct image URL
                result = response.json()
                if "data" not in result or "url" not in result["data"]:
                    raise Exception("Unexpected response format from ImgBB")
                
                image_url = result["data"]["url"]
                print(f"Image uploaded successfully! URL: {image_url}")
                return image_url
                
        except Exception as e:
            print(f"Failed to upload image: {str(e)}")
            raise Exception(f"Failed to upload image: {str(e)}")

    def analyze_food_image(
        self,
        image_source: str,
        extract_keywords: bool = True
    ) -> Tuple[bool, List[str], str]:
        """
        Analyze an image specifically for food content and extract keywords.
        
        Args:
            image_source (str): Path to local image file or URL
            extract_keywords (bool): Whether to extract keywords from the description
            
        Returns:
            Tuple[bool, List[str], str]: (contains_food, keywords, full_description)
        """
        try:
            # Check if the source is a URL or local file
            if self.is_url(image_source):
                # Convert to direct image URL if needed
                image_url = self.get_direct_image_url(image_source)
                print(f"Using image URL: {image_url}")
            else:
                # Upload local file
                image_url = self.upload_image(image_source)
            
            # Prepare a specific prompt for food detection
            prompt = """Analyze this image for ANY food or beverage items, including:
1. Fresh food and prepared dishes
2. Packaged foods and snacks
3. Canned goods and preserved foods
4. Beverages (both alcoholic and non-alcoholic)
5. Condiments and sauces
6. Ingredients and raw food items

For each item found:
- List the specific item name
- Include brand names if visible
- Specify if it's packaged/canned/fresh
- Note the quantity if obvious

If there is no food or beverage items in the image, state "No food or beverage items detected."

Format your response as JSON with the following structure:
{
    "contains_food": true/false,
    "food_items": [
        {
            "name": "item name",
            "type": "packaged/canned/fresh/beverage",
            "brand": "brand name if visible",
            "quantity": "quantity if visible"
        }
    ],
    "description": "detailed description of all items and their arrangement"
}"""

            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url,
                                "detail": "high",
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt,
                        },
                    ],
                },
            ]

            # Get the response
            response = self.client.chat.completions.create(
                model="grok-vision-beta",
                messages=messages,
                temperature=0.01,
                stream=False
            )

            # Extract the response text
            response_text = response.choices[0].message.content

            try:
                # Try to parse the response as JSON
                result = json.loads(response_text)
                contains_food = result.get("contains_food", False)
                food_items = result.get("food_items", [])
                description = result.get("description", "")

                # Print the results in a formatted way
                print("\nFood Analysis Results:")
                print("-" * 50)
                print(f"Contains food items: {'Yes' if contains_food else 'No'}")
                
                if contains_food and food_items:
                    print("\nItems detected:")
                    print("-" * 50)
                    for item in food_items:
                        print(f"\nItem: {item.get('name', 'Unknown')}")
                        if item.get('type'):
                            print(f"Type: {item['type']}")
                        if item.get('brand'):
                            print(f"Brand: {item['brand']}")
                        if item.get('quantity'):
                            print(f"Quantity: {item['quantity']}")
                
                print("\nDetailed description:")
                print("-" * 50)
                print(description)
                print("-" * 50)

                # Create a simple list of item names for the return value
                item_names = [item.get('name', '') for item in food_items]
                return contains_food, item_names, description

            except json.JSONDecodeError:
                # If JSON parsing fails, return the raw response
                print("\nFood Analysis Results:")
                print("-" * 20)
                print(response_text)
                print("-" * 20)
                return False, [], response_text

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return False, [], str(e)

if __name__ == "__main__":
    # Example usage
    grok = GrokAPI()
    
    # You can use either a local file path or a URL
    # Uncomment the one you want to use:
    
    # For local file:
    # image_source = r"C:\Users\Micke\Pictures\image (2).jpg"
    
    # For URL:
    image_source = r"C:\Users\Micke\Downloads\image (3).jpg"
    
    # Analyze the image
    contains_food, food_items, description = grok.analyze_food_image(image_source)
    
    # If food was found, print the keywords
    if contains_food:
        print("\nKeywords for database:")
        print(", ".join(food_items))