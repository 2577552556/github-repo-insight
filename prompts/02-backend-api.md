# Backend API Implementation

## Prompt Used

Implement the backend API for GitHub repository analysis.

## Implementation Details

### Core Layer
- `backend/app/core/config.py` - Settings with pydantic-settings
- `backend/app/core/exceptions.py` - Custom exceptions (InvalidURLError, RepositoryNotFoundError, etc.)

### GitHub Client
- `backend/app/clients/github.py` - Async httpx client for GitHub API
- `backend/app/utils/url_parser.py` - URL parsing utility

### Service Layer
- `backend/app/services/github.py` - GitHub data fetching service
- `backend/app/services/health_score.py` - Health score calculation (0-100 based on 4 dimensions)
- `backend/app/services/ai_evaluation.py` - AI evaluation with OpenAI + rule-based fallback

### API Route
- `backend/app/api/routes/analyze.py` - POST /api/analyze endpoint

## Health Score Dimensions

1. **Popularity** (0-25): Stars count
2. **Activity** (0-25): Recent updates
3. **Community** (0-25): Forks, watchers
4. **Maintenance** (0-25): Issue ratio

## AI Evaluation

- Uses OpenAI API when API key is available
- Falls back to rule-based evaluation otherwise
- Grades: A (85-100), B (70-84), C (50-69), D (30-49), F (0-29)