"""
Flask API server that integrates with the existing Dedalus Labs AI agent.
Run with: python server.py
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import asyncio
import json
from ai_agent import run_matching_agent

app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for frontend requests

@app.route('/')
def index():
    """Serve the frontend HTML."""
    return send_from_directory('.', 'index.html')

@app.route('/api/match', methods=['POST'])
def match_visitor():
    """
    API endpoint that uses the existing Dedalus Labs agent to match visitors with hosts.
    
    Expects JSON:
    {
        "visitor_query": "I need a quiet place, early bedtime...",
        "date_needed": "2025-11-08"
    }
    
    Returns:
    {
        "success": true,
        "matches": { ... }  // Result from Dedalus agent
    }
    """
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

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "Dorm Matching API"}), 200

if __name__ == '__main__':
    print("🚀 Starting Dorm Matching API Server...")
    print("📡 API available at: http://localhost:5000")
    print("🌐 Frontend: http://localhost:5000")
    print("🔗 API endpoint: http://localhost:5000/api/match")
    app.run(debug=True, port=5000)

