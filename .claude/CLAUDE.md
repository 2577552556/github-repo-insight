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

```
GITHUB_TOKEN=           # GitHub API Token (可选)
DEEPSEEK_API_KEY=       # DeepSeek API Key (AI评估用)
OPENAI_API_KEY=         # OpenAI API Key (备用)
```

Frontend

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

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

# 工作流程

## 服务启动脚本

项目使用脚本管理服务，位置：`scripts/`

| 脚本 | 功能 |
|------|------|
| `scripts/start-backend.sh` | 启动后端服务 (端口 8000) |
| `scripts/start-frontend.sh` | 启动前端服务 (端口 3000) |

### 启动步骤

```bash
# 1. 启动后端（使用 nohup 后台执行）
bash scripts/start-backend.sh

# 2. 启动前端（使用 nohup 后台执行）
bash scripts/start-frontend.sh
```

### 技术要求

- 服务必须使用 `nohup` 后台执行，确保终端关闭后服务仍运行
- 进程 PID 写入日志便于跟踪
- 启动前精确杀死旧进程，避免端口占用

### 日志位置

所有日志输出到 `logs/` 目录：

| 日志文件 | 内容 |
|----------|------|
| `logs/backend.log` | 后端服务日志 |
| `logs/frontend.log` | 前端服务日志 |

## 开发修改流程

每次修改代码后：

1. **重启服务**
   ```bash
   bash scripts/start-backend.sh   # 重启后端
   bash scripts/start-frontend.sh  # 重启前端
   ```

2. **测试功能**
   - 后端健康检查: `curl http://localhost:8000/health`
   - 前端: http://localhost:3000
   - API 测试: `curl -X POST http://localhost:8000/api/analyze -H "Content-Type: application/json" -d '{"url":"https://github.com/microsoft/vscode"}'`

3. **提交代码**
   ```bash
   git status
   git add <files>
   git commit -m "<中文描述>"
   git push origin main
   ```

## AI 评估服务

使用 LangGraph + DeepSeek 构建 AI Agent：

- **架构**: LangGraph Agent with DeepSeek
- **配置**: `DEEPSEEK_API_KEY` 环境变量
- **Fallback**: 无 API Key 时使用规则评估

## 环境要求

- 所有文档使用中文
- 日志使用中文
- 提交信息使用中文（或中英混合）

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

上传到github仓库里面：https://github.com/2577552556/github-repo-insight.git 

每次修改代码都需要启动前后端，日志放到logs/内，日志指的是进程的日志

所有文档和日志都用中文

# Repository Evaluation Architecture

## Design Principle

本项目不仅是 GitHub 数据展示工具。

本项目本质上是：

Repository Evaluation Engine（仓库评估引擎）

因此：

评分逻辑属于核心业务规则。

业务规则优先级高于代码实现。

任何评分逻辑修改必须先进行审计与验证。

禁止直接修改评分公式。

---

## Evaluation Pipeline

Repository URL

↓

GitHub Data Collection

↓

Repository Type Detection

↓

Base Score Calculation

↓

Dynamic Template Selection

↓

Specialized Score Calculation

↓

AI Evaluation

↓

Final Score

↓

Frontend Visualization

---

## Repository Type Detection

系统必须优先识别项目类型。

支持：

* Personal Project
* Community OSS
* Corporate OSS
* Open Core
* Source Available
* AI Platform
* Infrastructure Project
* SDK / Library
* Developer Tool

项目允许同时命中多个类型。

例如：

FastGPT

=

Corporate OSS

*

AI Platform

*

Source Available

---

## Mixed Type Support

项目类型不是互斥关系。

示例：

Vue

= Community OSS + Developer Tool

Kubernetes

= Community OSS + Infrastructure

FastGPT

= Corporate OSS + AI Platform + Source Available

Dify

= Corporate OSS + AI Platform

GitLab

= Open Core + Corporate OSS

评分时必须支持多标签组合。

禁止仅使用单一项目类型。

---

## Current Core Dimensions

保留现有维度：

* Popularity
* Activity
* Community
* Issue Governance
* PR Governance
* Engineering
* Release Maintenance

禁止随意删除维度。

新增维度必须经过设计评审。

---

## Dynamic Scoring Template

禁止所有项目使用同一评分标准。

系统必须根据项目类型动态调整权重。

示例：

Corporate OSS

降低：

* PR Governance
* Community

提高：

* Engineering
* Release Maintenance

Community OSS

提高：

* Community
* PR Governance
* Issue Governance

AI Platform

增加：

* AI Capability
* Model Ecosystem
* Deployment Capability

---

## Specialized Score Layer

对于特定项目增加专项评分。

AI Project：

* RAG
* Agent
* Workflow
* Knowledge Base
* Tool Calling
* Model Ecosystem
* Deployment

Open Core：

* Community Completeness
* Commercial Transparency

Infrastructure：

* Stability
* Release Quality
* Ecosystem Adoption

---

## License Rules

禁止：

NOASSERTION = 无许可证

必须区分：

* OSI License
* Source Available
* Open Core
* Custom License

Source Available 不得直接判定为低质量项目。

---

## Explainability Rules

所有 AI 分析结论必须：

1. 有数据依据
2. 有推理链
3. 有适用项目类型
4. 有置信度

禁止：

# PR 少

社区差

# Issue 响应慢

项目不健康

# License 非 OSI

项目风险高

这类未经验证的推断。

---

## Benchmark Repository Set

任何评分逻辑修改后必须重新分析：

* FastGPT
* Dify
* Kubernetes
* Vue
* PostgreSQL
* LangChain

输出：

旧评分

新评分

变化原因

如果出现明显异常：

停止开发

重新审计评分体系

禁止继续编码。

---

# Claude Working Rules

## Audit Before Code

对于以下内容：

* 评分公式
* 权重
* Repository Type Detection
* AI Evaluation Prompt
* Explain Engine

必须遵循：

Audit

↓

Design

↓

Plan

↓

Implement

禁止直接进入编码阶段。

---

## PLAN Mode First

当任务涉及：

* 评分逻辑
* AI分析逻辑
* Repository Type Detection
* Prompt工程

必须优先输出：

PLAN

内容包括：

1. 问题分析
2. 风险分析
3. 设计方案
4. 数据结构变化
5. API变化
6. 前端变化
7. 测试方案

确认后再编码。

---

## Evaluation System Refactor Workflow

评分系统改造流程：

Phase 1

审计现有指标

↓

Phase 2

验证 Benchmark Repository

↓

Phase 3

设计新规则

↓

Phase 4

设计数据结构

↓

Phase 5

设计 API

↓

Phase 6

实施代码修改

↓

Phase 7

回归测试

---

## Regression Test Requirements

每次评分逻辑修改后必须验证：

FastGPT

Dify

Vue

Kubernetes

PostgreSQL

LangChain

检查：

* Repository Type
* Health Score
* Grade
* AI Analysis

生成对比报告。

---

## Engineering Rule

评分逻辑：

backend/app/services/scoring/

Repository Type Detection：

backend/app/services/repository_type/

AI Explain Engine：

backend/app/services/ai_analysis/

禁止在 API Route 中实现评分逻辑。

禁止在 Frontend 中实现评分逻辑。

所有评分计算必须在 Backend Service Layer 完成。

---

## Long-term Goal

本项目目标不是：

GitHub Repository Viewer

而是：

GitHub Repository Insight Platform

支持：

* 多类型仓库识别
* 动态评分模型
* AI专项评估
* Explainable AI Analysis
* 企业级仓库体检
