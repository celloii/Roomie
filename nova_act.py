"""
Nova Act - AI Orchestration Layer
Orchestrates AI logic: queries Dedalus for events, uses Claude to filter/summarize them,
and formats responses for users based on their interests.
"""
import httpx
import json
from typing import List, Dict, Optional
from knot import Knot

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("Warning: anthropic package not installed. Claude AI features will be limited.")


class NovaAct:
    """AI orchestration for event recommendations."""
    
    def __init__(self):
        self.knot = Knot()
        self.claude_client = None
        
        if ANTHROPIC_AVAILABLE:
            try:
                claude_config = self.knot.get_claude_config()
                self.claude_client = Anthropic(api_key=claude_config["api_key"])
                self.claude_model = claude_config["model"]
            except Exception as e:
                print(f"Warning: Could not initialize Claude client: {e}")
    
    async def get_events_from_dedalus(
        self,
        category: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        free_only: bool = False,
        tags: Optional[str] = None
    ) -> List[Dict]:
        """Query Dedalus API for events."""
        dedalus_url = self.knot.get_dedalus_url("events")
        
        params = {}
        if category:
            params["category"] = category
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        if free_only:
            params["free_only"] = "true"
        if tags:
            params["tags"] = tags
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(dedalus_url, params=params)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Error fetching events from Dedalus: {e}")
            return []
    
    async def get_ai_recommendations(
        self,
        user_interests: str,
        events: List[Dict],
        max_recommendations: int = 5
    ) -> Dict:
        """
        Use Claude AI to filter and recommend events based on user interests.
        
        Args:
            user_interests: Description of user's interests (e.g., "I love technology, free events, and social gatherings")
            events: List of events from Dedalus
            max_recommendations: Maximum number of recommendations to return
        
        Returns:
            Dictionary with recommended events and reasoning
        """
        if not self.claude_client or not events:
            # Fallback: return all events if Claude is not available
            return {
                "recommendations": events[:max_recommendations],
                "reasoning": "AI recommendations unavailable. Showing all events.",
                "ai_enabled": False
            }
        
        # Prepare events summary for Claude
        events_summary = []
        for event in events:
            events_summary.append({
                "id": event.get("id"),
                "title": event.get("title"),
                "description": event.get("description"),
                "date": event.get("date"),
                "time": event.get("time"),
                "location": event.get("location"),
                "category": event.get("category"),
                "cost": event.get("cost", 0),
                "tags": event.get("tags", [])
            })
        
        prompt = f"""You are an event recommendation assistant for a college campus platform.

User's interests: {user_interests}

Available events:
{json.dumps(events_summary, indent=2)}

Please:
1. Analyze which events best match the user's interests
2. Rank them from most relevant to least relevant
3. Provide a brief explanation for each recommendation
4. Highlight any special features (e.g., free events, nearby locations, popular events)

Return your response as a JSON object with this structure:
{{
    "recommendations": [
        {{
            "event_id": <id>,
            "relevance_score": <0.0-1.0>,
            "reasoning": "<brief explanation>",
            "highlights": ["<feature1>", "<feature2>"]
        }}
    ],
    "summary": "<overall summary of recommendations>"
}}

Focus on the top {max_recommendations} most relevant events."""
        
        try:
            message = self.claude_client.messages.create(
                model=self.claude_model,
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse Claude's response
            response_text = message.content[0].text
            
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                ai_response = json.loads(json_match.group(0))
            else:
                # Fallback parsing
                ai_response = {"recommendations": [], "summary": response_text}
            
            # Map recommendations back to full event data
            recommendations = []
            for rec in ai_response.get("recommendations", [])[:max_recommendations]:
                event_id = rec.get("event_id")
                event = next((e for e in events if e.get("id") == event_id), None)
                if event:
                    recommendations.append({
                        "event": event,
                        "relevance_score": rec.get("relevance_score", 0.5),
                        "reasoning": rec.get("reasoning", ""),
                        "highlights": rec.get("highlights", [])
                    })
            
            return {
                "recommendations": recommendations,
                "summary": ai_response.get("summary", ""),
                "ai_enabled": True
            }
            
        except Exception as e:
            print(f"Error getting AI recommendations: {e}")
            # Fallback: return all events
            return {
                "recommendations": [{"event": e, "relevance_score": 0.5, "reasoning": "", "highlights": []} 
                                   for e in events[:max_recommendations]],
                "summary": "AI recommendations temporarily unavailable.",
                "ai_enabled": False
            }
    
    async def get_filtered_events(
        self,
        user_interests: Optional[str] = None,
        category: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        free_only: bool = False,
        tags: Optional[str] = None,
        use_ai: bool = True,
        max_results: int = 10
    ) -> Dict:
        """
        Main orchestration method: get events from Dedalus and optionally filter with AI.
        
        Returns:
            Dictionary with events and AI recommendations if enabled
        """
        # Step 1: Query Dedalus for events
        events = await self.get_events_from_dedalus(
            category=category,
            date_from=date_from,
            date_to=date_to,
            free_only=free_only,
            tags=tags
        )
        
        if not events:
            return {
                "events": [],
                "recommendations": None,
                "summary": "No events found matching your criteria."
            }
        
        # Step 2: If AI is enabled and user interests provided, get AI recommendations
        recommendations = None
        if use_ai and user_interests and self.claude_client:
            recommendations = await self.get_ai_recommendations(
                user_interests=user_interests,
                events=events,
                max_recommendations=max_results
            )
        
        return {
            "events": events,
            "recommendations": recommendations,
            "total_count": len(events)
        }
    
    async def summarize_event(self, event_id: int) -> Optional[str]:
        """Get an AI-generated summary of a specific event."""
        events = await self.get_events_from_dedalus()
        event = next((e for e in events if e.get("id") == event_id), None)
        
        if not event or not self.claude_client:
            return None
        
        prompt = f"""Provide a brief, engaging summary of this campus event:

Title: {event.get('title')}
Description: {event.get('description')}
Date: {event.get('date')} at {event.get('time')}
Location: {event.get('location')}
Category: {event.get('category')}
Cost: ${event.get('cost', 0):.2f}
Tags: {', '.join(event.get('tags', []))}

Create a 2-3 sentence summary that highlights why students would want to attend this event."""
        
        try:
            message = self.claude_client.messages.create(
                model=self.claude_model,
                max_tokens=200,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            return message.content[0].text
        except Exception as e:
            print(f"Error generating event summary: {e}")
            return None
    
    async def get_combined_recommendations(
        self,
        user_preferences: str,
        date_needed: Optional[str] = None,
        max_hosts: int = 5,
        max_events: int = 5
    ) -> Dict:
        """
        Get AI-powered combined recommendations for both hosts and events based on user preferences.
        
        Args:
            user_preferences: Description of user's preferences (e.g., "I need a quiet place to stay and love tech events")
            date_needed: Date the user needs accommodation (YYYY-MM-DD)
            max_hosts: Maximum number of host recommendations
            max_events: Maximum number of event recommendations
        
        Returns:
            Dictionary with recommended hosts and events with AI reasoning
        """
        # Get hosts from listings
        from tools import load_listings
        all_hosts = load_listings()
        
        # Filter hosts by date if provided
        if date_needed:
            available_hosts = [
                h for h in all_hosts 
                if date_needed in h.get("available_dates", [])
            ]
        else:
            available_hosts = all_hosts
        
        # Get events
        events = await self.get_events_from_dedalus()
        
        if not self.claude_client:
            # Fallback: return all without AI
            return {
                "hosts": available_hosts[:max_hosts],
                "events": events[:max_events],
                "reasoning": "AI recommendations unavailable.",
                "ai_enabled": False
            }
        
        # Prepare data for Claude
        hosts_summary = []
        for host in available_hosts:
            hosts_summary.append({
                "id": host.get("id"),
                "name": host.get("name"),
                "description": host.get("description", ""),
                "dorm_vibe": host.get("dorm_vibe", ""),
                "interests": host.get("interests", ""),
                "capacity": host.get("capacity", 1),
                "available_dates": host.get("available_dates", [])
            })
        
        events_summary = []
        for event in events:
            events_summary.append({
                "id": event.get("id"),
                "title": event.get("title"),
                "description": event.get("description"),
                "date": event.get("date"),
                "time": event.get("time"),
                "location": event.get("location"),
                "category": event.get("category"),
                "cost": event.get("cost", 0),
                "tags": event.get("tags", [])
            })
        
        prompt = f"""You are an AI assistant helping a student find the best accommodation and events on campus.

User's Preferences: {user_preferences}
Date Needed: {date_needed or "Not specified"}

Available Hosts:
{json.dumps(hosts_summary, indent=2)}

Available Events:
{json.dumps(events_summary, indent=2)}

Please:
1. Analyze which hosts best match the user's preferences (considering dorm_vibe, interests, and description)
2. Analyze which events best match the user's interests
3. Consider how hosts and events might complement each other (e.g., a host near event locations)
4. Rank hosts and events separately from most relevant to least relevant
5. Provide brief reasoning for each recommendation

Return your response as a JSON object with this structure:
{{
    "hosts": [
        {{
            "host_id": <id>,
            "relevance_score": <0.0-1.0>,
            "reasoning": "<brief explanation>",
            "highlights": ["<feature1>", "<feature2>"]
        }}
    ],
    "events": [
        {{
            "event_id": <id>,
            "relevance_score": <0.0-1.0>,
            "reasoning": "<brief explanation>",
            "highlights": ["<feature1>", "<feature2>"]
        }}
    ],
    "combined_insights": "<overall insights about how hosts and events work together>"
}}

Focus on the top {max_hosts} hosts and top {max_events} events."""
        
        try:
            message = self.claude_client.messages.create(
                model=self.claude_model,
                max_tokens=3000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse Claude's response
            response_text = message.content[0].text
            
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                ai_response = json.loads(json_match.group(0))
            else:
                ai_response = {"hosts": [], "events": [], "combined_insights": response_text}
            
            # Map recommendations back to full data
            recommended_hosts = []
            for rec in ai_response.get("hosts", [])[:max_hosts]:
                host_id = rec.get("host_id")
                host = next((h for h in available_hosts if h.get("id") == host_id), None)
                if host:
                    recommended_hosts.append({
                        "host": host,
                        "relevance_score": rec.get("relevance_score", 0.5),
                        "reasoning": rec.get("reasoning", ""),
                        "highlights": rec.get("highlights", [])
                    })
            
            recommended_events = []
            for rec in ai_response.get("events", [])[:max_events]:
                event_id = rec.get("event_id")
                event = next((e for e in events if e.get("id") == event_id), None)
                if event:
                    recommended_events.append({
                        "event": event,
                        "relevance_score": rec.get("relevance_score", 0.5),
                        "reasoning": rec.get("reasoning", ""),
                        "highlights": rec.get("highlights", [])
                    })
            
            return {
                "hosts": recommended_hosts,
                "events": recommended_events,
                "combined_insights": ai_response.get("combined_insights", ""),
                "ai_enabled": True
            }
            
        except Exception as e:
            print(f"Error getting combined recommendations: {e}")
            # Fallback
            return {
                "hosts": [{"host": h, "relevance_score": 0.5, "reasoning": "", "highlights": []} 
                          for h in available_hosts[:max_hosts]],
                "events": [{"event": e, "relevance_score": 0.5, "reasoning": "", "highlights": []} 
                           for e in events[:max_events]],
                "combined_insights": "AI recommendations temporarily unavailable.",
                "ai_enabled": False
            }

