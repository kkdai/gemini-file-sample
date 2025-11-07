#!/usr/bin/env python3
"""Test script for listing documents in a file search store"""

import requests
import os
import sys

# Configuration
BASE_URL = 'http://localhost:3000'
API_KEY = os.environ.get('GEMINI_API_KEY')

if not API_KEY:
    print("Error: GEMINI_API_KEY environment variable not set")
    print("Please set it with: export GEMINI_API_KEY='your-api-key'")
    sys.exit(1)

def test_list_stores():
    """Test listing all file search stores"""
    print("\n" + "=" * 60)
    print("Testing: List all file search stores")
    print("=" * 60)

    try:
        response = requests.get(
            f'{BASE_URL}/api/list-stores',
            headers={'X-API-Key': API_KEY}
        )
        response.raise_for_status()
        data = response.json()

        if data['success']:
            print(f"✅ SUCCESS: Found {len(data['stores'])} store(s)")
            for store in data['stores']:
                print(f"\n  Store: {store['name']}")
                print(f"  Display Name: {store['display_name']}")
                print(f"  Created: {store['create_time']}")
            return data['stores']
        else:
            print(f"❌ FAILED: {data.get('error', 'Unknown error')}")
            return []
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return []

def test_list_documents(store_name):
    """Test listing documents in a file search store"""
    print("\n" + "=" * 60)
    print(f"Testing: List documents in store")
    print(f"Store: {store_name}")
    print("=" * 60)

    try:
        response = requests.get(
            f'{BASE_URL}/api/list-documents',
            headers={'X-API-Key': API_KEY},
            params={'store_name': store_name}
        )
        response.raise_for_status()
        data = response.json()

        if data['success']:
            print(f"✅ SUCCESS: Found {data['count']} document(s)")
            for doc in data['documents']:
                print(f"\n  Document: {doc['name']}")
                print(f"  Display Name: {doc['display_name']}")
                print(f"  Created: {doc['create_time']}")
                print(f"  Updated: {doc['update_time']}")
            return True
        else:
            print(f"❌ FAILED: {data.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

def test_list_documents_invalid_store():
    """Test listing documents with invalid store name"""
    print("\n" + "=" * 60)
    print("Testing: List documents with invalid store name")
    print("=" * 60)

    try:
        response = requests.get(
            f'{BASE_URL}/api/list-documents',
            headers={'X-API-Key': API_KEY},
            params={'store_name': 'fileSearchStores/invalid-store-name-12345'}
        )

        data = response.json()

        # We expect this to fail or return empty
        if not data['success'] or data['count'] == 0:
            print("✅ SUCCESS: Properly handled invalid store name")
            return True
        else:
            print("⚠️  WARNING: Got unexpected success with invalid store")
            return False
    except Exception as e:
        print(f"✅ SUCCESS: Got expected error: {e}")
        return True

def test_list_documents_missing_param():
    """Test listing documents without store_name parameter"""
    print("\n" + "=" * 60)
    print("Testing: List documents without store_name parameter")
    print("=" * 60)

    try:
        response = requests.get(
            f'{BASE_URL}/api/list-documents',
            headers={'X-API-Key': API_KEY}
        )

        data = response.json()

        if not data['success'] and 'required' in data.get('error', '').lower():
            print("✅ SUCCESS: Properly rejected request without store_name")
            return True
        else:
            print("❌ FAILED: Should have rejected request without store_name")
            return False
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Starting File Search Store Document Listing Tests")
    print("=" * 60)

    results = []

    # Test 1: List all stores
    stores = test_list_stores()

    # Test 2: List documents in each store
    if stores:
        for store in stores:
            result = test_list_documents(store['name'])
            results.append(result)
    else:
        print("\n⚠️  No stores found. Cannot test document listing.")
        print("Please create a store and upload some files first.")

    # Test 3: Invalid store name
    results.append(test_list_documents_invalid_store())

    # Test 4: Missing parameter
    results.append(test_list_documents_missing_param())

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
