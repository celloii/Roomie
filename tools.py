# tools.py

# --- Mock Database (JSON/Python Dictionary approach) ---
MOCK_HOSTS_DATA = [
    {
        "id": 101, 
        "name": "Alex", 
        "interests": "Quiet study, loves coffee, early riser.",
        "dorm_vibe": "Quiet space, early bedtime (11 PM).",
        "available_dates": ["2025-11-08", "2025-11-09"],
        "capacity": 1
    },
    {
        "id": 102, 
        "name": "Jamie", 
        "interests": "Late-night gaming, heavy sleeper, social.",
        "dorm_vibe": "Loud, frequent guests, night owl.",
        "available_dates": ["2025-11-08", "2025-11-10"],
        "capacity": 2
    }
]
# --------------------------------------------------------

def find_available_hosts(visitor_date_range: str, min_capacity: int = 1) -> str:
    """
    Queries the mock database to find available hosts based on date and capacity.
    
    Args:
        visitor_date_range: The dates the visitor needs accommodation (e.g., '2025-11-08').
        min_capacity: The minimum capacity required.

    Returns:
        A JSON string containing the list of available hosts and their profiles (interests/vibe).
    """
    
    available_hosts = [
        host for host in MOCK_HOSTS_DATA 
        if visitor_date_range in host["available_dates"] and host["capacity"] >= min_capacity
    ]
    
    import json
    return json.dumps(available_hosts)