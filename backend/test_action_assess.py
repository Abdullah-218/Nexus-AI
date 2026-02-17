#!/usr/bin/env python
"""Test the assess_action function to identify the error"""
import json
from orchestrator_wrapper import assess_action

# Test with a real user and action
user_id = "user_1771346651612"
action_id = "action_001"
answers = [
    "Answer 1", "Answer 2", "Answer 3", "Answer 4", "Answer 5",
    "Answer 6", "Answer 7", "Answer 8", "Answer 9", "Answer 10"
]

try:
    result = assess_action(user_id, action_id, answers)
    print("Success!")
    print(json.dumps(result, indent=2))
except Exception as e:
    import traceback
    print(f"Error: {type(e).__name__}: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
