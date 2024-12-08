import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def analyze_image(image_url: str, prompt: str = "What's funny about this image?"):
    """
    Analyze an image using the Grok Vision API.
    
    Args:
        image_url (str): URL of the image to analyze
        prompt (str): Question to ask about the image
        
    Returns:
        None: Prints the response stream
    """
    # Get API key from environment variables
    xai_api_key = os.getenv("XAI_API_KEY")
    if not xai_api_key:
        raise ValueError("XAI_API_KEY environment variable is not set")

    # Initialize the client
    client = OpenAI(
        api_key=xai_api_key,
        base_url="https://api.x.ai/v1",
    )

    # Prepare the messages
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

    try:
        # Create the completion stream
        stream = client.chat.completions.create(
            model="grok-vision-beta",
            messages=messages,
            stream=True,
            temperature=0.01,
        )

        # Process the stream
        print("\nGrok Vision Response:")
        print("-" * 20)
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="", flush=True)
        print("\n" + "-" * 20)

    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    # Example usage
    test_image_url = "YOUR_IMAGE_URL_HERE"
    analyze_image(test_image_url) 