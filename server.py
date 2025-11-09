"""
Flask API server that integrates with the existing Dedalus Labs AI agent.
Run with: python server.py
"""
from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
import asyncio
import json
import os
from werkzeug.utils import secure_filename
from ai_agent import run_matching_agent
from auth import create_user, verify_user, get_user, add_role_to_user
from tools import (
    load_listings, get_listing_by_id, get_listing_by_email, 
    update_listing, add_image_to_listing, ensure_upload_folder,
    create_listing, update_listing_details, add_review, delete_listing
)

app = Flask(__name__, static_folder='.')
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
CORS(app, supports_credentials=True)  # Enable CORS with credentials for sessions

from datetime import timedelta

# Make sessions permanent so they persist
app.permanent_session_lifetime = timedelta(days=1)  # Sessions last 1 day

# Configure session cookie settings for persistence
# In production (HTTPS), set SESSION_COOKIE_SECURE=True
is_production = os.environ.get('ENVIRONMENT') == 'production' or os.environ.get('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = is_production  # True in production (HTTPS), False in development
app.config['SESSION_COOKIE_HTTPONLY'] = True

# Before each request, mark session as permanent if it has any data
@app.before_request
def make_session_permanent():
    if 'user_email' in session or 'guest' in session:
        session.permanent = True

@app.route('/')
def index():
    """Serve the login page as the home page."""
    return send_from_directory('.', 'login.html')

@app.route('/login')
def login_page():
    """Serve the login page."""
    return send_from_directory('.', 'login.html')

@app.route('/signup')
def signup_page():
    """Serve the signup page."""
    return send_from_directory('.', 'signup.html')

@app.route('/listing/<int:listing_id>')
def listing_page(listing_id):
    """Serve the listing detail page."""
    return send_from_directory('.', 'listing.html')

@app.route('/host/dashboard')
def host_dashboard():
    """Serve the host dashboard page."""
    return send_from_directory('.', 'host_dashboard.html')

@app.route('/dashboard')
def dashboard():
    """Serve the unified dashboard page."""
    return send_from_directory('.', 'dashboard.html')

@app.route('/events')
def events_page():
    """Serve the events page."""
    from flask import Response
    import os
    file_path = os.path.join('.', 'events.html')
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return Response(content, mimetype='text/html')
    return send_from_directory('.', 'events.html')

@app.route('/chatbot.js')
def chatbot_js():
    """Serve the chatbot JavaScript file."""
    return send_from_directory('.', 'chatbot.js', mimetype='application/javascript')

@app.route('/logo.svg')
def logo_svg():
    """Serve the Roomie logo SVG file."""
    return send_from_directory('.', 'logo.svg', mimetype='image/svg+xml')

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """Sign up a new user (no type required - can be both host and visitor)."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()
        name = data.get('name', '').strip()
        
        if not email or not password or not name:
            return jsonify({"error": "Email, password, and name are required"}), 400
        
        if create_user(email, password, name):
            # Auto-login after signup
            session['user_email'] = email
            session.permanent = True  # Make session persist for 1 day
            user = get_user(email)
            return jsonify({
                "success": True,
                "message": "Account created successfully",
                "user": user
            }), 200
        else:
            return jsonify({"error": "Email already exists"}), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login a user (no type required)."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        user = verify_user(email, password)
        
        if user:
            session['user_email'] = email
            session.permanent = True
            return jsonify({
                "success": True,
                "message": "Login successful",
                "user": user
            }), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 401
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/auth/check', methods=['GET'])
def check_auth():
    """Check if user is authenticated."""
    if 'user_email' in session:
        user = get_user(session['user_email'])
        if user:
            return jsonify({
                "authenticated": True,
                "user": user
            }), 200
    
    if 'guest' in session and session.get('guest'):
        return jsonify({
            "authenticated": False,
            "guest": True
        }), 200
    
    return jsonify({"authenticated": False, "guest": False}), 200

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout the current user by clearing the session."""
    try:
        session.clear()
        return jsonify({
            "success": True,
            "message": "Logged out successfully"
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/match', methods=['POST'])
def match_visitor():
    """
    API endpoint that uses the existing Dedalus Labs agent to match visitors with hosts.
    Allows both authenticated users and guests.
    """
    # Check authentication - allow guests or authenticated users
    is_guest = session.get('guest', False)
    is_authenticated = 'user_email' in session
    
    if not is_guest and not is_authenticated:
        return jsonify({"error": "Authentication required. Please login or continue as guest."}), 401
    
    # If authenticated, check/update roles (skip for guests)
    if is_authenticated:
        user = get_user(session['user_email'])
        if user and 'visitor' not in user.get('roles', []):
            # Add visitor role if they don't have it
            try:
                from auth import add_role_to_user
                add_role_to_user(session['user_email'], 'visitor')
            except:
                pass  # If add_role_to_user doesn't exist, continue anyway
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        visitor_query = data.get('visitor_query', '').strip()
        date_needed = data.get('date_needed', '').strip()
        
        if not visitor_query:
            return jsonify({"error": "visitor_query is required"}), 400
        if not date_needed:
            return jsonify({"error": "date_needed is required"}), 400
        
        # Call the existing Dedalus Labs agent
        result = asyncio.run(run_matching_agent(visitor_query, date_needed))
        
        # The agent returns a string (JSON), try to parse it
        if isinstance(result, str):
            # Try to extract JSON from markdown code blocks or plain text
            import re
            json_str = result.strip()
            
            # Remove markdown code blocks if present
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', json_str, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON object in the string
                json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
            
            try:
                parsed_result = json.loads(json_str)
                return jsonify({
                    "success": True,
                    "matches": parsed_result
                }), 200
            except json.JSONDecodeError:
                # If it's not valid JSON, try to return it as-is for frontend to handle
                return jsonify({
                    "success": True,
                    "matches": {"raw_output": result}
                }), 200
        else:
            # If it's already a dict/object
            return jsonify({
                "success": True,
                "matches": result
            }), 200
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return jsonify({
            "success": False,
            "error": str(e),
            "details": error_details
        }), 500

@app.route('/api/listings', methods=['GET'])
def get_all_listings():
    """Get all available listings with average ratings."""
    listings = load_listings()
    from tools import get_average_rating
    
    # Add average rating to each listing
    for listing in listings:
        listing['average_rating'] = get_average_rating(listing.get('id', 0))
        listing['review_count'] = len(listing.get('reviews', []))
    
    return jsonify({"success": True, "listings": listings}), 200

@app.route('/api/listings/match', methods=['POST'])
def match_listings():
    """Use AI agent to match listings based on visitor preferences."""
    if 'user_email' not in session:
        return jsonify({"error": "Authentication required. Please login."}), 401
    
    try:
        data = request.get_json()
        visitor_query = data.get('visitor_query', '').strip()
        date_needed = data.get('date_needed', '').strip()
        
        if not visitor_query or not date_needed:
            return jsonify({"error": "visitor_query and date_needed are required"}), 400
        
        # Call the existing Dedalus Labs agent
        result = asyncio.run(run_matching_agent(visitor_query, date_needed))
        
        # Debug logging
        print(f"AI Agent Result Type: {type(result)}")
        print(f"AI Agent Result: {result}")
        
        # Parse the result
        if isinstance(result, str):
            import re
            json_str = result.strip()
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', json_str, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
            
            try:
                parsed_result = json.loads(json_str)
                print(f"Parsed result: {parsed_result}")
                # Ensure the response has the expected structure
                if isinstance(parsed_result, dict) and 'ranked_matches' in parsed_result:
                    return jsonify({
                        "success": True,
                        "matches": parsed_result
                    }), 200
                else:
                    # If it's already the matches object, wrap it
                    return jsonify({
                        "success": True,
                        "matches": parsed_result if isinstance(parsed_result, dict) else {"ranked_matches": []}
                    }), 200
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                return jsonify({
                    "success": True,
                    "matches": {"raw_output": result, "ranked_matches": []}
                }), 200
        else:
            # If result is already a dict
            if isinstance(result, dict):
                return jsonify({
                    "success": True,
                    "matches": result
                }), 200
            else:
                return jsonify({
                    "success": True,
                    "matches": {"ranked_matches": []}
                }), 200
        
    except Exception as e:
        import traceback
        return jsonify({
            "success": False,
            "error": str(e),
            "details": traceback.format_exc()
        }), 500

@app.route('/api/listing/<int:listing_id>', methods=['GET'])
def get_listing(listing_id):
    """Get listing details by ID with average rating."""
    listing = get_listing_by_id(listing_id)
    if listing:
        from tools import get_average_rating
        listing['average_rating'] = get_average_rating(listing_id)
        listing['review_count'] = len(listing.get('reviews', []))
        return jsonify({"success": True, "listing": listing}), 200
    return jsonify({"error": "Listing not found"}), 404

@app.route('/api/listing/my-listings', methods=['GET'])
def get_my_listings():
    """Get all listings for the current host with average ratings."""
    if 'user_email' not in session:
        return jsonify({"error": "Authentication required. Please login."}), 401
    
    # Add host role if they don't have it
    user = get_user(session['user_email'])
    if user and 'host' not in user.get('roles', []):
        add_role_to_user(session['user_email'], 'host')
    
    from tools import get_listings_by_email, get_average_rating
    listings = get_listings_by_email(session['user_email'])
    
    # Add average rating to each listing
    for listing in listings:
        listing['average_rating'] = get_average_rating(listing.get('id', 0))
        listing['review_count'] = len(listing.get('reviews', []))
    
    return jsonify({"success": True, "listings": listings}), 200

@app.route('/api/listing/my-listing', methods=['GET'])
def get_my_listing():
    """Get the first listing for the current host (for backward compatibility)."""
    if 'user_email' not in session:
        return jsonify({"error": "Authentication required. Please login."}), 401
    
    listing = get_listing_by_email(session['user_email'])
    if listing:
        return jsonify({"success": True, "listing": listing}), 200
    return jsonify({"success": False, "listing": None, "error": "No listing found"}), 200

@app.route('/api/listing/create', methods=['POST'])
def create_listing_endpoint():
    """Create a new listing for the current host."""
    if 'user_email' not in session:
        return jsonify({"error": "Authentication required. Please login."}), 401
    
    # Add host role if they don't have it
    user = get_user(session['user_email'])
    if user and 'host' not in user.get('roles', []):
        add_role_to_user(session['user_email'], 'host')
        user = get_user(session['user_email'])
    
    try:
        data = request.get_json()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        description = data.get('description', '').strip()
        available_dates = data.get('available_dates', [])
        capacity = int(data.get('capacity', 1))
        dorm_vibe = data.get('dorm_vibe', '').strip()
        interests = data.get('interests', '').strip()
        
        listing = create_listing(
            email=session['user_email'],
            name=user['name'],
            description=description,
            available_dates=available_dates,
            capacity=capacity,
            dorm_vibe=dorm_vibe,
            interests=interests
        )
        
        if listing:
            return jsonify({
                "success": True,
                "message": "Listing created successfully",
                "listing": listing
            }), 200
        else:
            return jsonify({"error": "Failed to create listing"}), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/listing/<int:listing_id>/update', methods=['POST'])
def update_listing_endpoint(listing_id):
    """Update listing details."""
    if 'user_email' not in session:
        return jsonify({"error": "Authentication required. Please login."}), 401
    
    listing = get_listing_by_id(listing_id)
    if not listing:
        return jsonify({"error": "Listing not found"}), 404
    
    if listing.get('email') != session['user_email']:
        return jsonify({"error": "You can only update your own listing"}), 403
    
    try:
        data = request.get_json()
        updates = {}
        
        if 'description' in data:
            updates['description'] = data['description'].strip()
        if 'available_dates' in data:
            updates['available_dates'] = data['available_dates']
        if 'capacity' in data:
            updates['capacity'] = int(data['capacity'])
        if 'dorm_vibe' in data:
            updates['dorm_vibe'] = data['dorm_vibe'].strip()
        if 'interests' in data:
            updates['interests'] = data['interests'].strip()
        
        if update_listing_details(listing_id, updates):
            updated_listing = get_listing_by_id(listing_id)
            return jsonify({
                "success": True,
                "message": "Listing updated successfully",
                "listing": updated_listing
            }), 200
        else:
            return jsonify({"error": "Failed to update listing"}), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/listing/<int:listing_id>/delete', methods=['DELETE'])
def delete_listing_endpoint(listing_id):
    """Delete a listing."""
    if 'user_email' not in session:
        return jsonify({"error": "Authentication required. Please login."}), 401
    
    user = get_user(session['user_email'])
    if not user or 'host' not in user.get('roles', []):
        return jsonify({"error": "Only hosts can delete listings"}), 403
    
    # Verify the listing belongs to this user
    listing = get_listing_by_id(listing_id)
    if not listing:
        return jsonify({"error": "Listing not found"}), 404
    
    if listing.get('email') != session['user_email']:
        return jsonify({"error": "You can only delete your own listings"}), 403
    
    try:
        from tools import delete_listing
        if delete_listing(listing_id):
            return jsonify({
                "success": True,
                "message": "Listing deleted successfully"
            }), 200
        else:
            return jsonify({"error": "Failed to delete listing"}), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/listing/<int:listing_id>/review', methods=['POST'])
def add_review_endpoint(listing_id):
    """Add a review to a listing."""
    try:
        data = request.get_json()
        
        reviewer_name = data.get('reviewer_name', '').strip()
        rating = int(data.get('rating', 0))
        comment = data.get('comment', '').strip()
        
        if not reviewer_name or not comment:
            return jsonify({"error": "Reviewer name and comment are required"}), 400
        
        if rating < 1 or rating > 5:
            return jsonify({"error": "Rating must be between 1 and 5"}), 400
        
        if add_review(listing_id, reviewer_name, rating, comment):
            listing = get_listing_by_id(listing_id)
            return jsonify({
                "success": True,
                "message": "Review added successfully",
                "listing": listing
            }), 200
        else:
            return jsonify({"error": "Listing not found"}), 404
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/listing/<int:listing_id>/upload', methods=['POST'])
def upload_listing_image(listing_id):
    """Upload an image for a listing. Requires authentication."""
    if 'user_email' not in session:
        return jsonify({"error": "Authentication required. Please login."}), 401
    
    listing = get_listing_by_id(listing_id)
    if not listing:
        return jsonify({"error": "Listing not found"}), 404
    
    # Verify the listing belongs to the current host
    if listing.get('email') != session['user_email']:
        return jsonify({"error": "You can only upload images to your own listing"}), 403
    
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Check file extension
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    if '.' in file.filename:
        ext = file.filename.rsplit('.', 1)[1].lower()
        if ext not in allowed_extensions:
            return jsonify({"error": "Invalid file type. Allowed: png, jpg, jpeg, gif, webp"}), 400
    
    # Save file
    ensure_upload_folder()
    filename = secure_filename(f"{listing_id}_{file.filename}")
    filepath = os.path.join('uploads', filename)
    file.save(filepath)
    
    # Add image path to listing
    image_url = f"/uploads/{filename}"
    add_image_to_listing(listing_id, image_url)
    
    return jsonify({
        "success": True,
        "message": "Image uploaded successfully",
        "image_url": image_url
    }), 200

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded images."""
    return send_from_directory('uploads', filename)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "Roomie API"}), 200

# ===== Events API Endpoints (Nova Act Integration) =====

@app.route('/api/events', methods=['GET'])
def get_events():
    """
    Get events directly from Dedalus events module.
    """
    try:
        category = request.args.get('category')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        free_only = request.args.get('free_only', 'false').lower() == 'true'
        tags = request.args.get('tags')
        
        # Load events directly from file using absolute path
        import os
        import json
        
        # Get absolute path to events file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        events_file = os.path.join(base_dir, 'events_data', 'events.json')
        
        events = []
        # Try to load from file first
        if os.path.exists(events_file):
            try:
                with open(events_file, 'r') as f:
                    events = json.load(f)
            except Exception as e:
                print(f"Error reading events file: {e}")
                events = []
        
        # If no events, get defaults and save them
        if not events or len(events) == 0:
            from dedalus_events import get_default_events
            events = get_default_events()
            # Save defaults
            os.makedirs(os.path.dirname(events_file), exist_ok=True)
            try:
                with open(events_file, 'w') as f:
                    json.dump(events, f, indent=2)
            except Exception as e:
                print(f"Error saving events: {e}")
        
        # Apply filters
        if category:
            events = [e for e in events if e.get("category", "").lower() == category.lower()]
        
        if date_from:
            events = [e for e in events if e.get("date", "") >= date_from]
        
        if date_to:
            events = [e for e in events if e.get("date", "") <= date_to]
        
        if free_only:
            events = [e for e in events if (e.get("cost", 0) == 0 or e.get("cost", 0) == 0.0 or e.get("cost") is None or e.get("cost") == "0" or e.get("cost") == "0.0")]
        
        if tags:
            tag_list = [t.strip().lower() for t in tags.split(",")]
            events = [e for e in events if any(tag in [t.lower() for t in e.get("tags", [])] for tag in tag_list)]
        
        # Sort by date
        events.sort(key=lambda x: x.get("date", ""))
        
        return jsonify({
            "success": True,
            "events": events,
            "total_count": len(events)
        }), 200
        
    except Exception as e:
        import traceback
        return jsonify({
            "success": False,
            "error": str(e),
            "details": traceback.format_exc()
        }), 500

def get_keyword_based_recommendations(user_interests: str, events: list, max_recommendations: int = 5) -> dict:
    """
    Fallback keyword-based recommendation system when Claude AI is not available.
    Matches events based on keywords in titles, descriptions, tags, and categories.
    """
    if not events or not user_interests:
        return {
            "recommendations": [],
            "summary": "No events available for recommendations.",
            "ai_enabled": False
        }
    
    # Extract keywords from user interests (lowercase for matching)
    interest_lower = user_interests.lower()
    keywords = [word.strip() for word in interest_lower.split() if len(word.strip()) > 2]
    
    # Score each event based on keyword matches
    scored_events = []
    for event in events:
        score = 0
        matches = []
        
        # Check title
        title = (event.get("title", "") or "").lower()
        for keyword in keywords:
            if keyword in title:
                score += 3
                matches.append(f"title: '{keyword}'")
        
        # Check description
        description = (event.get("description", "") or "").lower()
        for keyword in keywords:
            if keyword in description:
                score += 2
                if f"description: '{keyword}'" not in matches:
                    matches.append(f"description: '{keyword}'")
        
        # Check tags
        tags = [tag.lower() if isinstance(tag, str) else str(tag).lower() for tag in (event.get("tags", []) or [])]
        for keyword in keywords:
            if keyword in tags:
                score += 4  # Tags are more specific, so higher weight
                if f"tag: '{keyword}'" not in matches:
                    matches.append(f"tag: '{keyword}'")
        
        # Check category
        category = (event.get("category", "") or "").lower()
        for keyword in keywords:
            if keyword in category:
                score += 2
                if f"category: '{keyword}'" not in matches:
                    matches.append(f"category: '{keyword}'")
        
        if score > 0:
            scored_events.append({
                "event": event,
                "relevance_score": min(score / 10.0, 1.0),  # Normalize to 0-1
                "reasoning": f"Matches your interests: {', '.join(matches[:3])}" if matches else "Relevant to your interests",
                "highlights": matches[:3]
            })
    
    # Sort by score (highest first)
    scored_events.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    # Take top recommendations
    top_recommendations = scored_events[:max_recommendations]
    
    # Generate summary
    if top_recommendations:
        event_titles = [rec["event"].get("title", "Event") for rec in top_recommendations[:3]]
        summary = f"Found {len(top_recommendations)} event(s) matching '{user_interests}': {', '.join(event_titles)}"
    else:
        summary = f"No events found matching '{user_interests}'. Try different keywords or browse all events."
    
    return {
        "recommendations": top_recommendations,
        "summary": summary,
        "ai_enabled": False
    }

@app.route('/api/events/recommendations', methods=['POST'])
def get_event_recommendations():
    """
    Get AI-powered event recommendations based on user interests.
    Uses Nova Act to orchestrate AI filtering with events loaded directly from file.
    """
    try:
        from nova_act import NovaAct
        from dedalus_events import load_events
        import asyncio
        import os
        import json
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        user_interests = data.get('interests', '').strip()
        if not user_interests:
            return jsonify({"error": "interests field is required"}), 400
        
        category = data.get('category')
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        free_only = data.get('free_only', False)
        max_results = data.get('max_results', 10)
        
        # Load events directly from file (same as /api/events endpoint)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        events_file = os.path.join(base_dir, 'events_data', 'events.json')
        
        events = []
        if os.path.exists(events_file):
            try:
                with open(events_file, 'r') as f:
                    events = json.load(f)
            except:
                from dedalus_events import get_default_events
                events = get_default_events()
        else:
            from dedalus_events import get_default_events
            events = get_default_events()
        
        # Apply basic filters first
        if category:
            events = [e for e in events if e.get("category", "").lower() == category.lower()]
        if date_from:
            events = [e for e in events if e.get("date", "") >= date_from]
        if date_to:
            events = [e for e in events if e.get("date", "") <= date_to]
        if free_only:
            events = [e for e in events if e.get("cost", 0) == 0.0]
        
        # Use Nova Act for AI recommendations
        nova_act = NovaAct()
        
        # Get AI recommendations using the events we already loaded
        recommendations = None
        if user_interests:
            if nova_act.claude_client:
                # Use Claude AI if available
                recommendations = asyncio.run(nova_act.get_ai_recommendations(
                    user_interests=user_interests,
                    events=events,
                    max_recommendations=max_results
                ))
            else:
                # Fallback: simple keyword-based matching
                recommendations = get_keyword_based_recommendations(
                    user_interests=user_interests,
                    events=events,
                    max_recommendations=max_results
                )
        
        return jsonify({
            "success": True,
            "events": events,
            "recommendations": recommendations,
            "total_count": len(events)
        }), 200
        
    except Exception as e:
        import traceback
        return jsonify({
            "success": False,
            "error": str(e),
            "details": traceback.format_exc()
        }), 500

@app.route('/api/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    """Get a specific event by ID from Dedalus."""
    try:
        from nova_act import NovaAct
        import asyncio
        
        nova_act = NovaAct()
        events = asyncio.run(nova_act.get_events_from_dedalus())
        
        event = next((e for e in events if e.get("id") == event_id), None)
        
        if not event:
            return jsonify({"error": "Event not found"}), 404
        
        return jsonify({
            "success": True,
            "event": event
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/combined/match', methods=['POST'])
def get_combined_match():
    """
    Get AI-powered combined recommendations for hosts and events.
    Uses Nova Act to find the best matches based on user preferences.
    """
    try:
        from nova_act import NovaAct
        import asyncio
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        user_preferences = data.get('preferences', '').strip()
        if not user_preferences:
            return jsonify({"error": "preferences field is required"}), 400
        
        date_needed = data.get('date_needed')
        max_hosts = data.get('max_hosts', 5)
        max_events = data.get('max_events', 5)
        
        nova_act = NovaAct()
        result = asyncio.run(nova_act.get_combined_recommendations(
            user_preferences=user_preferences,
            date_needed=date_needed,
            max_hosts=max_hosts,
            max_events=max_events
        ))
        
        return jsonify({
            "success": True,
            "hosts": result.get("hosts", []),
            "events": result.get("events", []),
            "combined_insights": result.get("combined_insights", ""),
            "ai_enabled": result.get("ai_enabled", False)
        }), 200
        
    except Exception as e:
        import traceback
        return jsonify({
            "success": False,
            "error": str(e),
            "details": traceback.format_exc()
        }), 500

# ===== Chatbot API Endpoint =====

@app.route('/api/chatbot/status', methods=['GET'])
def chatbot_status():
    """Check chatbot configuration status."""
    try:
        from knot import Knot
        knot = Knot()
        claude_config = knot.get_claude_config()
        return jsonify({
            "success": True,
            "configured": True,
            "model": claude_config.get("model", "unknown"),
            "api_key_set": bool(claude_config.get("api_key"))
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "configured": False,
            "error": str(e)
        }), 200

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    """
    Chatbot endpoint that uses Claude API to help users navigate the site.
    Provides accommodation and event recommendations based on user queries.
    """
    try:
        from knot import Knot
        from anthropic import Anthropic
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        message = data.get('message', '').strip()
        conversation_history = data.get('conversation_history', [])
        
        if not message:
            return jsonify({"error": "message field is required"}), 400
        
        # Initialize Claude client
        try:
            knot = Knot()
            claude_config = knot.get_claude_config()
            claude_client = Anthropic(api_key=claude_config["api_key"])
            claude_model = claude_config["model"]
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Claude API not configured: {str(e)}"
            }), 500
        
        # Load listings and events for context
        listings = load_listings()
        events = []
        try:
            import os
            import json
            base_dir = os.path.dirname(os.path.abspath(__file__))
            events_file = os.path.join(base_dir, 'events_data', 'events.json')
            if os.path.exists(events_file):
                with open(events_file, 'r') as f:
                    events = json.load(f)
        except:
            pass
        
        # Build system prompt based on user's requirements
        system_prompt = """You are an AI assistant helping someone find appropriate accommodation options. You will be provided with a location and the user's preferences. Always ask the user about where are they going, how long do they plan to stay, what's their preference/what do they like, what's their personality to help analyze the best result. Ask for users permission is important too.

<location>
{location}
</location>

<user_preferences>
{user_preferences}
</user_preferences>

<events>
{events}
</events>

Important guidelines for this task:

You should NOT help users find ways to crash in dormitories without permission, as this would involve trespassing on private property

You should NOT facilitate unauthorized access to student housing or university facilities

You should NOT provide information that could enable someone to illegally stay in places they don't have permission to be

Instead, you should:

Suggest legitimate accommodation options in the provided database

Provide helpful, legal alternatives while being respectful and not judgmental

Your response should acknowledge their location and preferences and then provide helpful legitimate dorm hosters info from the database.

same with the events recommendation
Use bullet points to list the options. Be concise and to the point.

Only provide options available in the website, they are all student hosters who have descriptions listed, match the most suitable one. Same for events. For example, an out going student is looking for a place to crash, you have two available dorms for that date, one host is quiet and sleeps early, the other one is talktive and loves to go out,. You match the user with the second one.

keep your answer precise and not too long. Use a vibe tone adjusting to the user's.

Write your response inside <answer> tags.""".format(
            location="Princeton",  # Default location, can be extracted from user query if needed
            user_preferences="",  # Will be extracted from conversation if mentioned
            events=json.dumps(events[:20], indent=2) if events else "[]",
            listings=json.dumps(listings[:20], indent=2) if listings else "[]"
        )
        
        # Add listings to the prompt after events section
        system_prompt += f"""

Available listings (student hosters):
{json.dumps(listings[:20], indent=2) if listings else "[]"}
"""
        
        # Build messages array with conversation history
        messages = []
        for msg in conversation_history[-10:]:  # Keep last 10 messages for context
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": message
        })
        
        # Call Claude API
        try:
            # Get temperature from environment or use default (0.7 = balanced, lower = more focused, higher = more creative)
            import os
            temperature = float(os.getenv('CLAUDE_TEMPERATURE', '0.7'))
            
            response = claude_client.messages.create(
                model=claude_model,
                max_tokens=200,  # Reduced for more concise responses
                temperature=temperature,  # Adjust temperature here (0.0-1.0, default: 0.7)
                system=system_prompt,
                messages=messages
            )
            
            # Extract response text safely
            if not response or not hasattr(response, 'content') or not response.content:
                raise ValueError("Invalid response structure from Claude API")
            
            response_text = ""
            if isinstance(response.content, list) and len(response.content) > 0:
                if hasattr(response.content[0], 'text'):
                    response_text = response.content[0].text
                elif isinstance(response.content[0], dict) and 'text' in response.content[0]:
                    response_text = response.content[0]['text']
                else:
                    response_text = str(response.content[0])
            else:
                response_text = str(response.content)
            
            if not response_text:
                raise ValueError("Empty response from Claude API")
            
            # Extract answer from <answer> tags if present
            import re
            answer_match = re.search(r'<answer>(.*?)</answer>', response_text, re.DOTALL)
            if answer_match:
                response_text = answer_match.group(1).strip()
            
            return jsonify({
                "success": True,
                "response": response_text
            }), 200
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            error_msg = str(e)
            print(f"Chatbot Claude API Error: {error_msg}")
            print(f"Error details: {error_details}")
            # Return error with details in debug mode, or simplified message in production
            return jsonify({
                "success": False,
                "error": error_msg,
                "details": error_details if app.debug else None
            }), 500
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        error_msg = str(e)
        print(f"Chatbot Error: {error_msg}")
        print(f"Error details: {error_details}")
        # Return error with details in debug mode, or simplified message in production
        return jsonify({
            "success": False,
            "error": error_msg,
            "details": error_details if app.debug else None
        }), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Starting Roomie API Server...")
    print(f"📡 API available at: http://localhost:{port}")
    print(f"🌐 Frontend: http://localhost:{port}")
    print(f"🔗 API endpoint: http://localhost:{port}/api/match")
    # Use 0.0.0.0 for production to accept connections from any interface
    app.run(debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true', port=port, host='0.0.0.0')

