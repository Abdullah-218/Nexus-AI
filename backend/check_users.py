#!/usr/bin/env python
"""Quick script to check if users are being saved to MongoDB"""
from db import db

print(f"MongoDB Available: {db.available}")

if db.available:
    collection = db.get_collection()
    user_count = collection.count_documents({})
    print(f"\nTotal users in database: {user_count}")
    
    if user_count > 0:
        print("\nRecent users (last 3):")
        users = list(collection.find({}, {'_id': 0}).sort('last_updated', -1).limit(3))
        for i, user in enumerate(users, 1):
            user_id = user.get("user_id", "N/A")
            name = user.get("profile", {}).get("name", "N/A")
            email = user.get("profile", {}).get("email", "N/A")
            target_role = user.get("profile", {}).get("target_role", "N/A")
            last_updated = user.get("last_updated", "N/A")[:19]
            print(f"{i}. {user_id}")
            print(f"   Name: {name}")
            print(f"   Email: {email}")
            print(f"   Target Role: {target_role}")
            print(f"   Last Updated: {last_updated}")
            print()
    else:
        print("\nNo users in database yet.")
else:
    print("\nMongoDB is NOT connected!")
    print("Check your MONGO_URI in .env and MongoDB Atlas network access settings.")
