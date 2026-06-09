# GitHub Repository Health Check

> 仓库体检平台 - 基于规则引擎 + AI 的开源项目健康度评估工具

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个全栈 Web 应用，对 GitHub 仓库进行多维度健康度评估，生成可视化体检报告。

## 功能特点

- **仓库信息提取** - 自动解析 GitHub 仓库元数据（Stars、Forks、Watchers、Issues 等）
- **语言分布分析** - 交互式饼图展示编程语言占比
- **九维度健康评分** - 基于流行度、活跃度、社区、Issue治理、PR治理、工程规范、发布维护等维度计算综合评分
- **AI 深度解读** - DeepSeek AI 分析优势、风险与改进建议
- **响应式设计** - 支持桌面和移动设备，深色模式

## 快速开始

### 方式一：一条命令启动（推荐）

```bash
# 克隆仓库
git clone https://github.com/2577552556/github-repo-insight.git
cd github-repo-insight

# 启动后端（自动安装依赖）
bash scripts/start-backend.sh

# 启动前端（新终端）
bash scripts/start-frontend.sh

# 打开浏览器访问 http://localhost:3000
```

### 方式二：Docker 启动

```bash
# 复制环境变量模板
cp .env.example .env

# 启动所有服务
docker compose up --build

# 访问 http://localhost:3000
```

## 手动安装（详细步骤）

### 前置要求

- Python 3.12+
- Node.js 20+
- npm 或 yarn
- Git

### 1. 克隆项目

```bash
git clone https://github.com/2577552556/github-repo-insight.git
cd github-repo-insight
```

### 2. 配置后端

```bash
cd backend

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 复制环境变量（可选，有默认配置）
cp ../.env.example .env
```

### 3. 配置前端

```bash
cd ../frontend

# 安装依赖
npm install
```

### 4. 启动服务

```bash
# 终端 1: 启动后端
cd backend
.venv\Scripts\activate  # Windows
uvicorn main:app --reload --port 8000

# 终端 2: 启动前端
cd frontend
npm run dev
```

### 5. 验证服务

```bash
# 检查后端健康状态
curl http://localhost:8000/health

# 检查前端
curl http://localhost:3000
```

访问 http://localhost:3000 开始使用。

## 环境变量

| 变量 | 说明 | 默认值 | 必需 |
|------|------|--------|------|
| `GITHUB_TOKEN` | GitHub API Token，提高 API 限额（60→5000次/小时） | 无 | 否 |
| `DEEPSEEK_API_KEY` | DeepSeek API Key，用于 AI 解读功能 | 无 | 否（有 fallback） |
| `OPENAI_API_KEY` | OpenAI API Key（备用） | 无 | 否 |
| `NEXT_PUBLIC_API_URL` | 后端 API 地址 | http://localhost:8000 | 否 |

> **注意**：无 API Key 时，系统使用规则引擎进行评分，AI 解读功能不可用但基础评分仍正常工作。

获取 API Key：
- [DeepSeek API Key](https://platform.deepseek.com/api_keys)
- [GitHub Token](https://github.com/settings/tokens/new?description=GitHub%20Repo%20Insight&scopes=public_repo)

## 健康评分体系

### 九维度评分（满分 100 分）

| 维度 | 满分 | 说明 |
|------|------|------|
| Popularity（流行度） | 25 | Stars、Forks、Watchers 综合评估 |
| Activity（活跃度） | 25 | Commit 频率、最近更新时间 |
| Community（社区） | 15 | 贡献者数量、社区活跃度 |
| Issue Governance（Issue治理） | 10 | Issue 响应时间、关闭率 |
| PR Governance（PR治理） | 10 | PR 合并时间、合并率 |
| Engineering（工程化） | 10 | README、LICENSE、CI/CD 配置 |
| Release/Maintenance（发布维护） | 5 | 发布节奏、维护状态 |

### 等级划分

| 等级 | 分数范围 | 说明 |
|------|----------|------|
| A | 90-100 | 优秀 - 高流行度、活跃维护 |
| B | 80-89 | 良好 - 维护良好、社区健康 |
| C | 70-79 | 一般 - 中等活跃度和社区 |
| D | 60-69 | 较差 - 低活跃度或社区 |
| E | 50-59 | 很差 - 严重问题 |
| F | <50 | 极差 - 停滞或废弃项目 |

## API 文档

启动服务后访问：
- API 文档：http://localhost:8000/docs
- ReDoc：http://localhost:8000/redoc

### 分析仓库

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"url":"https://github.com/microsoft/vscode"}'
```

### 获取配置状态

```bash
curl http://localhost:8000/api/settings
```

### 更新配置

```bash
curl -X PUT http://localhost:8000/api/settings \
  -H "Content-Type: application/json" \
  -d '{"deepseek_api_key":"sk-...", "github_token":"ghp_..."}'
```

## 项目结构

```
github-repo-insight/
├── frontend/                 # Next.js 15 前端
│   ├── app/                 # 页面和布局
│   ├── components/          # React 组件
│   ├── contexts/            # React Context
│   ├── hooks/               # 自定义 Hooks
│   ├── services/            # API 服务
│   └── types/               # TypeScript 类型
├── backend/                 # Python FastAPI 后端
│   ├── app/
│   │   ├── api/routes/      # API 路由
│   │   ├── services/       # 业务逻辑
│   │   ├── schemas/        # Pydantic 模型
│   │   ├── clients/        # GitHub API 客户端
│   │   └── core/           # 配置和异常
│   ├── main.py             # FastAPI 入口
│   └── requirements.txt    # Python 依赖
├── scripts/                 # 服务启动脚本
├── docs/                    # 文档
├── docker-compose.yml       # Docker Compose 配置
├── Dockerfile.backend      # 后端 Docker 镜像
└── Dockerfile.frontend      # 前端 Docker 镜像
```

## 开发指南

### 代码规范

- **Python**: PEP8, Black, Ruff, 类型提示必需
- **TypeScript**: Strict mode, 禁止使用 `any`
- **React**: 函数组件 + Hooks，组件不超过 300 行

### 提交规范

使用 Conventional Commits：
- `feat:` 新功能
- `fix:` 修复 bug
- `refactor:` 重构
- `docs:` 文档更新
- `test:` 测试
- `chore:` 其他

### 测试

```bash
# 后端测试
cd backend
pytest

# 前端构建检查
cd frontend
npm run build
```

## 故障排查

### 常见问题

**Q: 启动后显示 "Connection refused"**

检查服务是否运行：
```bash
curl http://localhost:8000/health
curl http://localhost:3000
```

**Q: GitHub API Rate Limit**

配置 GitHub Token：
1. 打开 http://localhost:3000
2. 点击设置图标
3. 输入 GitHub Token
4. 保存

**Q: AI 解读功能不可用**

配置 DeepSeek API Key：
1. 获取 Key：https://platform.deepseek.com/api_keys
2. 打开设置，输入 Key
3. 保存

**Q: 端口被占用**

Windows 检查并杀死进程：
```bash
netstat -ano | findstr :8000
taskkill /PID <pid> /F
```

**Q: Python 依赖安装失败**

确保 Python 版本 >= 3.12：
```bash
python --version
```

使用国内镜像：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

更多问题请参考 [docs/Troubleshooting.md](docs/Troubleshooting.md)。

## 贡献

欢迎提交 Issue 和 Pull Request！

查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解更多。

## License

MIT License - 详见 [LICENSE](LICENSE) 文件。