"""
Dedalus - FastAPI Backend Server for Events
Stores and fetches event data, serving as the core API for events.
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date
import json
import os
from typing import List, Dict

app = FastAPI(title="Dedalus Events API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Event data storage
EVENTS_FILE = 'events_data/events.json'

# Ensure events_data directory exists
os.makedirs('events_data', exist_ok=True)

# Pydantic models
class Event(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    date: str  # ISO format date string
    time: str  # Time string (e.g., "18:00")
    location: str
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    category: str  # e.g., "academic", "social", "sports", "arts", "food"
    cost: Optional[float] = 0.0  # 0.0 means free
    organizer: str
    capacity: Optional[int] = None
    tags: List[str] = []
    image_url: Optional[str] = None
    registration_url: Optional[str] = None

class EventCreate(Event):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    location: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    category: Optional[str] = None
    cost: Optional[float] = None
    organizer: Optional[str] = None
    capacity: Optional[int] = None
    tags: Optional[List[str]] = None
    image_url: Optional[str] = None
    registration_url: Optional[str] = None

# Helper functions
def load_events() -> List[Dict]:
    """Load events from JSON file."""
    if os.path.exists(EVENTS_FILE):
        try:
            with open(EVENTS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return get_default_events()
    return get_default_events()

def save_events(events: List[Dict]):
    """Save events to JSON file."""
    with open(EVENTS_FILE, 'w') as f:
        json.dump(events, f, indent=2)

def get_default_events() -> List[Dict]:
    """Get default Princeton campus events."""
    return [
        {
            "id": 1,
            "title": "AI & Ethics Symposium",
            "description": "A full-day symposium on the intersection of artificial intelligence, policy, and human values. Hosted at Friend Center Auditorium.",
            "date": "2025-11-12",
            "time": "09:00",
            "location": "Friend Center Auditorium",
            "location_lat": 40.3500,
            "location_lng": -74.6530,
            "category": "academic",
            "cost": 0.0,
            "organizer": "Center for Human Values",
            "capacity": 200,
            "tags": ["academic", "free", "ai", "ethics"],
            "image_url": None,
            "registration_url": None
        },
        {
            "id": 2,
            "title": "Fall A Cappella Jam",
            "description": "Join Princeton's top vocal groups for a night of music, rhythm, and campus energy in Richardson Auditorium.",
            "date": "2025-11-14",
            "time": "19:00",
            "location": "Richardson Auditorium",
            "location_lat": 40.3510,
            "location_lng": -74.6550,
            "category": "arts",
            "cost": 10.0,
            "organizer": "Music Department",
            "capacity": 800,
            "tags": ["arts", "music", "a cappella"],
            "image_url": None,
            "registration_url": None
        },
        {
            "id": 3,
            "title": "Global Food Bazaar",
            "description": "Sample cuisines from student-run international booths at Frist Campus Center Lawn. A true feast for all cultures.",
            "date": "2025-11-16",
            "time": "12:00",
            "location": "Frist Campus Center Lawn",
            "location_lat": 40.3480,
            "location_lng": -74.6514,
            "category": "food",
            "cost": 8.0,
            "organizer": "International Student Association",
            "capacity": 500,
            "tags": ["food", "cultural", "social"],
            "image_url": None,
            "registration_url": None
        },
        {
            "id": 4,
            "title": "Yoga by the Lake",
            "description": "Early morning group yoga at Carnegie Lake to center your mind and body before finals week.",
            "date": "2025-11-09",
            "time": "07:00",
            "location": "Carnegie Lake",
            "location_lat": 40.3430,
            "location_lng": -74.6470,
            "category": "sports",
            "cost": 5.0,
            "organizer": "Wellness Center",
            "capacity": 50,
            "tags": ["sports", "wellness", "yoga", "outdoor"],
            "image_url": None,
            "registration_url": None
        },
        {
            "id": 5,
            "title": "Startup Coffee Chat",
            "description": "Meet founders, designers, and coders from across campus at Small World Coffee. Bring your ideas and curiosity.",
            "date": "2025-11-11",
            "time": "15:00",
            "location": "Small World Coffee",
            "location_lat": 40.3490,
            "location_lng": -74.6500,
            "category": "social",
            "cost": 0.0,
            "organizer": "Entrepreneurship Club",
            "capacity": 30,
            "tags": ["social", "free", "networking", "startup"],
            "image_url": None,
            "registration_url": None
        },
        {
            "id": 6,
            "title": "TigerHacks: Sustainability Challenge",
            "description": "Princeton's largest 24-hour hackathon focused on sustainable innovation and AI-driven green solutions.",
            "date": "2025-11-22",
            "time": "09:00",
            "location": "Friend Center",
            "location_lat": 40.3500,
            "location_lng": -74.6530,
            "category": "academic",
            "cost": 0.0,
            "organizer": "TigerHacks",
            "capacity": 300,
            "tags": ["academic", "free", "hackathon", "sustainability", "ai"],
            "image_url": None,
            "registration_url": None
        },
        {
            "id": 7,
            "title": "Outdoor Movie Night: La La Land",
            "description": "An open-air movie screening at Poe Field with popcorn, blankets, and fairy lights.",
            "date": "2025-11-13",
            "time": "19:00",
            "location": "Poe Field",
            "location_lat": 40.3450,
            "location_lng": -74.6480,
            "category": "arts",
            "cost": 7.0,
            "organizer": "Student Activities",
            "capacity": 200,
            "tags": ["arts", "movie", "outdoor", "social"],
            "image_url": None,
            "registration_url": None
        },
        {
            "id": 8,
            "title": "Intercollegiate Soccer Match",
            "description": "Cheer for the Princeton Tigers as they face off against Harvard in a thrilling soccer showdown.",
            "date": "2025-11-18",
            "time": "15:00",
            "location": "Roberts Stadium",
            "location_lat": 40.3450,
            "location_lng": -74.6480,
            "category": "sports",
            "cost": 0.0,
            "organizer": "Athletics Department",
            "capacity": 2000,
            "tags": ["sports", "free", "soccer", "competition"],
            "image_url": None,
            "registration_url": None
        },
        {
            "id": 9,
            "title": "Open Mic & Poetry Night",
            "description": "An intimate evening of poetry, acoustic music, and personal storytelling at Café Vivian.",
            "date": "2025-11-20",
            "time": "19:30",
            "location": "Café Vivian",
            "location_lat": 40.3485,
            "location_lng": -74.6510,
            "category": "arts",
            "cost": 5.0,
            "organizer": "Creative Writing Club",
            "capacity": 60,
            "tags": ["arts", "poetry", "music", "open mic"],
            "image_url": None,
            "registration_url": None
        },
        {
            "id": 10,
            "title": "Thanksgiving Potluck Dinner",
            "description": "A cozy community meal at the Graduate College dining hall — everyone brings a dish and a story to share.",
            "date": "2025-11-27",
            "time": "18:00",
            "location": "Graduate College Dining Hall",
            "location_lat": 40.3520,
            "location_lng": -74.6560,
            "category": "food",
            "cost": 10.0,
            "organizer": "Graduate Student Council",
            "capacity": 150,
            "tags": ["food", "social", "thanksgiving", "community"],
            "image_url": None,
            "registration_url": None
        }
    ]

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Dedalus Events API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Dedalus Events API"}

@app.get("/events", response_model=List[Event])
async def get_events(
    category: Optional[str] = Query(None, description="Filter by category"),
    date_from: Optional[str] = Query(None, description="Filter events from this date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter events until this date (YYYY-MM-DD)"),
    free_only: Optional[bool] = Query(False, description="Show only free events"),
    tags: Optional[str] = Query(None, description="Comma-separated tags to filter by")
):
    """Get all events with optional filters."""
    events = load_events()
    
    # Apply filters
    if category:
        events = [e for e in events if e.get("category", "").lower() == category.lower()]
    
    if date_from:
        events = [e for e in events if e.get("date", "") >= date_from]
    
    if date_to:
        events = [e for e in events if e.get("date", "") <= date_to]
    
    if free_only:
        events = [e for e in events if e.get("cost", 0) == 0.0]
    
    if tags:
        tag_list = [t.strip().lower() for t in tags.split(",")]
        events = [e for e in events if any(tag in [t.lower() for t in e.get("tags", [])] for tag in tag_list)]
    
    # Sort by date
    events.sort(key=lambda x: x.get("date", ""))
    
    return events

@app.get("/events/{event_id}", response_model=Event)
async def get_event(event_id: int):
    """Get a specific event by ID."""
    events = load_events()
    event = next((e for e in events if e.get("id") == event_id), None)
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return event

@app.post("/events", response_model=Event)
async def create_event(event: EventCreate):
    """Create a new event."""
    events = load_events()
    
    # Generate new ID
    max_id = max([e.get("id", 0) for e in events], default=0)
    new_id = max_id + 1
    
    event_dict = event.dict()
    event_dict["id"] = new_id
    events.append(event_dict)
    save_events(events)
    
    return event_dict

@app.put("/events/{event_id}", response_model=Event)
async def update_event(event_id: int, event_update: EventUpdate):
    """Update an existing event."""
    events = load_events()
    
    event_index = next((i for i, e in enumerate(events) if e.get("id") == event_id), None)
    
    if event_index is None:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Update only provided fields
    update_data = event_update.dict(exclude_unset=True)
    events[event_index].update(update_data)
    save_events(events)
    
    return events[event_index]

@app.delete("/events/{event_id}")
async def delete_event(event_id: int):
    """Delete an event."""
    events = load_events()
    
    event_index = next((i for i, e in enumerate(events) if e.get("id") == event_id), None)
    
    if event_index is None:
        raise HTTPException(status_code=404, detail="Event not found")
    
    deleted_event = events.pop(event_index)
    save_events(events)
    
    return {"message": "Event deleted successfully", "event": deleted_event}

@app.get("/events/categories/list")
async def get_categories():
    """Get list of all event categories."""
    events = load_events()
    categories = list(set([e.get("category", "") for e in events if e.get("category")]))
    return {"categories": sorted(categories)}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Dedalus Events API Server...")
    print("📡 API available at: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)

