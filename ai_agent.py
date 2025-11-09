# ai_agent.py
import os
import sys
import asyncio
import json
import re
from dotenv import load_dotenv

# Fix for Python 3.9 compatibility with dedalus_labs (TypeAlias was added in Python 3.10)
if sys.version_info < (3, 10):
    import typing
    if not hasattr(typing, 'TypeAlias'):
        # Add TypeAlias compatibility for Python 3.9
        typing.TypeAlias = type(None)

# Try to import dedalus_labs, but make it optional
try:
    from dedalus_labs import AsyncDedalus, DedalusRunner
    DEDALUS_AVAILABLE = True
    print("✓ Dedalus Labs AI agent is available and ready to use")
except ImportError as e:
    DEDALUS_AVAILABLE = False
    print(f"Warning: dedalus_labs not available: {e}. Will use Claude API directly for AI matching.")
    AsyncDedalus = None
    DedalusRunner = None

# Try to import Claude API
try:
    from anthropic import Anthropic
    from knot import Knot
    CLAUDE_AVAILABLE = True
except ImportError as e:
    CLAUDE_AVAILABLE = False
    print(f"Warning: Claude API not available: {e}. AI matching will use fallback logic.")

from tools import find_available_hosts # Import your mock database tool

# Ensure DEDALUS_API_KEY is set in your environment or .env file
load_dotenv() # Load environment variables from .env file

async def run_matching_agent(visitor_query: str, date_needed: str) -> str:
    """
    Runs the Dedalus AI agent to find and rank the most compatible host.
    Falls back to simple matching if dedalus_labs is not available.
    """
    if not DEDALUS_AVAILABLE:
        # Fallback: improved matching with conflict detection
        import json
        hosts_json = find_available_hosts(visitor_date_range=date_needed)
        hosts = json.loads(hosts_json) if isinstance(hosts_json, str) else hosts_json
        
        # Define keyword opposites/conflicts
        opposites = {
            'quiet': ['loud', 'noisy', 'party', 'social', 'night owl', 'late night'],
            'loud': ['quiet', 'silent', 'peaceful', 'calm', 'early', 'early bedtime'],
            'early': ['late', 'night owl', 'late night', 'night'],
            'late': ['early', 'early riser', 'early bedtime', 'morning'],
            'study': ['party', 'social', 'loud', 'noisy'],
            'party': ['quiet', 'study', 'peaceful', 'calm'],
            'social': ['quiet', 'study', 'solitary', 'peaceful'],
            'night owl': ['early', 'early riser', 'early bedtime', 'morning'],
            'peaceful': ['loud', 'noisy', 'party', 'social']
        }
        
        matches = []
        query_lower = visitor_query.lower()
        query_words = set(query_lower.split())
        
        for host in hosts:
            score = 0.3  # Lower base score - must earn points
            reasoning_parts = []
            
            # Check dorm_vibe
            if host.get('dorm_vibe'):
                vibe_lower = host['dorm_vibe'].lower()
                vibe_words = set(vibe_lower.split())
                
                # Check for matches
                matches_found = query_words.intersection(vibe_words)
                if matches_found:
                    score += 0.4  # Strong match bonus
                    reasoning_parts.append(f"vibe matches: {', '.join(matches_found)}")
                
                # Check for conflicts/opposites
                has_conflict = False
                for query_word in query_words:
                    if query_word in opposites:
                        for opposite in opposites[query_word]:
                            if opposite in vibe_lower:
                                score -= 0.5  # Heavy penalty for conflicts
                                has_conflict = True
                                reasoning_parts.append(f"conflict: {query_word} vs {opposite}")
                
                # Partial word matches (e.g., "quiet" in "quiet space")
                for query_word in query_words:
                    if len(query_word) > 3 and query_word in vibe_lower:
                        if query_word not in matches_found:
                            score += 0.2
                            reasoning_parts.append(f"partial vibe match: {query_word}")
            
            # Check interests
            if host.get('interests'):
                interests_lower = host['interests'].lower()
                interests_words = set(interests_lower.split())
                
                # Check for matches
                interest_matches = query_words.intersection(interests_words)
                if interest_matches:
                    score += 0.3
                    reasoning_parts.append(f"interests match: {', '.join(interest_matches)}")
                
                # Partial word matches
                for query_word in query_words:
                    if len(query_word) > 3 and query_word in interests_lower:
                        if query_word not in interest_matches:
                            score += 0.15
                            reasoning_parts.append(f"partial interest match: {query_word}")
            
            # Normalize score to 0.0-1.0 range
            score = max(0.0, min(1.0, score))
            
            reasoning = "Basic keyword matching (AI unavailable)"
            if reasoning_parts:
                reasoning = "; ".join(reasoning_parts)
            
            matches.append({
                "host_id": host.get('id', 0),
                "name": host.get('name', 'Unknown'),
                "compatibility_score": score,
                "reasoning": reasoning
            })
        
        # Sort by score (highest first), and filter out very low scores
        matches.sort(key=lambda x: x['compatibility_score'], reverse=True)
        # Only return matches with score > 0.2 to avoid showing terrible matches
        matches = [m for m in matches if m['compatibility_score'] > 0.2]
        
        return json.dumps({"ranked_matches": matches})
    
    # 1. Try to use Dedalus Labs, but fall back if it fails
    try:
        dedalus_api_key = os.environ.get("DEDALUS_API_KEY")
        if not dedalus_api_key:
            raise ValueError("DEDALUS_API_KEY not set, using fallback matching")
        
        # Use cloud endpoint explicitly (don't use localhost from DEDALUS_BASE_URL env var)
        client = AsyncDedalus(api_key=dedalus_api_key, base_url='https://api.dedaluslabs.ai')
        runner = DedalusRunner(client)

        # 2. Define the Master Prompt (The core instructions for the AI)
        prompt = f"""
        You are an expert compatibility agent for a college dorm-matching app.
        Your goal is to match a visitor with the most compatible host.
        
        Visitor's Request: The visitor needs accommodation on {date_needed}. 
        Their profile is: "{visitor_query}"

        STEPS:
        1. First, you MUST call the 'find_available_hosts' tool using the date_needed as the 'visitor_date_range' argument.
        2. Analyze the 'dorm_vibe' and 'interests' of each returned host against the Visitor's Profile.
        3. Rank the hosts from BEST MATCH to POOREST MATCH.
        4. **Crucially, output the results as a single, valid JSON object** containing the ranked list of matches.
        
        JSON Format MUST be:
        {{
            "ranked_matches": [
                {{ "host_id": <id>, "name": "<name>", "compatibility_score": <float 0.0-1.0>, "reasoning": "<short explanation>" }},
                ... (other hosts)
            ]
        }}
        """
        
        # 3. Execute the agent with the tool
        # The Dedalus Runner handles deciding when to call find_available_hosts based on the prompt.
        response = await runner.run(
            input=prompt,
            tools=[find_available_hosts],  # Pass your local Python function here
            model="google/gemini-2.5-pro",   # Use a strong model for reasoning/tool use
            max_steps=5 # Prevent infinite loops in the hackathon environment
        )
        
        # The final_output is the structured JSON generated by the agent
        # It may be wrapped in markdown code blocks, so extract JSON if needed
        output = response.final_output
        if isinstance(output, str):
            # Remove markdown code blocks if present
            import re
            # Try to extract JSON from markdown code block (non-greedy match)
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', output, re.DOTALL)
            if json_match:
                output = json_match.group(1)
            else:
                # Try to find JSON object directly (greedy match for nested objects)
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', output, re.DOTALL)
                if json_match:
                    output = json_match.group(0)
                else:
                    # Last resort: find anything that looks like JSON
                    json_match = re.search(r'\{.*\}', output, re.DOTALL)
                    if json_match:
                        output = json_match.group(0)
        return output
    except Exception as e:
        # If Dedalus fails (no API key, network error, etc.), use fallback
        print(f"Dedalus Labs failed ({e}), using fallback matching logic")
        # Fall through to fallback logic below
        pass
    
    # Fallback: improved matching with conflict detection (same as above)
    import json
    hosts_json = find_available_hosts(visitor_date_range=date_needed)
    hosts = json.loads(hosts_json) if isinstance(hosts_json, str) else hosts_json
    
    # Define keyword opposites/conflicts
    opposites = {
        'quiet': ['loud', 'noisy', 'party', 'social', 'night owl', 'late night'],
        'loud': ['quiet', 'silent', 'peaceful', 'calm', 'early', 'early bedtime'],
        'early': ['late', 'night owl', 'late night', 'night'],
        'late': ['early', 'early riser', 'early bedtime', 'morning'],
        'study': ['party', 'social', 'loud', 'noisy'],
        'party': ['quiet', 'study', 'peaceful', 'calm'],
        'social': ['quiet', 'study', 'solitary', 'peaceful'],
        'night owl': ['early', 'early riser', 'early bedtime', 'morning'],
        'peaceful': ['loud', 'noisy', 'party', 'social']
    }
    
    matches = []
    query_lower = visitor_query.lower()
    query_words = set(query_lower.split())
    
    for host in hosts:
        score = 0.3  # Lower base score - must earn points
        reasoning_parts = []
        
        # Check dorm_vibe
        if host.get('dorm_vibe'):
            vibe_lower = host['dorm_vibe'].lower()
            vibe_words = set(vibe_lower.split())
            
            # Check for matches
            matches_found = query_words.intersection(vibe_words)
            if matches_found:
                score += 0.4  # Strong match bonus
                reasoning_parts.append(f"vibe matches: {', '.join(matches_found)}")
            
            # Check for conflicts/opposites
            has_conflict = False
            for query_word in query_words:
                if query_word in opposites:
                    for opposite in opposites[query_word]:
                        if opposite in vibe_lower:
                            score -= 0.5  # Heavy penalty for conflicts
                            has_conflict = True
                            reasoning_parts.append(f"conflict: {query_word} vs {opposite}")
            
            # Partial word matches (e.g., "quiet" in "quiet space")
            for query_word in query_words:
                if len(query_word) > 3 and query_word in vibe_lower:
                    if query_word not in matches_found:
                        score += 0.2
                        reasoning_parts.append(f"partial vibe match: {query_word}")
        
        # Check interests
        if host.get('interests'):
            interests_lower = host['interests'].lower()
            interests_words = set(interests_lower.split())
            
            # Check for matches
            interest_matches = query_words.intersection(interests_words)
            if interest_matches:
                score += 0.3
                reasoning_parts.append(f"interests match: {', '.join(interest_matches)}")
            
            # Partial word matches
            for query_word in query_words:
                if len(query_word) > 3 and query_word in interests_lower:
                    if query_word not in interest_matches:
                        score += 0.15
                        reasoning_parts.append(f"partial interest match: {query_word}")
        
        # Normalize score to 0.0-1.0 range
        score = max(0.0, min(1.0, score))
        
        reasoning = "AI-powered matching"
        if reasoning_parts:
            reasoning = "; ".join(reasoning_parts)
        
        matches.append({
            "host_id": host.get('id', 0),
            "name": host.get('name', 'Unknown'),
            "compatibility_score": score,
            "reasoning": reasoning
        })
    
    # Sort by score (highest first), and filter out very low scores
    matches.sort(key=lambda x: x['compatibility_score'], reverse=True)
    # Only return matches with score > 0.2 to avoid showing terrible matches
    matches = [m for m in matches if m['compatibility_score'] > 0.2]
    
    return json.dumps({"ranked_matches": matches})

# Example of how your API endpoint would call this function:
# if __name__ == "__main__":
#     match_data = asyncio.run(run_matching_agent(
#         visitor_query="I need a quiet place, I have classes early and go to bed by 10 PM.",
#         date_needed="2025-11-08"
#     ))
#     print(match_data)