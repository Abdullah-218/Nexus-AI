#!/usr/bin/env python
"""Test market intelligence regeneration on onboarding"""
from orchestrator_wrapper import onboard_user
from db import db
import json

# Test data
test_data = {
    "name": "Test User",
    "email": "test_market_regen@example.com",
    "target_role": "Python Developer",
    "skills": ["Python", "FastAPI"],
    "strengths": ["Problem solving"],
    "weaknesses": ["Public speaking"],
    "experience_years": 2,
    "phone": "555-1234"
}

try:
    # First onboarding (should create user with email_check placeholder)
    # Then second onboarding (should update with real role and regenerate market intel)
    result = onboard_user(test_data)
    user_id = result["user_id"]
    print(f"✓ User created: {user_id}")
    print(f"  Name: {result['profile'].get('name')}")
    print(f"  Email: {result['profile'].get('email')}")
    print(f"  Target Role: {result['profile'].get('target_role')}")
    
    # Check what was saved in MongoDB
    user = db.get_user(user_id)
    if user:
        market = user.get("market_analysis", {})
        print(f"\n✓ Market Intelligence generated:")
        print(f"  Role Title: {market.get('role_title')}")
        print(f"  Demand Score: {market.get('demand_score')}")
        print(f"  Last Updated: {market.get('last_updated')}")
        
        # Verify role_title matches target_role
        if market.get('role_title') == test_data['target_role']:
            print(f"\n✅ SUCCESS: Market intelligence has correct role!")
        else:
            print(f"\n❌ MISMATCH: Expected '{test_data['target_role']}', got '{market.get('role_title')}'")
    else:
        print("❌ User not found in database!")
        
except Exception as e:
    import traceback
    print(f"❌ Error: {e}")
    traceback.print_exc()
