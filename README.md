# GitHub Repository Health Check

A full-stack web application that analyzes public GitHub repositories and generates comprehensive health reports with AI-powered evaluation.

## Features

- **Repository URL Input**: Validate and analyze any public GitHub repository
- **Repository Metadata**: Display stars, forks, watchers, issues, language, and more
- **Language Distribution**: Interactive pie chart showing programming language breakdown
- **Health Score**: Calculate 0-100 score based on popularity, activity, community, and maintenance
- **AI Evaluation**: AI-powered repository assessment with grade (A-F) and summary
- **Responsive Design**: Works on desktop and mobile with dark mode support

## Tech Stack

### Frontend
- Next.js 15 (React 19)
- TypeScript (strict mode)
- TailwindCSS
- shadcn/ui
- Recharts

### Backend
- Python 3.12+
- FastAPI
- Pydantic v2
- httpx (async)

## Architecture

```
Frontend (Next.js 15 + React 19)
├── app/                    # Next.js pages
├── components/             # React components
│   ├── ui/                 # shadcn/ui components
│   └── *.tsx              # Feature components
├── services/api.ts        # API service layer
├── hooks/useAnalysis.ts   # Analysis state hook
└── types/index.ts         # TypeScript definitions

Backend (Python 3.12+ + FastAPI)
├── main.py                # FastAPI entry point
├── app/
│   ├── api/routes/        # API route handlers
│   ├── services/          # Business logic
│   ├── schemas/           # Pydantic models
│   ├── clients/           # GitHub API client
│   ├── core/              # Config, exceptions
│   └── utils/             # URL parser
└── requirements.txt

Docker
├── Dockerfile.backend
├── Dockerfile.frontend
└── docker-compose.yml
```

## API Design

### Analyze Repository

**Endpoint**: `POST /api/analyze`

**Request**:
```json
{
  "url": "https://github.com/microsoft/vscode"
}
```

**Response**:
```json
{
  "repository": {
    "name": "vscode",
    "owner": "microsoft",
    "full_name": "microsoft/vscode",
    "description": "Visual Studio Code",
    "stars": 150000,
    "forks": 25000,
    "watchers": 150000,
    "open_issues": 5000,
    "language": "TypeScript",
    "created_at": "2015-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "default_branch": "main"
  },
  "languages": {
    "TypeScript": 70.5,
    "JavaScript": 20.0,
    "CSS": 9.5
  },
  "health_score": {
    "score": 95,
    "dimensions": {
      "popularity": 25,
      "activity": 25,
      "community": 23,
      "maintenance": 22
    }
  },
  "ai_score": {
    "score": 92,
    "grade": "A",
    "summary": "Excellent repository with strong community..."
  }
}
```

## Health Score Calculation

The health score (0-100) is calculated based on four dimensions:

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Popularity | 0-25 | Based on star count |
| Activity | 0-25 | Based on recent updates |
| Community | 0-25 | Based on forks and watchers |
| Maintenance | 0-25 | Based on issue ratio |

### Scoring Standards

| Grade | Score Range | Description |
|-------|-------------|-------------|
| A | 85-100 | Excellent - Highly popular, actively maintained |
| B | 70-84 | Good - Well maintained with decent community |
| C | 50-69 | Average - Moderate activity and community |
| D | 30-49 | Below Average - Low activity or community |
| F | 0-29 | Poor - New, abandoned, or minimal engagement |

## AI Evaluation

The AI evaluation uses OpenAI API when `OPENAI_API_KEY` is configured. If no API key is present, a rule-based fallback is used.

## Setup Guide

### Prerequisites

- Python 3.12+
- Node.js 20+
- Docker (optional)

### Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Docker Setup

```bash
docker compose up --build
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GITHUB_TOKEN` | GitHub API token for increased rate limit | No |
| `OPENAI_API_KEY` | OpenAI API key for AI evaluation | No |
| `NEXT_PUBLIC_API_URL` | Backend API URL (default: http://localhost:8000) | No |

## Error Handling

The API handles the following error cases:

| Status | Error | Description |
|--------|-------|-------------|
| 400 | Invalid URL | GitHub URL format is incorrect |
| 404 | Not Found | Repository does not exist |
| 429 | Rate Limit | GitHub API rate limit exceeded |
| 502 | API Error | GitHub API returned an error |
| 503 | Network Error | Network connectivity issue |

## Development

### Testing Backend

```bash
cd backend
pytest
```

### Building Frontend

```bash
cd frontend
npm run build
```

## Project Structure

```
github-repo-insight/
├── frontend/
│   ├── app/
│   ├── components/
│   ├── services/
│   ├── hooks/
│   ├── lib/
│   └── types/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   ├── schemas/
│   │   ├── clients/
│   │   ├── core/
│   │   └── utils/
│   └── main.py
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── README.md
└── CLAUDE.md
```

## License

MIT