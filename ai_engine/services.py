import os
import base64
import json
from openai import OpenAI
from django.conf import settings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq Client
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def encode_image(image_file):
    """Utility to encode a Django UploadedFile to base64."""
    return base64.b64encode(image_file.read()).decode('utf-8')

def generate_description_from_text(name, category, keywords, product_type):
    """
    Generate professional product title and description using Groq Llama 3.1.
    """
    prompt = f"""Generate a professional marketplace listing for:
    Product Name: {name}
    Category: {category}
    Keywords: {keywords}
    Type: {product_type}
    
    Return the response ONLY as a JSON object with two fields: 'title' and 'description'.
    Example format: {{"title": "...", "description": "..."}}
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Groq Text Error: {e}")
        return {"title": name, "description": f"A high-quality {category} product."}

def generate_description_from_image(image_file, name, category, keywords, price, product_type):
    """
    Generate professional product title and description using Groq Llama 3.2 Vision.
    Analyzes the image to provide more accurate details.
    """
    try:
        base64_image = encode_image(image_file)
        
        prompt = f"""Analyze this product image and metadata:
        Provided Name: {name}
        Category: {category}
        Keywords: {keywords}
        Type: {product_type}
        Price Hint: {price}
        
        Create a professional and persuasive marketplace title and description based on the visual contents and metadata.
        Return the response ONLY as a JSON object with two fields: 'title' and 'description'.
        Example format: {{"title": "...", "description": "..."}}
        """

        response = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Groq Vision Error: {e}")
        # Fallback to text mode if vision fails or image is empty
        return generate_description_from_text(name, category, keywords, product_type)
