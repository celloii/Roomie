# main.py — DormSwap Backend Server
from flask import Flask, send_from_directory, jsonify, request, make_response
from tools import load_listings, get_default_listings, find_available_hosts
import json

app = Flask(__name__, static_folder='.', static_url_path='')

# -------------------- HTML ROUTES --------------------

@app.get("/")
def home():
    """Serve the landing page."""
    return send_from_directory(".", "index.html")

@app.get("/dashboard")
def dashboard():
    """Serve the student dashboard page."""
    return send_from_directory(".", "dashboard.html")

@app.get("/login")
def login_page():
    """Serve the login page."""
    return send_from_directory(".", "login.html")

@app.get("/host")
@app.get("/host/dashboard")
def host_dashboard():
    """Serve the host dashboard page."""
    return send_from_directory(".", "host_dashboard.html")

@app.get("/favicon.ico")
def favicon():
    """Prevent 404 for missing favicon."""
    try:
        return send_from_directory(".", "favicon.ico")
    except Exception:
        return make_response(("", 204))

# -------------------- API ROUTES --------------------

@app.get("/api/listings")
def api_listings():
    """Return all listings."""
    return jsonify(load_listings())

@app.get("/api/find_hosts")
def api_find_hosts():
    """Find available hosts for a given date."""
    date = request.args.get("date")
    if not date:
        return jsonify({"error": "Missing 'date' parameter"}), 400

    result = find_available_hosts(date)

    # If result is JSON string (from older version), parse it
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            result = {"result": result}
    return jsonify(result)

@app.get("/api/auth/check")
def api_auth_check():
    """
    Placeholder auth check endpoint.
    In future: verify user session/cookie and return user info.
    """
    return jsonify({"authenticated": False, "user": None})

# -------------------- ADMIN / RESET --------------------

@app.post("/api/reset")
def api_reset():
    """Reset listings file to default sample data."""
    from tools import save_listings
    save_listings(get_default_listings())
    return jsonify({"message": "Listings reset to default."})

# -------------------- MAIN ENTRY --------------------

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

