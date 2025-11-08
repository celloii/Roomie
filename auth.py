"""
Simple authentication system for storing and managing users.
Uses JSON file for persistence.
"""
import json
import os
import hashlib
from typing import Optional, Dict

USERS_FILE = 'users.json'

def load_users() -> Dict:
    """Load users from JSON file."""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"hosts": {}, "visitors": {}}
    return {"hosts": {}, "visitors": {}}

def save_users(users: Dict):
    """Save users to JSON file."""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def hash_password(password: str) -> str:
    """Simple password hashing (for demo purposes)."""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(email: str, password: str, name: str, user_type: str) -> bool:
    """
    Create a new user.
    user_type should be 'host' or 'visitor'
    """
    users = load_users()
    user_key = user_type + "s"  # 'hosts' or 'visitors'
    
    if email in users[user_key]:
        return False  # User already exists
    
    users[user_key][email] = {
        "email": email,
        "password_hash": hash_password(password),
        "name": name,
        "type": user_type
    }
    
    save_users(users)
    return True

def verify_user(email: str, password: str, user_type: str) -> Optional[Dict]:
    """
    Verify user credentials.
    Returns user data if valid, None otherwise.
    """
    users = load_users()
    user_key = user_type + "s"
    
    if email not in users[user_key]:
        return None
    
    user = users[user_key][email]
    if user["password_hash"] == hash_password(password):
        # Return user data without password
        return {
            "email": user["email"],
            "name": user["name"],
            "type": user["type"]
        }
    
    return None

def get_user(email: str, user_type: str) -> Optional[Dict]:
    """Get user data by email."""
    users = load_users()
    user_key = user_type + "s"
    
    if email in users[user_key]:
        user = users[user_key][email]
        return {
            "email": user["email"],
            "name": user["name"],
            "type": user["type"]
        }
    return None

