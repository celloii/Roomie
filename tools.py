# tools.py
import json
import os

# --- Mock Database (JSON file approach) ---
LISTINGS_FILE = 'listings.json'
UPLOAD_FOLDER = 'uploads'

def ensure_upload_folder():
    """Create uploads folder if it doesn't exist."""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

def load_listings() -> list:
    """Load listings from JSON file."""
    if os.path.exists(LISTINGS_FILE):
        try:
            with open(LISTINGS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return get_default_listings()
    return get_default_listings()

def save_listings(listings: list):
    """Save listings to JSON file."""
    with open(LISTINGS_FILE, 'w') as f:
        json.dump(listings, f, indent=2)

def get_default_listings() -> list:
    """Get default listings data."""
    return [
        {
            "id": 101, 
            "name": "Alex", 
            "email": "alex@example.com",
            "interests": "Quiet study, loves coffee, early riser.",
            "dorm_vibe": "Quiet space, early bedtime (11 PM).",
            "available_dates": ["2025-11-08", "2025-11-09"],
            "capacity": 1,
            "images": [],
            "description": "A cozy, quiet dorm room perfect for studying. Early bedtime environment."
        },
        {
            "id": 102, 
            "name": "Jamie", 
            "email": "jamie@example.com",
            "interests": "Late-night gaming, heavy sleeper, social.",
            "dorm_vibe": "Loud, frequent guests, night owl.",
            "available_dates": ["2025-11-08", "2025-11-10"],
            "capacity": 2,
            "images": [],
            "description": "A vibrant, social dorm space. Great for night owls and gamers."
        }
    ]

def get_listing_by_id(listing_id: int) -> dict:
    """Get a listing by ID."""
    listings = load_listings()
    for listing in listings:
        if listing.get("id") == listing_id:
            return listing
    return None

def get_listings_by_email(email: str) -> list:
    """Get all listings by host email."""
    listings = load_listings()
    return [listing for listing in listings if listing.get("email") == email]

def get_listing_by_email(email: str) -> dict:
    """Get the first listing by host email (for backward compatibility)."""
    listings = get_listings_by_email(email)
    return listings[0] if listings else None

def update_listing(listing_id: int, updates: dict):
    """Update a listing."""
    listings = load_listings()
    for i, listing in enumerate(listings):
        if listing.get("id") == listing_id:
            listings[i].update(updates)
            save_listings(listings)
            return True
    return False

def add_image_to_listing(listing_id: int, image_path: str):
    """Add an image path to a listing."""
    listings = load_listings()
    for listing in listings:
        if listing.get("id") == listing_id:
            if "images" not in listing:
                listing["images"] = []
            listing["images"].append(image_path)
            save_listings(listings)
            return True
    return False

def create_listing(email: str, name: str, description: str = "", available_dates: list = None, capacity: int = 1, dorm_vibe: str = "", interests: str = "") -> dict:
    """Create a new listing for a host. Hosts can have multiple listings."""
    listings = load_listings()
    
    # Find the next available ID
    max_id = max([listing.get("id", 0) for listing in listings], default=100)
    new_id = max_id + 1
    
    new_listing = {
        "id": new_id,
        "email": email,
        "name": name,
        "description": description,
        "available_dates": available_dates or [],
        "capacity": capacity,
        "dorm_vibe": dorm_vibe,
        "interests": interests,
        "images": [],
        "reviews": []
    }
    
    listings.append(new_listing)
    save_listings(listings)
    return new_listing

def update_listing_details(listing_id: int, updates: dict):
    """Update listing details (description, dates, capacity, etc.)."""
    listings = load_listings()
    for i, listing in enumerate(listings):
        if listing.get("id") == listing_id:
            # Only update allowed fields
            allowed_fields = ["description", "available_dates", "capacity", "dorm_vibe", "interests"]
            for key, value in updates.items():
                if key in allowed_fields or key in ["dorm_vibe", "interests"]:
                    listings[i][key] = value
            save_listings(listings)
            return True
    return False

def add_review(listing_id: int, reviewer_name: str, rating: int, comment: str) -> bool:
    """Add a review to a listing."""
    if rating < 1 or rating > 5:
        return False
    
    listings = load_listings()
    for listing in listings:
        if listing.get("id") == listing_id:
            if "reviews" not in listing:
                listing["reviews"] = []
            
            import datetime
            review = {
                "id": len(listing["reviews"]) + 1,
                "reviewer_name": reviewer_name,
                "rating": rating,
                "comment": comment,
                "date": datetime.datetime.now().isoformat()
            }
            
            listing["reviews"].append(review)
            save_listings(listings)
            return True
    return False

def get_average_rating(listing_id: int) -> float:
    """Calculate average rating for a listing."""
    listing = get_listing_by_id(listing_id)
    if not listing or not listing.get("reviews"):
        return 0.0
    
    reviews = listing["reviews"]
    if len(reviews) == 0:
        return 0.0
    
    total_rating = sum(review.get("rating", 0) for review in reviews)
    return round(total_rating / len(reviews), 1)

def delete_listing(listing_id: int) -> bool:
    """Delete a listing by ID."""
    listings = load_listings()
    original_length = len(listings)
    listings = [listing for listing in listings if listing.get("id") != listing_id]
    
    if len(listings) < original_length:
        save_listings(listings)
        return True
    return False

def find_available_hosts(visitor_date_range: str, min_capacity: int = 1) -> str:
    """
    Queries the listings database to find available hosts based on date and capacity.
    Supports both single dates and date ranges (comma-separated or dash-separated).
    
    Args:
        visitor_date_range: The dates the visitor needs accommodation. Can be:
            - Single date: '2025-11-08'
            - Date range: '2025-11-08,2025-11-10' or '2025-11-08-2025-11-10'
            - Comma-separated dates: '2025-11-08,2025-11-09,2025-11-10'
        min_capacity: The minimum capacity required.

    Returns:
        A JSON string containing the list of available hosts and their profiles (interests/vibe).
    """
    listings = load_listings()
    
    # Parse date range - support multiple formats
    needed_dates = []
    if ',' in visitor_date_range:
        # Comma-separated dates
        needed_dates = [d.strip() for d in visitor_date_range.split(',')]
    elif '-' in visitor_date_range and len(visitor_date_range.split('-')) == 3:
        # Check if it's a date range (start-end) or just a date with dashes
        parts = visitor_date_range.split('-')
        if len(parts) == 5:  # YYYY-MM-DD-YYYY-MM-DD format
            start_date = f"{parts[0]}-{parts[1]}-{parts[2]}"
            end_date = f"{parts[3]}-{parts[4]}-{parts[5] if len(parts) > 5 else parts[4]}"
            # Generate date range
            from datetime import datetime, timedelta
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            current = start
            while current <= end:
                needed_dates.append(current.strftime('%Y-%m-%d'))
                current += timedelta(days=1)
        else:
            # Single date
            needed_dates = [visitor_date_range]
    else:
        # Single date
        needed_dates = [visitor_date_range]
    
    # Find hosts that have ALL needed dates available
    available_hosts = []
    for host in listings:
        host_dates = set(host.get("available_dates", []))
        # Check if host has all needed dates available
        if all(date in host_dates for date in needed_dates) and host.get("capacity", 0) >= min_capacity:
            available_hosts.append(host)
    
    return json.dumps(available_hosts)