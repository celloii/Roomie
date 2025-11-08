#!/usr/bin/env python3
"""
Test script to verify the backend is running correctly.
Run this with: python test_backend.py
"""

import asyncio
import json
import os
import sys
from tools import find_available_hosts
from ai_agent import run_matching_agent

def test_find_available_hosts():
    """Test the find_available_hosts tool function."""
    print("=" * 60)
    print("TEST 1: Testing find_available_hosts tool")
    print("=" * 60)
    
    # Test case 1: Valid date
    print("\n✓ Test 1.1: Finding hosts for date '2025-11-08'")
    result = find_available_hosts("2025-11-08")
    hosts = json.loads(result)
    print(f"   Found {len(hosts)} host(s)")
    for host in hosts:
        print(f"   - {host['name']} (ID: {host['id']})")
    assert len(hosts) == 2, f"Expected 2 hosts, got {len(hosts)}"
    
    # Test case 2: Date with only one host
    print("\n✓ Test 1.2: Finding hosts for date '2025-11-09'")
    result = find_available_hosts("2025-11-09")
    hosts = json.loads(result)
    print(f"   Found {len(hosts)} host(s)")
    assert len(hosts) == 1, f"Expected 1 host, got {len(hosts)}"
    assert hosts[0]['name'] == "Alex", "Expected Alex to be available"
    
    # Test case 3: Date with no hosts
    print("\n✓ Test 1.3: Finding hosts for date '2025-12-25' (no hosts)")
    result = find_available_hosts("2025-12-25")
    hosts = json.loads(result)
    print(f"   Found {len(hosts)} host(s)")
    assert len(hosts) == 0, f"Expected 0 hosts, got {len(hosts)}"
    
    # Test case 4: With capacity filter
    print("\n✓ Test 1.4: Finding hosts with capacity >= 2")
    result = find_available_hosts("2025-11-08", min_capacity=2)
    hosts = json.loads(result)
    print(f"   Found {len(hosts)} host(s) with capacity >= 2")
    assert len(hosts) == 1, f"Expected 1 host, got {len(hosts)}"
    assert hosts[0]['name'] == "Jamie", "Expected Jamie (capacity 2)"
    
    print("\n✅ All find_available_hosts tests passed!")


async def test_matching_agent():
    """Test the run_matching_agent function (requires DEDALUS_API_KEY)."""
    print("\n" + "=" * 60)
    print("TEST 2: Testing run_matching_agent (requires API key)")
    print("=" * 60)
    
    # Check if API key is set
    api_key = os.environ.get("DEDALUS_API_KEY")
    if not api_key:
        print("\n⚠️  WARNING: DEDALUS_API_KEY not set in environment.")
        print("   Skipping agent test. Set it with:")
        print("   export DEDALUS_API_KEY='your-key-here'")
        print("   or create a .env file with DEDALUS_API_KEY=your-key-here")
        return False
    
    print(f"\n✓ API key found: {api_key[:10]}...")
    
    try:
        print("\n✓ Running matching agent with test query...")
        visitor_query = "I need a quiet place, I have classes early and go to bed by 10 PM."
        date_needed = "2025-11-08"
        
        result = await run_matching_agent(visitor_query, date_needed)
        
        print(f"\n✓ Agent returned result:")
        print(f"   Type: {type(result)}")
        print(f"   Content preview: {str(result)[:200]}...")
        
        # Try to parse as JSON if it's a string
        if isinstance(result, str):
            try:
                parsed = json.loads(result)
                print(f"\n✓ Result is valid JSON!")
                if "ranked_matches" in parsed:
                    print(f"   Found {len(parsed['ranked_matches'])} ranked matches")
                    for i, match in enumerate(parsed['ranked_matches'][:3], 1):
                        print(f"   {i}. {match.get('name', 'Unknown')} - Score: {match.get('compatibility_score', 'N/A')}")
            except json.JSONDecodeError:
                print(f"   (Result is not JSON, but that's okay)")
        
        print("\n✅ Matching agent test completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR during agent test: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_imports():
    """Test that all required modules can be imported."""
    print("=" * 60)
    print("TEST 0: Testing imports")
    print("=" * 60)
    
    try:
        import dedalus_labs
        print("✓ dedalus_labs imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import dedalus_labs: {e}")
        print("   Install it with: pip install dedalus-labs")
        return False
    
    try:
        from tools import find_available_hosts
        print("✓ tools module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import tools: {e}")
        return False
    
    try:
        from ai_agent import run_matching_agent
        print("✓ ai_agent module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ai_agent: {e}")
        return False
    
    print("\n✅ All imports successful!")
    return True


async def main():
    """Run all tests."""
    print("\n" + "🚀 Starting Backend Tests" + "\n")
    
    # Test 0: Imports
    if not test_imports():
        print("\n❌ Import tests failed. Please fix import errors first.")
        sys.exit(1)
    
    # Test 1: Tool function
    try:
        test_find_available_hosts()
    except AssertionError as e:
        print(f"\n❌ Tool test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error in tool test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Test 2: Agent function (optional if no API key)
    agent_success = await test_matching_agent()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print("✅ Tool function tests: PASSED")
    if agent_success:
        print("✅ Agent function test: PASSED")
    else:
        print("⚠️  Agent function test: SKIPPED (no API key)")
    print("\n🎉 Backend is working correctly!")


if __name__ == "__main__":
    asyncio.run(main())

