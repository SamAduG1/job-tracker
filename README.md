# JobTracker

A full-stack web application for tracking job applications with analytics dashboard.

## Features

- Track job applications with detailed information
- View application statistics and response rates
- Filter and search applications
- Visual dashboard with charts
- Status pipeline tracking (Applied → Interview → Offer)

## Tech Stack

**Frontend:**
- React + Vite
- Tailwind CSS
- Recharts for data visualization

**Backend:**
- Flask + SQLAlchemy
- PostgreSQL (production) / SQLite (development)
- RESTful API

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Backend runs on http://localhost:5000

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on http://localhost:5173

## API Endpoints

```
GET    /api/applications       - Get all applications
GET    /api/applications/:id   - Get one application
POST   /api/applications       - Create application
PUT    /api/applications/:id   - Update application
DELETE /api/applications/:id   - Delete application
GET    /api/stats              - Get dashboard statistics
```

## Deployment

- Frontend: Vercel
- Backend: Render
- Database: PostgreSQL on Render

## Author

Sam Adu-Gyapong
