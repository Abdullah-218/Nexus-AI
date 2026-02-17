#!/usr/bin/env python
"""Direct database query to check user"""
from db import db

user_id = "user_1771346651612"
col = db.get_collection()

# Try direct query
if col is not None:
    doc = col.find_one({"user_id": user_id})
    print(f"Direct query result: {doc is not None}")
    if doc:
        print(f"User ID: {doc.get('user_id')}")
        print(f"Email: {doc.get('profile', {}).get('email')}")
        print(f"Target Role: {doc.get('profile', {}).get('target_role')}")
    else:
        # List all users
        all_users = list(col.find({}, {"_id": 0, "user_id": 1, "profile.email": 1}))
        print(f"\nTotal users in collection: {len(all_users)}")
        for u in all_users[:5]:
            print(f"  - {u.get('user_id')} | {u.get('profile', {}).get('email')}")
else:
    print("Database not available")
