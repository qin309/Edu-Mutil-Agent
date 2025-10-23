#!/usr/bin/env python3
"""
Test script for the corrected knowledge.py implementation
"""
import requests
import json
import time

# Test configuration
BASE_URL = "http://localhost:8000"
ENDPOINT = "/api/knowledge/query"

def test_knowledge_query_scenarios():
    """Test various knowledge query scenarios"""
    print("=== Testing Corrected Knowledge Query Implementation ===")
    
    test_cases = [
        {
            "name": "Simple Question",
            "data": {
                "question": "What is machine learning?",
                "mode": "hybrid",
            },
            "params": {"space_name": "test"}
        },
        {
            "name": "Chinese Question",
            "data": {
                "question": "讲一下Deepseekv3.2的特点",
                "mode": "hybrid",
                "model": "moonshotai/Kimi-K2-Instruct-0905"
            },
            "params": {"space_name": "test"}
        },
        {
            "name": "Mathematical Question",
            "data": {
                "question": "How do I solve quadratic equations?",
                "mode": "local"
            },
            "params": {"space_name": "default"}
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        print(f"   Question: {test_case['data']['question']}")
        
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{BASE_URL}{ENDPOINT}",
                json=test_case['data'],
                params=test_case['params'],
                timeout=50  # 50 second timeout to allow for LightRAG processing or fallback
            )
            
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ SUCCESS ({elapsed_time:.2f}s)")
                print(f"   Mode: {result.get('mode', 'N/A')}")
                print(f"   Sources: {result.get('sources', [])}")
                print(f"   Answer length: {len(result.get('answer', ''))}")
                print(f"   Answer preview: {result.get('answer', '')[:150]}...")
                
                results.append({
                    "test": test_case['name'],
                    "success": True,
                    "time": elapsed_time,
                    "mode": result.get('mode'),
                    "answer_length": len(result.get('answer', ''))
                })
            else:
                print(f"   ❌ FAILED - HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                results.append({
                    "test": test_case['name'],
                    "success": False,
                    "time": elapsed_time,
                    "error": f"HTTP {response.status_code}"
                })
                
        except requests.exceptions.Timeout:
            elapsed_time = time.time() - start_time
            print(f"   ⚠️  TIMEOUT after {elapsed_time:.2f}s")
            results.append({
                "test": test_case['name'],
                "success": False,
                "time": elapsed_time,
                "error": "Timeout"
            })
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"   ❌ ERROR after {elapsed_time:.2f}s: {e}")
            results.append({
                "test": test_case['name'],
                "success": False,
                "time": elapsed_time,
                "error": str(e)
            })
    
    return results

def test_knowledge_status():
    """Test knowledge status endpoint"""
    print("\n=== Testing Knowledge Status ===")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/knowledge/status",
            params={"space_name": "test"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Status endpoint working:")
            print(f"   Available: {result.get('available', 'N/A')}")
            print(f"   Space: {result.get('space_name', 'N/A')}")
            print(f"   Message: {result.get('message', 'N/A')}")
            return True
        else:
            print(f"❌ Status failed - HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Status error: {e}")
        return False

def main():
    """Main test function"""
    print("🔧 Testing Corrected Knowledge.py Implementation")
    print("=" * 60)
    
    # Test status first
    status_ok = test_knowledge_status()
    
    # Test query scenarios
    query_results = test_knowledge_query_scenarios()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   Status endpoint: {'✅ OK' if status_ok else '❌ FAILED'}")
    
    successful_queries = sum(1 for r in query_results if r['success'])
    total_queries = len(query_results)
    print(f"   Query success rate: {successful_queries}/{total_queries}")
    
    if successful_queries > 0:
        avg_time = sum(r['time'] for r in query_results if r['success']) / successful_queries
        print(f"   Average response time: {avg_time:.2f}s")
        
        modes_used = set(r.get('mode') for r in query_results if r['success'] and r.get('mode'))
        print(f"   Response modes: {list(modes_used)}")
    
    print("\n🎯 Expected Behavior:")
    print("   • LightRAG queries should complete within 30s")
    print("   • Timeout queries should fallback to educational responses")
    print("   • All queries should return helpful content")
    print("   • No hanging or empty responses")
    
    if successful_queries == total_queries and status_ok:
        print("\n🎉 All tests passed! Knowledge base is working correctly.")
    else:
        print(f"\n⚠️  {total_queries - successful_queries} tests failed. Check backend logs for details.")

if __name__ == "__main__":
    main()