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
                data = json.load(f)
                # Migrate old format to new format if needed
                if "users" not in data:
                    users = {}
                    # Migrate from old format
                    for email, user_data in data.get("hosts", {}).items():
                        users[email] = {
                            "email": email,
                            "password_hash": user_data.get("password_hash"),
                            "name": user_data.get("name"),
                            "roles": ["host"]
                        }
                    for email, user_data in data.get("visitors", {}).items():
                        if email in users:
                            if "host" not in users[email]["roles"]:
                                users[email]["roles"].append("visitor")
                        else:
                            users[email] = {
                                "email": email,
                                "password_hash": user_data.get("password_hash"),
                                "name": user_data.get("name"),
                                "roles": ["visitor"]
                            }
                    return {"users": users}
                return data
        except (json.JSONDecodeError, IOError):
            return {"users": {}}
    return {"users": {}}

def save_users(users: Dict):
    """Save users to JSON file."""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def hash_password(password: str) -> str:
    """Simple password hashing (for demo purposes)."""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(email: str, password: str, name: str) -> bool:
    """
    Create a new user. Users can have multiple roles (host, visitor, or both).
    """
    users_data = load_users()
    users = users_data.get("users", {})
    
    if email in users:
        return False  # User already exists
    
    users[email] = {
        "email": email,
        "password_hash": hash_password(password),
        "name": name,
        "roles": []  # Roles will be added as needed
    }
    
    users_data["users"] = users
    save_users(users_data)
    return True

def add_role_to_user(email: str, role: str) -> bool:
    """Add a role to an existing user."""
    users_data = load_users()
    users = users_data.get("users", {})
    
    if email not in users:
        return False
    
    if role not in users[email].get("roles", []):
        if "roles" not in users[email]:
            users[email]["roles"] = []
        users[email]["roles"].append(role)
        users_data["users"] = users
        save_users(users_data)
    return True

def verify_user(email: str, password: str) -> Optional[Dict]:
    """
    Verify user credentials (no type required).
    Returns user data with roles if valid, None otherwise.
    """
    users_data = load_users()
    users = users_data.get("users", {})
    
    if email not in users:
        return None
    
    user = users[email]
    if user["password_hash"] == hash_password(password):
        # Return user data without password
        return {
            "email": user["email"],
            "name": user["name"],
            "roles": user.get("roles", [])
        }
    
    return None

def get_user(email: str) -> Optional[Dict]:
    """Get user data by email."""
    users_data = load_users()
    users = users_data.get("users", {})
    
    if email in users:
        user = users[email]
        return {
            "email": user["email"],
            "name": user["name"],
            "roles": user.get("roles", [])
        }
    return None

