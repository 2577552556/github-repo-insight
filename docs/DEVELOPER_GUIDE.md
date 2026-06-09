# GitHub Repository Insight - 开发者手册

## 目录

1. [项目结构](#1-项目结构)
2. [核心模块](#2-核心模块)
3. [评分引擎](#3-评分引擎)
4. [AI 分析流程](#4-ai-分析流程)
5. [数据库设计](#5-数据库设计)
6. [API 参考](#6-api-参考)
7. [开发指南](#7-开发指南)
8. [测试](#8-测试)

---

## 1. 项目结构

### 1.1 整体架构

```
github-repo-insight/
├── frontend/                     # Next.js 15 前端
│   ├── app/                      # App Router 页面
│   │   ├── page.tsx              # 首页
│   │   ├── layout.tsx            # 根布局
│   │   └── providers.tsx         # React Provider
│   ├── components/               # React 组件
│   │   ├── AnalysisDashboard.tsx # 分析结果仪表板
│   │   ├── HealthScoreCard.tsx   # 健康评分卡片
│   │   ├── AIAnalysisCard.tsx     # AI 解读卡片
│   │   ├── HistorySidebar.tsx     # 历史侧边栏
│   │   └── ...
│   ├── hooks/                    # 自定义 Hooks
│   │   ├── useAnalysis.ts        # 流式分析状态
│   │   ├── useWorkspace.ts        # 工作区状态
│   │   └── useSettings.ts         # 设置状态
│   ├── services/                  # API 服务
│   │   ├── api.ts                # 分析 API
│   │   └── settingsApi.ts         # 设置 API
│   └── types/                     # TypeScript 类型
│
├── backend/                      # Python FastAPI 后端
│   ├── app/
│   │   ├── api/routes/           # API 路由
│   │   │   ├── analyze.py         # 分析接口
│   │   │   ├── analysis.py         # 历史记录接口
│   │   │   └── settings.py         # 设置接口
│   │   ├── services/              # 业务逻辑
│   │   │   ├── health_score.py     # 评分引擎
│   │   │   ├── ai_maturity_score.py # AI 成熟度
│   │   │   ├── ai_evaluation.py   # AI 解读
│   │   │   ├── github.py          # GitHub 数据获取
│   │   │   ├── database.py         # 数据库服务
│   │   │   ├── settings_service.py # 设置服务
│   │   │   └── credential_manager.py # 凭据加密
│   │   ├── schemas/               # Pydantic 模型
│   │   │   └── analyze.py          # 数据模型定义
│   │   ├── clients/                # 外部 API 客户端
│   │   │   └── github.py            # GitHub API 客户端
│   │   ├── core/                   # 核心配置
│   │   │   ├── config.py            # Pydantic Settings
│   │   │   └── exceptions.py        # 自定义异常
│   │   └── utils/                   # 工具函数
│   │       └── url_parser.py        # URL 解析
│   ├── main.py                      # FastAPI 入口
│   └── requirements.txt             # Python 依赖
│
└── scripts/                        # 服务脚本
```

### 1.2 关键文件说明

| 文件 | 说明 |
|------|------|
| `backend/main.py` | FastAPI 应用入口，注册路由和中间件 |
| `backend/app/services/health_score.py` | 评分引擎核心，7 维度评分逻辑 |
| `backend/app/services/ai_evaluation.py` | AI 解读服务，LangGraph 状态机 |
| `backend/app/services/github.py` | GitHub 数据获取，高并发并行请求 |
| `frontend/hooks/useAnalysis.ts` | SSE 流式分析状态管理 |

---

## 2. 核心模块

### 2.1 前端核心模块

#### useAnalysis Hook

```typescript
// frontend/hooks/useAnalysis.ts
const { status, result, error, analyze, reset } = useAnalysis();
```

**状态类型**:
- `idle` - 初始状态
- `streaming` - 流式分析中
- `success` - 分析完成
- `error` - 分析失败

#### useWorkspace Hook

```typescript
// frontend/hooks/useWorkspace.ts
const { history, activeRecord, loadRecord, deleteRecord, refreshHistory } = useWorkspace();
```

### 2.2 后端核心模块

#### GitHub 服务 (github.py)

```python
# 并行获取多个数据源
metrics = await github_service.get_repository_metrics(owner, repo)
```

#### 评分引擎 (health_score.py)

```python
# 计算健康评分
health_score = await health_score_service.calculate(repo_info, languages, metrics)
```

#### AI 解读 (ai_evaluation.py)

```python
# 生成 AI 解读
analysis = await ai_evaluation_service.interpret(
    repository=repo_info,
    languages=languages,
    metrics=metrics,
    health_score=health_score
)
```

---

## 3. 评分引擎

### 3.1 评分维度

满分 100 分，7 个维度：

| 维度 | 满分 | 评分依据 |
|---|---|---|
| Popularity | 25 | Stars + Forks + Watchers |
| Activity | 25 | 更新时间 + Commits 频率 |
| Community | 15 | Contributors + Issue 关闭率 |
| Issue Governance | 10 | 响应时间 + 关闭率 |
| PR Governance | 10 | 合并时间 + 合并率 |
| Engineering | 10 | License + Topics + Description |
| Release/Maintenance | 5 | 发布节奏 + 维护风险 |

### 3.2 项目类型检测

支持 9 种类型：

1. **AI_PLATFORM** - AI 平台/应用
2. **INFRASTRUCTURE** - 基础设施
3. **SDK_LIBRARY** - SDK/工具库
4. **DEVELOPER_TOOL** - 开发者工具
5. **SOURCE_AVAILABLE** - 源码可见
6. **OPENCORE** - 核心开源 + 商业扩展
7. **CORPORATE** - 企业主导开源
8. **COMMUNITY** - 社区驱动开源
9. **PERSONAL** - 个人项目

### 3.3 AI 成熟度专项

针对 AI Platform 项目，检测 7 项能力：

- RAG (检索增强生成)
- Agent (智能体)
- Workflow (工作流)
- Knowledge Base (知识库)
- Tool Calling (工具调用)
- Model Ecosystem (模型生态)
- Deployment (部署能力)

### 3.4 新增评分维度

如需新增评分维度：

1. 在 `HealthScoreDimensions` 中添加字段
2. 在 `health_score.py` 中实现计算逻辑
3. 更新 `calculate_health_score` 函数
4. 在前端 `HealthScoreCard` 中添加展示

---

## 4. AI 分析流程

### 4.1 整体流程

```
用户请求
    │
    ▼
analyze.py (API 入口)
    │
    ├─► github.py (获取仓库数据)
    │       ├─► get_repository()
    │       ├─► get_languages()
    │       └─► get_metrics() // 并行执行
    │
    ├─► health_score.py (规则引擎评分)
    │       ├─► detect_project_type()
    │       ├─► calculate_dimensions()
    │       └─► calculate_ai_maturity() // 仅 AI Platform
    │
    ├─► ai_evaluation.py (AI 解读)
    │       └─► LangGraph StateGraph
    │               └─► interpret_node (DeepSeek)
    │
    ▼
返回 AnalyzeResponse
```

### 4.2 SSE 流式推送

```typescript
// 前端: api.ts
const response = await fetch('/api/analyze/stream?url=...');
const reader = response.body.getReader();
```

后端分 6 个阶段推送：
1. `repository` - 仓库信息
2. `languages` - 语言分布
3. `metrics` - 扩展指标
4. `health_score` - 健康评分
5. `ai_score` - AI 评分
6. `ai_analysis` - AI 解读（可选）

### 4.3 LangGraph 状态机

```python
# ai_evaluation.py
state = {
    "repository": RepositoryInfo,
    "languages": LanguageDistribution,
    "metrics": RepositoryMetrics,
    "health_score": HealthScore,
    "summary": str,
    "strengths": list[str],
    "risks": list[str],
    "suggestions": list[str],
    "iteration": int,
}
```

---

## 5. 数据库设计

### 5.1 analysis_records 表

```sql
CREATE TABLE analysis_records (
    id TEXT PRIMARY KEY,
    repository_url TEXT NOT NULL,
    repository_name TEXT NOT NULL,
    owner TEXT NOT NULL,
    full_name TEXT NOT NULL,
    score INTEGER,
    grade TEXT(1),
    type_detection TEXT,  -- JSON
    status TEXT NOT NULL DEFAULT 'processing',
    error_message TEXT,
    analysis_version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    result_json TEXT,  -- JSON
);
```

### 5.2 credentials 表

```sql
CREATE TABLE credentials (
    id TEXT PRIMARY KEY,
    provider TEXT NOT NULL,      -- 'github', 'deepseek'
    name TEXT NOT NULL,           -- 'token', 'api_key'
    encrypted_value TEXT NOT NULL,  -- AES 密文
    iv TEXT NOT NULL,            -- 初始化向量
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
);
```

---

## 6. API 参考

### 6.1 分析接口

#### POST /api/analyze

同步分析仓库，返回完整报告。

**请求**:
```json
{
  "url": "https://github.com/microsoft/vscode"
}
```

**响应**: `AnalyzeResponse` 对象

#### GET /api/analyze/stream

SSE 流式分析，边分析边推送结果。

**参数**: `url` - 仓库 URL

**响应**: SSE 流

### 6.2 历史记录接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/analysis` | POST | 创建分析记录 |
| `/api/analysis/history` | GET | 获取历史列表 |
| `/api/analysis/{id}` | GET | 获取单条记录 |
| `/api/analysis/{id}` | DELETE | 删除记录 |
| `/api/analysis/{id}/reanalyze` | POST | 重新分析 |

### 6.3 设置接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/settings` | GET | 获取配置状态 |
| `/api/settings` | PUT | 更新配置 |

---

## 7. 开发指南

### 7.1 环境搭建

```bash
# 1. 克隆代码
git clone https://github.com/2577552556/github-repo-insight.git
cd github-repo-insight

# 2. 安装后端依赖
cd backend
pip install -r requirements.txt

# 3. 安装前端依赖
cd ../frontend
npm install
```

### 7.2 开发调试

```bash
# 启动后端（支持热重载）
cd backend
python -m uvicorn main:app --reload --port 8000

# 启动前端（支持热重载）
cd frontend
npm run dev
```

### 7.3 代码规范

#### Python

- 使用 Type Hints
- 遵循 PEP 8
- 使用 Pydantic v2 模型

#### TypeScript

- 启用 Strict Mode
- 避免使用 `any`
- 使用 Interface 而非 Type Alias（简单对象）

### 7.4 新增 API 路由

1. 在 `backend/app/api/routes/` 创建新文件
2. 定义 Pydantic Request/Response 模型
3. 注册路由到 `main.py`

```python
# backend/app/api/routes/example.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/example")
async def example_endpoint():
    return {"message": "example"}
```

```python
# backend/main.py
from app.api.routes import example

app.include_router(example.router, prefix="/api")
```

### 7.5 新增前端组件

1. 在 `frontend/components/` 创建组件文件
2. 使用 TypeScript 定义 Props 接口
3. 在需要的地方导入使用

---

## 8. 测试

### 8.1 后端测试

```bash
cd backend

# 运行所有测试
pytest

# 运行单个测试文件
pytest tests/test_health_score.py

# 查看覆盖率
pytest --cov=app tests/
```

### 8.2 前端构建

```bash
cd frontend

# 开发构建
npm run build

# TypeScript 类型检查
npx tsc --noEmit
```

### 8.3 手动测试流程

1. 启动服务: `bash scripts/start-backend.sh && bash scripts/start-frontend.sh`
2. 访问 http://localhost:3000
3. 输入仓库 URL 进行分析
4. 检查分析结果和日志

---

## 附录：技术栈

### 前端

- Next.js 15 (App Router)
- React 19
- TypeScript (Strict Mode)
- TailwindCSS
- shadcn/ui
- Recharts
- Lucide Icons

### 后端

- Python 3.12+
- FastAPI
- Pydantic v2
- SQLAlchemy
- httpx
- LangGraph
- DeepSeek (ChatDeepSeek)

### 数据库

- SQLite (本地文件)

---

*最后更新: 2026-06-10*