# HackPrinceton 2025 - Dorm Matching Platform

A dorm matching platform that connects visitors with hosts using AI. Built for HackPrinceton 2025.

## What it does

Visitors can search for hosts based on dates and get AI-powered compatibility matches. Hosts can create listings with their availability, dorm vibe, and preferences. The system uses Dedalus Labs to match visitors with the most compatible hosts.

## Getting started

First, clone the repo and set up a virtual environment:

```bash
git clone https://github.com/celloii/HackPrinceton-2025.git
cd HackPrinceton-2025
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

You'll need a `.env` file with your API keys:

```env
DEDALUS_API_KEY=your_dedalus_api_key_here
SECRET_KEY=your_secret_key_here
```

The app will create `users.json` and `listings.json` automatically when you first run it.

## Running it

Just run:

```bash
python server.py
```

Then go to `http://localhost:5000` in your browser.

If you want to run the events system too, use:

```bash
./start_events_system.sh
```

## Tech stuff

- Flask for the backend
- Dedalus Labs for AI matching
- FastAPI for the events API
- JSON files for data storage (for now)

## Notes

If port 5000 is already in use (like on macOS with AirPlay), you can either change the port in `server.py` or disable AirPlay. There's a script for that: `./disable_airplay.sh`

The app stores everything in JSON files right now, which is fine for development but you'd probably want a real database for production.

Built for HackPrinceton 2025.
