# CLAUDE.md

# Project

Github Repository Health Check

Build a full-stack web application that analyzes a public GitHub repository and generates a repository health report.

Time limit: 48 hours.

Goal:

A user enters a GitHub repository URL and receives:

* Repository information
* Repository metrics
* Language distribution
* Health score
* AI-generated repository evaluation

The project should prioritize:

1. Functionality
2. Simplicity
3. Readability
4. Engineering quality

Avoid over-engineering.

---

# Tech Stack

## Frontend

Use:

* Next.js 15
* React 19
* TypeScript
* TailwindCSS
* shadcn/ui
* Recharts

Requirements:

* Strict TypeScript
* Responsive Design
* Dark Mode
* Component-driven Architecture

Do not use:

* Redux
* MobX
* Complex state management

Prefer:

* React Hooks
* Context only if necessary

---

## Backend

Use:

* Python 3.12+
* FastAPI
* Pydantic v2
* httpx

Requirements:

* Async-first
* Typed APIs
* Clear service layer

Do not use:

* Django
* Flask

---

# Project Structure

github-health-check/

├── frontend/
│
│   ├── app/
│   ├── components/
│   ├── services/
│   ├── hooks/
│   ├── lib/
│   └── types/
│
├── backend/
│
│   ├── app/
│   │
│   │   ├── api/
│   │   ├── services/
│   │   ├── schemas/
│   │   ├── clients/
│   │   ├── core/
│   │   └── utils/
│   │
│   └── main.py
│
├── prompts/
│
├── screenshots/
│
├── docs/
│
├── docker-compose.yml
│
├── README.md
│
└── CLAUDE.md

---

# Architecture

Backend Architecture

API Layer
↓
Service Layer
↓
Github Client
↓
Github REST API

No business logic inside routes.

Bad:

@app.post("/analyze")

# 100 lines business logic

Good:

@app.post("/analyze")
return await analyze_service.run()

---

Frontend Architecture

Page
↓
Components
↓
Services
↓
Backend API

Pages should focus on UI composition.

Business logic belongs in:

frontend/services

frontend/lib

---

# Repository Analysis Flow

User Input

https://github.com/microsoft/vscode

↓

Frontend Validation

↓

Backend API

↓

GitHub API

↓

Metrics Calculation

↓

Health Score

↓

AI Score

↓

Frontend Visualization

---

# Core Features

## Feature 1

Repository URL Input

User enters:

https://github.com/owner/repo

Validate:

* valid URL
* public repository

Show friendly errors.

---

## Feature 2

Repository Metadata

Fetch from:

GET /repos/{owner}/{repo}

Display:

* repository name
* owner
* description
* stars
* forks
* watchers
* open issues
* created time
* updated time
* default branch

---

## Feature 3

Language Distribution

Fetch:

GET /repos/{owner}/{repo}/languages

Calculate percentages.

Display with Pie Chart.

Example:

TypeScript 55%

Python 30%

Go 15%

---

## Feature 4

Health Score

Generate repository health score.

Dimensions:

Popularity

Activity

Community

Maintenance

Output:

0 ~ 100

Example:

{
"score": 86
}

---

## Feature 5

Visualization Dashboard

Display:

Metric Cards

Language Pie Chart

Health Score Card

AI Score Card

Repository Summary

---

## Feature 6

AI Evaluation

Optional.

Use OpenAI-compatible API.

Input:

* repository description
* stars
* forks
* languages
* update time

Output:

{
"score": 89,
"grade": "A",
"summary": "Repository is actively maintained and has a strong community."
}

Fallback:

Rule-based evaluation if no API key exists.

The application must still work without AI.

---

# API Design

## Analyze Repository

POST /api/analyze

Request

{
"url": "https://github.com/microsoft/vscode"
}

Response

{
"repository": {},
"languages": {},
"health_score": {},
"ai_score": {}
}

---

# Frontend Components

RepositoryInput

MetricCard

RepositoryInfo

LanguageChart

HealthScoreCard

AIScoreCard

LoadingState

ErrorState

AnalysisDashboard

Components should be reusable.

---

# Coding Standards

## TypeScript

Enable strict mode.

Do not use:

any

Prefer:

unknown

interfaces

Example:

interface RepositoryMetrics {
stars: number;
forks: number;
}

---

## React

Prefer functional components.

Prefer hooks.

Keep components under 300 lines.

Extract reusable logic into hooks.

---

## Python

Follow:

PEP8

Black

Ruff

Type hints are mandatory.

Example:

async def analyze_repository(
owner: str,
repo: str
) -> RepositoryAnalysis:
...

---

# Error Handling

Must handle:

Invalid URL

Repository Not Found

Rate Limit Exceeded

Github API Error

Network Error

Unexpected Exception

Return meaningful error messages.

Do not expose stack traces.

---

# Environment Variables

Backend

GITHUB_TOKEN=

OPENAI_API_KEY=

Frontend

NEXT_PUBLIC_API_URL=

---

# Version Control

Use GitHub.

Commit code frequently.

Never submit all work in one commit.

---

## Branch Strategy

main

develop

feature/*

Examples:

feature/backend-api

feature/dashboard-ui

feature/health-score

feature/ai-analysis

---

## Commit Convention

Use Conventional Commits.

Allowed:

feat:

fix:

refactor:

docs:

test:

style:

chore:

Examples:

feat: implement github repository analysis

feat: add language distribution chart

fix: handle invalid repository url

refactor: extract github api client

docs: update deployment instructions

---

## Commit Frequency

Create commits after major milestones.

Recommended:

1. Project Initialization

2. Backend Setup

3. Github Integration

4. Frontend Form

5. Dashboard

6. Charts

7. Health Score

8. AI Score

9. Docker

10. Documentation

Expected:

10~20 commits

Minimum:

8 commits

---

# Git Ignore

Must include:

node_modules/

.next/

dist/

coverage/

.env

.env.*

**pycache**/

.pytest_cache/

.venv/

.idea/

.vscode/

---

# Testing

Backend:

pytest

Frontend:

basic component tests

Focus on:

Repository Parsing

Github API Integration

Health Score Calculation

---

# Docker

Provide:

backend Dockerfile

frontend Dockerfile

docker-compose.yml

Application should start using:

docker compose up

---

# Documentation

README must contain:

Project Overview

Tech Stack

Architecture

Setup Guide

Environment Variables

Run Instructions

Screenshots

Prompt Engineering Process

AI Evaluation Logic

Future Improvements

---

# AI Coding Traceability

Create:

prompts/

Store prompts used during development.

Examples:

01-project-init.md

02-fastapi-api.md

03-nextjs-dashboard.md

04-health-score.md

05-ai-analysis.md

---

# Screenshots

Create:

screenshots/

Include:

Claude Code conversations

Implementation screenshots

UI screenshots

Folder structure screenshots

---

# Development Workflow

For every major feature:

1. Write Prompt

2. Generate Code

3. Review Code

4. Commit Code

5. Save Prompt

6. Capture Screenshot

Traceability must exist between:

Prompt
↓
Code
↓
Commit

---

# Release

Before submission:

Update README

Run Tests

Build Frontend

Build Backend

Create Git Tag

Example:

v1.0.0

Provide:

GitHub Repository URL

README

Source Code

Prompt Records

Screenshots

---

# Success Criteria

The project is considered complete if:

✓ User can input GitHub repository URL

✓ Backend can retrieve GitHub repository data

✓ Frontend can display repository information

✓ Language chart works

✓ Health score works

✓ AI evaluation works

✓ Docker deployment works

✓ README is complete

✓ Git history is meaningful

✓ Prompt records are included

✓ Screenshots are included

Focus on delivering a complete and maintainable MVP within 48 hours.
