# GitHub Repository Insight - 管理员手册

## 目录

1. [部署指南](#1-部署指南)
2. [配置管理](#2-配置管理)
3. [数据库](#3-数据库)
4. [日志管理](#4-日志管理)
5. [备份恢复](#5-备份恢复)
6. [故障排查](#6-故障排查)
7. [安全事项](#7-安全事项)

---

## 1. 部署指南

### 1.1 环境要求

| 组件 | 要求 |
|------|------|
| 操作系统 | Windows / Linux / macOS |
| Node.js | 20+ |
| Python | 3.12+ |
| 内存 | 最少 2GB |
| 磁盘 | 最少 1GB 可用空间 |

### 1.2 目录结构

```
github-repo-insight/
├── backend/                 # 后端服务
│   ├── app/                 # 应用代码
│   │   ├── api/routes/      # API 路由
│   │   ├── services/        # 业务逻辑
│   │   ├── schemas/         # 数据模型
│   │   ├── clients/         # 外部 API 客户端
│   │   ├── core/            # 核心配置
│   │   └── utils/           # 工具函数
│   ├── data/                # 数据目录
│   │   ├── analysis.db       # SQLite 数据库
│   │   └── .credential_key   # 加密主密钥
│   ├── main.py              # FastAPI 入口
│   └── requirements.txt      # Python 依赖
├── frontend/                # 前端服务
│   ├── app/                 # Next.js 页面
│   ├── components/          # React 组件
│   ├── hooks/               # 自定义 Hooks
│   ├── services/            # API 服务
│   └── package.json         # Node.js 依赖
├── scripts/                  # 服务脚本
│   ├── start-backend.sh      # 启动后端
│   ├── start-frontend.sh     # 启动前端
│   ├── stop-backend.sh       # 停止后端
│   ├── stop-frontend.sh      # 停止前端
│   └── stop-all.sh           # 停止所有
├── logs/                    # 日志目录
├── docs/                    # 文档
└── README.md                # 项目说明
```

### 1.3 部署步骤

#### 方式一：脚本部署（推荐）

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

# 4. 启动后端服务
cd ..
bash scripts/start-backend.sh

# 5. 启动前端服务
bash scripts/start-frontend.sh
```

#### 方式二：手动部署

**后端**:

```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**前端**:

```bash
cd frontend
npm run dev
```

### 1.4 服务管理

#### 启动服务

```bash
# 启动后端
bash scripts/start-backend.sh

# 启动前端
bash scripts/start-frontend.sh
```

#### 停止服务

```bash
# 停止所有服务
bash scripts/stop-all.sh

# 或分别停止
bash scripts/stop-backend.sh
bash scripts/stop-frontend.sh
```

#### 检查服务状态

```bash
# 检查后端健康
curl http://localhost:8000/health

# 检查前端
curl http://localhost:3000
```

---

## 2. 配置管理

### 2.1 环境变量

后端配置文件位于 `backend/.env`:

```bash
# GitHub API Token (可选)
GITHUB_TOKEN=

# DeepSeek API Key (可选，用于 AI 解读)
DEEPSEEK_API_KEY=

# OpenAI API Key (备用)
OPENAI_API_KEY=

# API 端点 (通常无需修改)
OPENAI_API_URL=https://api.openai.com/v1
DEEPSEEK_API_URL=https://api.deepseek.com
```

### 2.2 运行时配置

用户可通过 Web 界面修改以下配置：

- GitHub Token
- DeepSeek API Key

这些配置存储在 SQLite 数据库中，使用 AES-256-CBC 加密。

### 2.3 配置优先级

运行时通过 API 设置的凭据 > `.env` 文件中的默认值

---

## 3. 数据库

### 3.1 数据库位置

```
backend/data/analysis.db
```

### 3.2 数据库结构

#### analysis_records 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT | UUID 主键 |
| repository_url | TEXT | 仓库 URL |
| repository_name | TEXT | 仓库名 |
| owner | TEXT | 所有者 |
| full_name | TEXT | owner/repo |
| score | INTEGER | 总分 |
| grade | TEXT | 等级 A-F |
| type_detection | TEXT | JSON，项目类型检测结果 |
| status | TEXT | processing/completed/failed |
| error_message | TEXT | 错误信息 |
| analysis_version | INTEGER | 版本号 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |
| result_json | TEXT | JSON，完整分析结果 |

#### credentials 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT | UUID 主键 |
| provider | TEXT | github / deepseek |
| name | TEXT | token / api_key |
| encrypted_value | TEXT | AES 加密的密文 |
| iv | TEXT | 初始化向量 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### 3.3 数据库维护

#### 查看数据库大小

```bash
ls -lh backend/data/analysis.db
```

#### 清理历史记录

用户可通过 Web 界面删除单条记录，或调用 API 批量删除。

---

## 4. 日志管理

### 4.1 日志位置

| 日志 | 路径 |
|------|------|
| 后端日志 | `logs/backend.log` |
| 前端日志 | `logs/frontend.log` |

### 4.2 日志轮转

日志文件会随服务重启而创建新的。建议定期清理或使用 logrotate。

### 4.3 日志级别

后端日志默认级别为 `INFO`。可在 `backend/main.py` 中调整。

### 4.4 查看日志

```bash
# 实时查看后端日志
tail -f logs/backend.log

# 查看最后 100 行
tail -100 logs/backend.log

# 搜索错误
grep -i error logs/backend.log
```

---

## 5. 备份恢复

### 5.1 备份

需要备份的关键文件：

```bash
# 数据库
cp backend/data/analysis.db backup/analysis.db.$(date +%Y%m%d)

# 加密主密钥 (重要！)
cp backend/data/.credential_key backup/.credential_key.$(date +%Y%m%d)
```

### 5.2 恢复

```bash
# 恢复数据库
cp backup/analysis.db.20260610 backend/data/analysis.db

# 恢复主密钥
cp backup/.credential_key.20260610 backend/data/.credential_key
```

### 5.3 注意事项

- 主密钥丢失后，已加密的凭据将无法解密
- 更换主密钥后需要重新配置 API Key

---

## 6. 故障排查

### 6.1 服务无法启动

#### 检查端口占用

```bash
netstat -ano | grep ":8000"
netstat -ano | grep ":3000"
```

#### 检查依赖安装

```bash
# Python 依赖
cd backend
pip install -r requirements.txt

# Node.js 依赖
cd ../frontend
npm install
```

### 6.2 分析失败

#### 检查 GitHub API 限制

未配置 Token 时，GitHub API 限制为 60 次/小时。

#### 检查 DeepSeek API

确保 API Key 有效且有足够配额。

#### 查看错误日志

```bash
tail -100 logs/backend.log
```

### 6.3 前端加载慢

- 检查 `npm install` 是否完成
- 清除缓存: `rm -rf frontend/.next`
- 重新构建: `cd frontend && npm run build`

### 6.4 数据库损坏

如果数据库损坏，删除后重启服务会自动创建新的空数据库：

```bash
rm backend/data/analysis.db
bash scripts/start-backend.sh
```

---

## 7. 安全事项

### 7.1 凭据保护

- API Key 和 Token 使用 AES-256-CBC 加密存储
- 主密钥文件 `.credential_key` 已加入 `.gitignore`，不会提交到版本库
- 不要将 `.credential_key` 文件分享给他人

### 7.2 网络安全

- 建议仅在内网环境部署
- 如需公网访问，使用 HTTPS 和身份认证
- 定期更换 API Key

### 7.3 数据备份

- 定期备份数据库和主密钥
- 备份文件存储在安全位置
- 测试恢复流程

---

## 附录：服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| 后端 API | 8000 | FastAPI 服务 |
| 前端 | 3000 | Next.js 开发服务器 |
| 数据库 | - | SQLite 文件存储 |

---

*最后更新: 2026-06-10*