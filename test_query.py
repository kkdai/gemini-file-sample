#!/usr/bin/env python3
"""Test script to find the correct way to use file search with generate_content"""

from google import genai
from google.genai import types
import os

# Get API key from environment or prompt
api_key = os.environ.get('GEMINI_API_KEY')
if not api_key:
    api_key = input("Please enter your GEMINI_API_KEY: ").strip()
    if not api_key:
        print("API key is required")
        exit(1)

client = genai.Client(api_key=api_key)

# Use your existing store
store_name = 'fileSearchStores/filetest1-w3acmokds7ka'
query_text = "幫我整理檔案內容摘要給我"

print("=" * 60)
print("Testing different approaches to use file_search with generate_content")
print("=" * 60)

# Approach 1: Using Tool with file_search parameter
print("\n[Approach 1] Using types.Tool(file_search=...)")
try:
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=query_text,
        config=types.GenerateContentConfig(
            tools=[
                types.Tool(
                    file_search=types.FileSearch(
                        file_search_store_names=[store_name]
                    )
                )
            ]
        )
    )
    print(f"✅ SUCCESS! Response: {response.text[:200]}...")
except Exception as e:
    print(f"❌ FAILED: {e}")

# Approach 2: Using FileSearch directly in tools list
print("\n[Approach 2] Using types.FileSearch() directly in tools")
try:
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=query_text,
        config=types.GenerateContentConfig(
            tools=[
                types.FileSearch(
                    file_search_store_names=[store_name]
                )
            ]
        )
    )
    print(f"✅ SUCCESS! Response: {response.text[:200]}...")
except Exception as e:
    print(f"❌ FAILED: {e}")

# Approach 3: Using dictionary
print("\n[Approach 3] Using dictionary format")
try:
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=query_text,
        config=types.GenerateContentConfig(
            tools=[
                {
                    'file_search': {
                        'file_search_store_names': [store_name]
                    }
                }
            ]
        )
    )
    print(f"✅ SUCCESS! Response: {response.text[:200]}...")
except Exception as e:
    print(f"❌ FAILED: {e}")

# Approach 4: Creating Tool with dictionary
print("\n[Approach 4] Using types.Tool with dict parameter")
try:
    tool_dict = {'file_search': types.FileSearch(file_search_store_names=[store_name])}
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=query_text,
        config=types.GenerateContentConfig(tools=[types.Tool(**tool_dict)])
    )
    print(f"✅ SUCCESS! Response: {response.text[:200]}...")
except Exception as e:
    print(f"❌ FAILED: {e}")

print("\n" + "=" * 60)
print("Test completed")
print("=" * 60)
