import os
import base64
import requests # type: ignore
import json
from openai import OpenAI
from dotenv import load_dotenv
from typing import Union, List, Dict, Optional, Tuple
from urllib.parse import urlparse
from bs4 import BeautifulSoup # type: ignore

# Load environment variables from .env file
load_dotenv()

class GrokAPI:
    def __init__(self, api_key: Optional[str] = None, imgbb_api_key: Optional[str] = None):
        """Initialize the Grok API client."""
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
        """Check if a string is a valid URL."""
        try:
            result = urlparse(string)
            return all([result.scheme, result.netloc])
        except:
            return False

    def get_direct_image_url(self, url: str) -> str:
        """Convert various image sharing URLs to direct image URLs."""
        # Handle ImgBB sharing URLs
        if "ibb.co" in url:
            try:
                response = requests.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                meta_tag = soup.find('meta', property='og:image')
                
                if meta_tag and meta_tag.get('content'):
                    return meta_tag['content']
            except Exception as e:
                print(f"Warning: Could not convert ImgBB URL: {str(e)}")
        
        return url

    def upload_image(self, image_path: str) -> str:
        """Upload an image to ImgBB and return the URL."""
        imgbb_url = "https://api.imgbb.com/1/upload"
        
        try:
            with open(image_path, "rb") as file:
                image_data = base64.b64encode(file.read()).decode('utf-8')
                
                payload = {
                    "key": self.imgbb_api_key,
                    "image": image_data,
                    "name": os.path.basename(image_path)
                }
                
                response = requests.post(imgbb_url, data=payload)
                
                if response.status_code != 200:
                    print(f"Error response from ImgBB: {response.text}")
                    raise Exception(f"ImgBB API returned status code {response.status_code}")
                
                result = response.json()
                if "data" not in result or "url" not in result["data"]:
                    raise Exception("Unexpected response format from ImgBB")
                
                image_url = result["data"]["url"]
                print(f"Image uploaded successfully! URL: {image_url}")
                return image_url
                
        except Exception as e:
            print(f"Failed to upload image: {str(e)}")
            raise

    def analyze_food_image(self, image_source: str) -> Tuple[bool, List[Dict], str]:
        """Analyze an image for food content and extract details."""
        try:
            # Check if the source is a URL or local file
            if self.is_url(image_source):
                image_url = self.get_direct_image_url(image_source)
                print(f"Using image URL: {image_url}")
            else:
                image_url = self.upload_image(image_source)
            
            # Prepare the specific prompt for food detection
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

            # Extract and parse the response
            response_text = response.choices[0].message.content
            try:
                # Check if the response contains JSON (even within markdown code blocks)
                if '{' in response_text and '}' in response_text:
                    # Extract JSON part
                    start = response_text.find('{')
                    end = response_text.rfind('}') + 1
                    json_text = response_text[start:end]
                    
                    # Parse JSON
                    result = json.loads(json_text)
                else:
                    print("No valid JSON found in response")
                    return False, [], response_text

                contains_food = result.get("contains_food", False)
                food_items = result.get("food_items", [])
                description = result.get("description", "")

                # Clean up food items
                cleaned_items = []
                for item in food_items:
                    if isinstance(item, dict) and 'name' in item:
                        # Ensure all required fields exist
                        cleaned_item = {
                            'name': item.get('name', '').strip(),
                            'type': item.get('type', 'uncategorized').strip(),
                            'brand': item.get('brand', '').strip(),
                            'quantity': item.get('quantity', '').strip()
                        }
                        cleaned_items.append(cleaned_item)

                # Print the results
                print("\nFood Analysis Results:")
                print("-" * 50)
                print(f"Contains food items: {'Yes' if contains_food else 'No'}")
                
                if contains_food and cleaned_items:
                    print(f"\nFound {len(cleaned_items)} items:")
                    print("-" * 50)
                    for item in cleaned_items:
                        print(f"\nItem: {item['name']}")
                        print(f"Type: {item['type']}")
                        if item['brand'] and item['brand'].lower() != 'unknown':
                            print(f"Brand: {item['brand']}")
                        if item['quantity']:
                            print(f"Quantity: {item['quantity']}")
                
                print("\nDetailed description:")
                print("-" * 50)
                print(description)
                print("-" * 50)

                return contains_food, cleaned_items, description

            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {str(e)}")
                print("Raw response:", response_text)
                return False, [], response_text
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                return False, [], str(e)

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return False, [], str(e) 