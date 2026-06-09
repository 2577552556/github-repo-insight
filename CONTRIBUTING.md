# 贡献指南

感谢您对 GitHub Repository Health Check 项目的兴趣！我们欢迎各种形式的贡献。

## 如何贡献

### 报告问题

如果您发现 bug 或有新功能建议：

1. 先搜索 [Issues](https://github.com/2577552556/github-repo-insight/issues) 确认问题未被报告
2. 创建新 Issue，包含：
   - 清晰的问题描述
   - 复现步骤
   - 环境信息（操作系统、Python 版本、Node.js 版本）
   - 截图（如果适用）

### 提交代码

#### 分支策略

```
main          # 稳定版本
├── develop   # 开发分支
└── feature/* # 功能分支
```

#### 开发流程

1. **Fork 仓库** 到您的 GitHub 账户

2. **克隆并创建分支**：
```bash
git clone https://github.com/your-username/github-repo-insight.git
cd github-repo-insight
git checkout -b feature/your-feature-name
```

3. **进行开发**：
```bash
# 启动后端
bash scripts/start-backend.sh

# 启动前端（新终端）
bash scripts/start-frontend.sh
```

4. **编写代码**：
   - 遵循项目代码规范
   - 添加必要的类型注解
   - 编写清晰的注释

5. **提交代码**：
```bash
git add .
git commit -m "feat: 添加新功能描述"
```

6. **推送并创建 Pull Request**：
```bash
git push origin feature/your-feature-name
```

#### 提交规范

使用 Conventional Commits 格式：

| 类型 | 说明 |
|------|------|
| `feat:` | 新功能 |
| `fix:` | 修复 bug |
| `refactor:` | 重构（不改变功能） |
| `docs:` | 文档更新 |
| `style:` | 代码格式（不影响功能） |
| `test:` | 测试相关 |
| `chore:` | 其他（构建、依赖更新等） |

示例：
```
feat: 添加仓库收藏功能
fix: 修复分析页面加载慢的问题
docs: 更新 README 安装步骤
refactor: 重构 GitHub API 客户端
```

## 代码规范

### Python

- 遵循 PEP 8
- 使用 Black 格式化
- 使用 Ruff 进行 lint 检查
- 类型提示必须添加

```python
async def analyze_repository(
    owner: str,
    repo: str,
) -> RepositoryAnalysis:
    """分析仓库并返回结果."""
    ...
```

### TypeScript

- 启用 strict mode
- 禁止使用 `any`，使用 `unknown` 代替
- 组件不超过 300 行
- 使用函数组件和 Hooks

```typescript
interface RepositoryInfo {
  name: string;
  owner: string;
  full_name: string;
}
```

### React

- 使用函数组件
- 使用 Hooks 管理状态
- 组件职责单一
- 提取可复用的逻辑到 hooks

## 测试

### 后端测试

```bash
cd backend
pytest
```

### 前端构建检查

```bash
cd frontend
npm run build
npm run lint
```

## 项目结构

```
github-repo-insight/
├── frontend/          # Next.js 前端
│   ├── app/           # 页面
│   ├── components/    # React 组件
│   ├── hooks/         # 自定义 Hooks
│   ├── services/      # API 服务
│   └── types/         # TypeScript 类型
├── backend/           # FastAPI 后端
│   ├── app/
│   │   ├── api/       # API 路由
│   │   ├── services/  # 业务逻辑
│   │   ├── schemas/   # 数据模型
│   │   └── core/      # 核心配置
│   └── main.py        # 入口文件
├── scripts/           # 启动脚本
└── docs/             # 文档
```

## 开发流程

1. **讨论** - 在提交 PR 前，先在 Issue 中讨论您的想法
2. **开发** - 按照代码规范进行开发
3. **测试** - 确保本地测试通过
4. **提交** - 使用清晰的提交信息
5. **审核** - 等待代码审核
6. **合并** - 经审核后合并到主分支

## 许可证

通过贡献代码，您同意将您的代码按照 MIT 许可证授权。

---

再次感谢您的贡献！