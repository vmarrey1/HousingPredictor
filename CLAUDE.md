# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

UC Berkeley Four Year Plan Generator - a web application helping students create personalized four-year academic plans. Uses Google Gemini AI for intelligent course scheduling.

## Architecture

```
Frontend (Next.js 14 + TypeScript)
         ↓
    Nginx (reverse proxy, rate limiting)
         ↓
Backend (Flask + Gunicorn)
         ↓
    MongoDB + CSV course data + Google Gemini API
```

**Backend** (`/backend/app.py`): Single Flask file handling all API routes, authentication, plan generation, and AI integration.

**Frontend** (`/frontend/app/`): Next.js App Router with pages for landing (`page.tsx`), schedule display (`schedule/page.tsx`), schedules list (`schedules/page.tsx`), and auth (`auth/page.tsx`).

## Development Commands

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux
pip install -r requirements.txt
python app.py                  # Runs on http://localhost:5000
```

### Frontend
```bash
cd frontend
npm install
npm run dev      # Development server on http://localhost:3000
npm run build    # Production build
npm run lint     # ESLint
```

### Production (Docker)
```bash
./build.sh       # Build Docker image
./deploy.sh      # Deploy with docker-compose
docker-compose logs -f berkeley-planner  # View logs
```

## Key API Endpoints

- `POST /api/auth/signup|login|logout` - Authentication
- `GET /api/auth/me` - Current user
- `GET /api/majors` - List all majors
- `POST /api/generate-plan` - Generate 4-year plan (main feature)
- `POST /api/course-options` - Get course alternatives for requirements
- `POST /api/ai-suggestions` - AI-powered course suggestions
- `GET|POST|PUT|DELETE /api/schedules` - CRUD for saved schedules

## Environment Variables

Backend requires `.env` with:
- `GEMINI_API_KEY` - Google Gemini API key (required for AI features)
- `SECRET_KEY` - Flask session secret
- `MONGODB_URI` - MongoDB connection string
- `FLASK_ENV` - Set to `production` for prod

Frontend uses `NEXT_PUBLIC_API_BASE` for production API URL.

## Data Flow

1. Course data loaded from `courses-report.2025-09-04 (7).csv` at startup
2. Major requirements are hardcoded in `app.py` (100+ majors)
3. Plan generation uses Gemini AI with fallback to basic algorithm
4. User schedules stored in MongoDB with indexes on `email` and `user_id`

## Important Patterns

- Frontend proxies `/api/*` to backend in development via `next.config.js`
- Production uses `NEXT_PUBLIC_API_BASE` environment variable for API calls
- CORS configured for `berkeleyfouryearplan.com` and localhost origins
- Session cookies use `SameSite=None`, `Secure`, `HttpOnly` in production
- Nginx handles rate limiting: 10 req/s for API, 30 req/s general

## Testing Locally

Run backend and frontend in separate terminals. Frontend at `:3000` automatically proxies API calls to backend at `:5000`.
