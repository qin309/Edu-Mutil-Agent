#!/usr/bin/env python3
"""
Test script to verify knowledge endpoint functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import httpx

async def test_knowledge_endpoints():
    """Test if the knowledge endpoints work correctly"""
    
    print("Testing knowledge endpoints...")
    
    base_url = "http://localhost:8000"
    
    # Test endpoints to check
    endpoints_to_test = [
        ("GET", "/api/knowledge/status", None, "Knowledge status"),
        ("GET", "/api/knowledge/spaces", None, "Knowledge spaces list"),
        ("GET", "/api/knowledge/documents?space_name=test", None, "Documents list"),
        ("POST", "/api/knowledge/query?space_name=test", {
            "question": "讲一下Deepseekv3.2的特点",
            "mode": "hybrid",
            "model": "moonshotai/Kimi-K2-Instruct-0905"
        }, "Knowledge query")
    ]
    
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            for method, endpoint, data, description in endpoints_to_test:
                print(f"\n📝 Testing {description}: {method} {endpoint}")
                
                try:
                    if method == "GET":
                        response = await client.get(f"{base_url}{endpoint}")
                    elif method == "POST":
                        response = await client.post(
                            f"{base_url}{endpoint}",
                            json=data,
                            headers={"Content-Type": "application/json"}
                        )
                    
                    print(f"Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        print(f"✅ SUCCESS!")
                        if len(response.text) > 200:
                            print(f"Response preview: {response.text[:200]}...")
                        else:
                            print(f"Response: {response.text}")
                    elif response.status_code == 401:
                        print(f"🔒 AUTHENTICATION ERROR: {response.status_code}")
                        print("This endpoint requires authentication")
                    elif response.status_code == 500:
                        print(f"❌ SERVER ERROR: {response.status_code}")
                        print(f"Response: {response.text}")
                    else:
                        print(f"⚠️ UNEXPECTED STATUS: {response.status_code}")
                        print(f"Response: {response.text}")
                        
                except httpx.ConnectError:
                    print("❌ CONNECTION ERROR: Cannot connect to backend")
                except httpx.ReadTimeout:
                    print("⏰ TIMEOUT ERROR: Request took too long")
                except Exception as e:
                    print(f"❌ ERROR: {e}")
                
                print("-" * 60)
                
    except Exception as e:
        print(f"❌ GENERAL ERROR: {e}")

async def test_basic_connectivity():
    """Test basic backend connectivity"""
    print("Testing basic backend connectivity...")
    
    base_url = "http://localhost:8000"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{base_url}/")
            print(f"Root endpoint status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Backend is responding")
                return True
            else:
                print("❌ Backend returned unexpected status")
                return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Knowledge Endpoint Functionality")
    print("=" * 60)
    
    # First test basic connectivity
    connectivity_ok = asyncio.run(test_basic_connectivity())
    
    if connectivity_ok:
        print("\n" + "=" * 60)
        print("Testing Knowledge Endpoints")
        print("=" * 60)
        asyncio.run(test_knowledge_endpoints())
    else:
        print("\n❌ Cannot proceed with knowledge endpoint tests - backend not responding")
        print("Please ensure the backend server is running with: python main.py")