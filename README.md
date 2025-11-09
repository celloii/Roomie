# Roomie

Find a couch, floor, or spare bed in another student's dorm when you're traveling for hackathons, conferences, or campus events — without blowing your budget.

DormSwap makes it simple to host, swap, or find short-term stays with other students. Think "Airbnb for college students," but lightweight and AI-assisted.

## Why this exists

College students are constantly on the move — hackathons, case comps, auditions, interviews. Hotels are pricey and far from campus. Meanwhile, lots of dorm rooms have a spare mattress for a night or two.

DormSwap simplifies the logistics: post availability, browse nearby hosts, and get AI-recommended matches based on vibe, schedule, and preferences.

## What's in this MVP

Host listings: simple form with dates, dorm name, a short "vibe"/rules blurb.

Visitor requests: message a host; hosts can accept/decline.

AI matching (MVP): rank hosts by compatibility using text similarity on interests/sleep schedule/dorm vibe.

Mock database: JSON file storage for listings while we iterate.

Upload support: basic uploads/ folder for profile photos or docs (optional in MVP).

## Hackathon Tracks (and how we use them)

Dedalus — we adapt the "Travel Agent" idea to search available dorm rooms instead of flights/hotels. The agent pulls host profiles and returns ranked matches.

Amazon — "improving campus life." Explore Amazon Nova Act to auto-discover campus events/restaurants near you, and AI Studio for the demo video workflow.

YC — "Rebuild Airbnb with AI." We put AI at the center of matching and decision support, not just as a bolt-on feature.

## Tech Stack

Frontend: simple HTML/CSS or lightweight React (TBD as we iterate)

Backend: Python Flask

AI / Matching: TF-IDF + cosine similarity (baseline), optional Dedalus agent orchestration

Data: JSON file (listings.json) for MVP

Env/Secrets: .env for API keys (do not commit)
