#!/usr/bin/env python3
"""Test script to validate Eden AI API."""

import requests
import json

EDENAI_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMWE3NzRlZTgtMTJiZS00OGFiLWFlOTgtYzg4YjEzN2IxYjcxIiwidHlwZSI6ImFwaV90b2tlbiJ9.K3b3goz-yYmjnr32IviXOWa2JaT0Xu8cG6CO6AOdrbY"

url = "https://api.edenai.run/v2/text/embeddings"

headers = {
    "Authorization": f"Bearer {EDENAI_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "providers": "cohere",
    "texts": ["This is a test sentence"],
    "settings": {
        "cohere": "embed-english-v3.0"
    }
}

print("Testing Eden AI API...")
print(f"URL: {url}")
print(f"API Key: {EDENAI_API_KEY[:20]}...")
print("\nSending request...")

try:
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ API is VALID!")
        print("\nResponse structure:")
        print(json.dumps(result, indent=2)[:500])  # Print first 500 chars
        
        # Check if embedding is present
        if 'cohere' in result and 'items' in result['cohere']:
            embedding = result['cohere']['items'][0]['embedding']
            print(f"\n✅ Embedding generated successfully!")
            print(f"Embedding dimension: {len(embedding)}")
            print(f"First 5 values: {embedding[:5]}")
        else:
            print("\n❌ Unexpected response structure")
            print(f"Full response: {json.dumps(result, indent=2)}")
    else:
        print(f"\n❌ API Error!")
        print(f"Response: {response.text}")
        
except requests.exceptions.Timeout:
    print("\n❌ Request timed out")
except requests.exceptions.RequestException as e:
    print(f"\n❌ Request failed: {str(e)}")
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
