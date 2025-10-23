#!/usr/bin/env python3
"""
Test script for debugging knowledge endpoint issues
"""
import requests
import json
import time

# Test configuration
BASE_URL = "http://localhost:8000"
ENDPOINT = "/api/knowledge/query"

def test_knowledge_query():
    """Test the simplified knowledge query endpoint"""
    print("=== Testing Debug Knowledge Query Endpoint ===")
    
    # Test data
    test_data = {
        "question": "讲一下Deepseekv3.2的特点",
        "mode": "hybrid",
        "model": "moonshotai/Kimi-K2-Instruct-0905"
    }
    
    params = {
        "space_name": "test"
    }
    
    try:
        print(f"Making POST request to: {BASE_URL}{ENDPOINT}")
        print(f"Data: {json.dumps(test_data, indent=2)}")
        print(f"Params: {params}")
        
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            json=test_data,
            params=params,
            timeout=10  # 10 second timeout to match frontend
        )
        
        elapsed_time = time.time() - start_time
        print(f"Request completed in {elapsed_time:.2f} seconds")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS - Response received:")
            print(f"  Question: {result.get('question', 'N/A')}")
            print(f"  Answer length: {len(result.get('answer', ''))}")
            print(f"  Mode: {result.get('mode', 'N/A')}")
            print(f"  Sources: {result.get('sources', [])}")
            print(f"  Answer preview: {result.get('answer', '')[:200]}...")
            return True
        else:
            print(f"❌ FAILED - HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        elapsed_time = time.time() - start_time
        print(f"❌ TIMEOUT after {elapsed_time:.2f} seconds")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ CONNECTION ERROR: {e}")
        print("Make sure the backend server is running on http://localhost:8000")
        return False
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"❌ ERROR after {elapsed_time:.2f} seconds: {e}")
        return False

def test_knowledge_status():
    """Test the knowledge status endpoint"""
    print("\n=== Testing Knowledge Status Endpoint ===")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/knowledge/status",
            params={"space_name": "test"},
            timeout=5
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Status endpoint working:")
            print(f"  Available: {result.get('available', 'N/A')}")
            print(f"  Space: {result.get('space_name', 'N/A')}")
            print(f"  Message: {result.get('message', 'N/A')}")
            return True
        else:
            print(f"❌ Status endpoint failed - HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Status endpoint error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Testing Debug Knowledge Endpoints")
    print("=" * 50)
    
    # Test status first
    status_ok = test_knowledge_status()
    
    # Test query
    query_ok = test_knowledge_query()
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"  Status endpoint: {'✅ OK' if status_ok else '❌ FAILED'}")
    print(f"  Query endpoint:  {'✅ OK' if query_ok else '❌ FAILED'}")
    
    if query_ok and status_ok:
        print("🎉 All tests passed! The debug endpoint is working.")
    else:
        print("⚠️  Some tests failed. Check the backend server logs.")