# HackPrinceton 2025 - Dorm Matching Platform

A smart dorm matching platform that connects visitors with hosts using AI-powered compatibility matching. Built for HackPrinceton 2025.

## 🎯 Features

- **AI-Powered Matching**: Uses Dedalus Labs AI agent to find the most compatible hosts based on visitor profiles
- **User Authentication**: Secure login/signup system with role-based access (visitor/host)
- **Host Listings**: Hosts can create and manage their dorm listings with availability dates, capacity, and preferences
- **Date Range Support**: Search for hosts available on specific dates or date ranges
- **Smart Search**: Find available hosts based on dates and capacity requirements
- **Reviews & Ratings**: Visitors can leave reviews and ratings for hosts
- **Event Integration**: FastAPI backend for event management and recommendations
- **Image Uploads**: Hosts can upload images for their listings

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **AI Agent**: Dedalus Labs
- **Events API**: FastAPI
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Session-based auth
- **Storage**: JSON files (users, listings, events)

## 📋 Prerequisites

- Python 3.9+
- pip
- Virtual environment (recommended)

## 🚀 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/celloii/HackPrinceton-2025.git
cd HackPrinceton-2025
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the root directory:

```env
# Dedalus Labs API Key
DEDALUS_API_KEY=your_dedalus_api_key_here

# Flask Secret Key (for sessions)
SECRET_KEY=your_secret_key_here

# Optional: Anthropic API Key (for Claude features)
ANTHROPIC_API_KEY=your_claude_api_key_here
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Optional: Server Port
PORT=5000
```

### 5. Initialize Data Files

The application will automatically create the following files on first run:
- `users.json` - User accounts
- `listings.json` - Host listings
- `events_data/events.json` - Event data

## 🏃 Running the Application

### Option 1: Run Main Server Only

```bash
python server.py
```

The server will start on `http://localhost:5000`

### Option 2: Run with Events System

```bash
./start_events_system.sh
```

This starts both the FastAPI events server (port 8000) and the Flask server (port 5000).

### Option 3: Run Alternative Server

```bash
python main.py
```

## 📡 API Endpoints

### Authentication
- `POST /api/auth/signup` - Create new user account
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/check` - Check current session

### Listings
- `GET /api/listings` - Get all listings
- `GET /api/listing/<id>` - Get specific listing
- `POST /api/listing/create` - Create new listing (host only)
- `PUT /api/listing/<id>` - Update listing (host only)
- `DELETE /api/listing/<id>` - Delete listing (host only)

### Matching
- `POST /api/match` - Find compatible hosts using AI
  - Body: `{ "visitor_query": "...", "date_needed": "YYYY-MM-DD" }`

### Reviews
- `POST /api/listing/<id>/review` - Add review to listing
  - Body: `{ "reviewer_name": "...", "rating": 5, "comment": "..." }`

### Events
- `GET /api/events` - Get all events
- `POST /api/events` - Create new event
- `GET /api/events/<id>` - Get specific event

## 📁 Project Structure

```
HackPrinceton-2025/
├── server.py              # Main Flask server
├── main.py                # Alternative Flask server
├── auth.py                # Authentication logic
├── tools.py               # Listing management utilities
├── ai_agent.py            # Dedalus AI agent integration
├── dedalus_events.py      # FastAPI events server
├── nova_act.py            # AI orchestration layer
├── knot.py                # API configuration management
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in git)
├── users.json             # User data (not in git)
├── listings.json          # Listing data (not in git)
├── events_data/           # Event data directory
│   └── events.json
├── uploads/               # Uploaded images
├── index.html             # Main landing page
├── login.html             # Login page
├── signup.html            # Signup page
├── dashboard.html         # Unified dashboard
├── host_dashboard.html     # Host dashboard
├── listing.html           # Listing detail page
├── events.html            # Events page
└── README.md              # This file
```

## 🔧 Configuration

### Port Configuration

If port 5000 is already in use (e.g., by macOS AirPlay Receiver), you can:

1. **Change the port** in `server.py`:
   ```python
   port = int(os.environ.get('PORT', 5001))  # Change default port
   ```

2. **Disable AirPlay Receiver** (macOS):
   ```bash
   ./disable_airplay.sh
   ```

3. **Use environment variable**:
   ```bash
   PORT=5001 python server.py
   ```

## 🧪 Testing

Run the test suite:

```bash
python test_backend.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 Notes

- The application uses JSON files for data storage (suitable for development/demo)
- For production, consider migrating to a proper database (PostgreSQL, MongoDB, etc.)
- API keys should be kept secure and never committed to git
- The `.env` file is already in `.gitignore`

## 🐛 Troubleshooting

### Port Already in Use
- Check what's using the port: `lsof -i :5000`
- Kill the process or change the port

### Import Errors
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### API Key Issues
- Verify `.env` file exists and contains correct keys
- Check that environment variables are loaded correctly

## 📄 License

This project was created for HackPrinceton 2025.

## 👥 Team

Built by the HackPrinceton 2025 team.

---

**Happy Hacking! 🚀**
