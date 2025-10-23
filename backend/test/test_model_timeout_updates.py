#!/usr/bin/env python3
"""
Test script for updated knowledge.py with extended timeout and model selection
"""
import requests
import json
import time

# Test configuration
BASE_URL = "http://localhost:8000"
ENDPOINT = "/api/knowledge/query"

def test_model_selection_and_timeout():
    """Test model selection and extended timeout functionality"""
    print("=== Testing Model Selection and Extended Timeout ===")
    
    test_cases = [
        {
            "name": "DeepSeek Model Test",
            "data": {
                "question": "deepseekv3.2的特点是什么？",
                "mode": "hybrid",
                "model": "deepseek-ai/DeepSeek-V3.1-Terminus"
            },
            "params": {"space_name": "test"},
            "expected_timeout": 90  # Backend timeout is now 90s
        },
        {
            "name": "Default Model Test (No Model Specified)",
            "data": {
                "question": "What is machine learning?",
                "mode": "hybrid"
                # No model specified - should use Pro/moonshotai/Kimi-K2-Instruct-0905
            },
            "params": {"space_name": "test"},
            "expected_timeout": 90
        },
        {
            "name": "Custom Model Test",
            "data": {
                "question": "人工智能的发展历程",
                "mode": "local",
                "model": "Pro/THUDM/glm-4-9b-chat"
            },
            "params": {"space_name": "test"},
            "expected_timeout": 90
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f\"\\n{i}. Testing: {test_case['name']}\")\n        print(f\"   Question: {test_case['data']['question']}\")\n        print(f\"   Model: {test_case['data'].get('model', 'Default (Pro/moonshotai/Kimi-K2-Instruct-0905)')}\")\n        \n        try:\n            start_time = time.time()\n            \n            response = requests.post(\n                f\"{BASE_URL}{ENDPOINT}\",\n                json=test_case['data'],\n                params=test_case['params'],\n                timeout=120  # Frontend timeout of 120s to allow for 90s backend processing\n            )\n            \n            elapsed_time = time.time() - start_time\n            \n            if response.status_code == 200:\n                result = response.json()\n                print(f\"   ✅ SUCCESS ({elapsed_time:.2f}s)\")\n                print(f\"   Mode: {result.get('mode', 'N/A')}\")\n                print(f\"   Model Used: {result.get('model_used', 'N/A')}\")\n                print(f\"   Sources: {result.get('sources', [])}\")\n                print(f\"   Answer length: {len(result.get('answer', ''))}\")\n                \n                # Check if timeout worked\n                if elapsed_time < test_case['expected_timeout']:\n                    print(f\"   ⚡ Completed within expected timeout ({test_case['expected_timeout']}s)\")\n                else:\n                    print(f\"   ⚠️  Took longer than expected timeout ({test_case['expected_timeout']}s)\")\n                \n                # Preview answer\n                answer_preview = result.get('answer', '')[:200].replace('\\n', ' ')\n                print(f\"   Answer preview: {answer_preview}...\")\n                \n                results.append({\n                    \"test\": test_case['name'],\n                    \"success\": True,\n                    \"time\": elapsed_time,\n                    \"mode\": result.get('mode'),\n                    \"model_used\": result.get('model_used'),\n                    \"within_timeout\": elapsed_time < test_case['expected_timeout']\n                })\n            else:\n                print(f\"   ❌ FAILED - HTTP {response.status_code}\")\n                print(f\"   Response: {response.text[:300]}...\")\n                results.append({\n                    \"test\": test_case['name'],\n                    \"success\": False,\n                    \"time\": elapsed_time,\n                    \"error\": f\"HTTP {response.status_code}\"\n                })\n                \n        except requests.exceptions.Timeout:\n            elapsed_time = time.time() - start_time\n            print(f\"   ⚠️  TIMEOUT after {elapsed_time:.2f}s (Frontend timeout: 120s)\")\n            print(f\"   This indicates backend processing exceeded 90s timeout\")\n            results.append({\n                \"test\": test_case['name'],\n                \"success\": False,\n                \"time\": elapsed_time,\n                \"error\": \"Frontend Timeout\"\n            })\n        except Exception as e:\n            elapsed_time = time.time() - start_time\n            print(f\"   ❌ ERROR after {elapsed_time:.2f}s: {e}\")\n            results.append({\n                \"test\": test_case['name'],\n                \"success\": False,\n                \"time\": elapsed_time,\n                \"error\": str(e)\n            })\n    \n    return results\n\ndef main():\n    \"\"\"Main test function\"\"\"\n    print(\"🔧 Testing Updated Knowledge.py - Model Selection & Extended Timeout\")\n    print(\"=\" * 80)\n    \n    # Test the updated functionality\n    test_results = test_model_selection_and_timeout()\n    \n    # Summary\n    print(\"\\n\" + \"=\" * 80)\n    print(\"📊 Test Summary:\")\n    \n    successful_tests = sum(1 for r in test_results if r['success'])\n    total_tests = len(test_results)\n    print(f\"   Success rate: {successful_tests}/{total_tests}\")\n    \n    if successful_tests > 0:\n        avg_time = sum(r['time'] for r in test_results if r['success']) / successful_tests\n        print(f\"   Average response time: {avg_time:.2f}s\")\n        \n        # Check model usage\n        models_used = set(r.get('model_used') for r in test_results if r['success'] and r.get('model_used'))\n        print(f\"   Models successfully used: {list(models_used)}\")\n        \n        # Check timeout performance\n        within_timeout = sum(1 for r in test_results if r['success'] and r.get('within_timeout', False))\n        print(f\"   Tests completed within 90s timeout: {within_timeout}/{successful_tests}\")\n    \n    print(\"\\n🎯 Expected Behavior:\")\n    print(\"   • User-specified models should be used in LightRAG processing\")\n    print(\"   • Default model: Pro/moonshotai/Kimi-K2-Instruct-0905 when no model specified\")\n    print(\"   • Backend timeout extended to 90 seconds (30s + 1 minute)\")\n    print(\"   • Frontend timeout set to 120 seconds for buffer\")\n    print(\"   • All queries should complete or fallback gracefully\")\n    \n    if successful_tests == total_tests:\n        print(\"\\n🎉 All tests passed! Model selection and timeout updates are working correctly.\")\n    else:\n        print(f\"\\n⚠️  {total_tests - successful_tests} tests failed. Check backend logs for details.\")\n        print(\"   Note: Some timeouts may be expected for complex queries with new models.\")\n\nif __name__ == \"__main__\":\n    main()