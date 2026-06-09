# 故障排查指南

本文档收录常见问题及解决方案。

## 目录

- [服务启动问题](#服务启动问题)
- [API 调用问题](#api-调用问题)
- [AI 功能问题](#ai-功能问题)
- [Docker 问题](#docker-问题)

---

## 服务启动问题

### 端口被占用

**症状**：`Error: port already in use` 或 `EADDRINUSE`

**解决方案**：

Windows：
```bash
# 检查端口占用
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# 杀死进程
taskkill /F /PID <pid>
```

Linux/macOS：
```bash
# 检查端口占用
lsof -i :8000
lsof -i :3000

# 杀死进程
kill -9 <pid>
```

### Python 版本不对

**症状**：`SyntaxError` 或 `ModuleNotFoundError`

**解决方案**：

```bash
# 检查 Python 版本（需要 3.12+）
python --version

# 如果版本过低，下载安装 https://www.python.org/downloads/
```

### 后端依赖安装失败

**症状**：`pip install` 报错或超时

**解决方案**：

使用国内镜像：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

或使用阿里云镜像：
```bash
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### 前端 node_modules 问题

**症状**：`npm install` 失败或模块找不到

**解决方案**：

```bash
cd frontend

# 删除 node_modules 重新安装
rm -rf node_modules package-lock.json
npm install
```

---

## API 调用问题

### GitHub API Rate Limit

**症状**：`429 Too Many Requests` 或 `rate limit exceeded`

**原因**：未使用 GitHub Token，API 限额只有 60 次/小时

**解决方案**：

1. 获取 GitHub Token：https://github.com/settings/tokens/new
   - 选择 `public_repo` 权限
2. 配置 Token：
   - 打开 http://localhost:3000
   - 点击设置图标
   - 输入 GitHub Token 并保存

或通过环境变量：
```bash
# Windows
set GITHUB_TOKEN=ghp_xxxxxxxxxxxx

# Linux/macOS
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
```

### 仓库不存在

**症状**：`404 Not Found`

**解决方案**：
- 检查 URL 格式是否正确：`https://github.com/owner/repo`
- 确认仓库是公开的（私有仓库无法访问）

### 网络连接失败

**症状**：`Network Error` 或 `Connection refused`

**解决方案**：

1. 检查后端是否运行：
```bash
curl http://localhost:8000/health
```

2. 检查防火墙设置
3. 检查代理设置（如果在中国大陆）

---

## AI 功能问题

### AI 解读功能不可用

**症状**：健康评分正常，但 AI 分析显示"数据不足以生成..."

**原因**：未配置 DeepSeek API Key

**解决方案**：

1. 获取 DeepSeek API Key：https://platform.deepseek.com/api_keys
2. 配置 Key：
   - 打开 http://localhost:3000
   - 点击设置图标
   - 输入 DeepSeek API Key 并保存

### DeepSeek API 调用失败

**症状**：`AI 解读服务调用失败` 或 `Invalid API Key`

**解决方案**：

1. 确认 API Key 正确且未过期
2. 检查 API Key 额度：https://platform.deepseek.com/usage
3. 确认网络可以访问 DeepSeek API

### AI 分析内容过于简略

**症状**：AI 分析只有几句话

**解决方案**：
- 重启后端服务（可能使用了缓存的旧 prompt）
- 确认 `ai_evaluation.py` 中的 `max_tokens` 设置足够大

---

## Docker 问题

### Docker 构建失败

**症状**：`docker build` 报错

**解决方案**：

1. 清理 Docker 缓存：
```bash
docker builder prune
docker compose build --no-cache
```

2. 检查 Docker 是否运行：
```bash
docker --version
docker compose --version
```

### Docker 健康检查失败

**症状**：`healthcheck failed`

**解决方案**：

1. 检查容器日志：
```bash
docker compose logs backend
```

2. 确认端口未被占用：
```bash
netstat -ano | findstr :8000
```

3. 手动测试健康端点：
```bash
docker exec -it <container_id> python -c "import httpx; print(httpx.get('http://localhost:8000/health').text)"
```

### Docker 端口冲突

**症状**：前端或后端无法启动

**解决方案**：

1. 停止本地服务（如果正在运行）
2. 或修改 docker-compose.yml 中的端口映射：
```yaml
ports:
  - "3001:3000"  # 改用 3001 端口
```

---

## 验证清单

如果遇到问题，按以下顺序检查：

- [ ] Python 版本 >= 3.12
- [ ] Node.js 版本 >= 20
- [ ] 后端依赖安装成功
- [ ] 前端 node_modules 已安装
- [ ] 端口未被占用
- [ ] 服务已启动（curl 健康检查通过）
- [ ] GitHub Token 已配置（如果遇到 rate limit）
- [ ] DeepSeek API Key 已配置（如果 AI 功能不可用）

---

## 获取帮助

如果以上方法都无法解决问题：

1. 查看日志文件：`logs/backend.log` 或 `logs/frontend.log`
2. 检查 GitHub Issues：https://github.com/2577552556/github-repo-insight/issues
3. 提交新的 Issue，包含：
   - 错误信息
   - 复现步骤
   - 环境信息（操作系统、Python 版本、Node.js 版本）