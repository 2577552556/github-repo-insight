#!/bin/bash
# 后端服务启动脚本
# 使用方法: bash scripts/start-backend.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 停止现有后端进程
echo "停止现有后端进程..."
# 精确杀死包含项目路径的 python 进程（uvicorn）
# 注意：wmic 输出包含 ^M（回车符），需要用 tr 去除
# 注意：Windows 下需要用 cmd //c 执行 taskkill
for pid in $(wmic process where "name='python.exe' and commandline like '%github-repo-insight%backend%'" get processid 2>/dev/null | tr -d '\r' | grep -E "^[0-9]+$"); do
    echo "  杀死进程 $pid"
    cmd //c "taskkill /F /PID $pid" 2>/dev/null || true
done
sleep 1

# 启动后端服务
echo "启动后端服务 (端口 8000)..."
cd "$PROJECT_DIR/backend"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --log-level info >> "$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!

echo "后端服务已启动 (PID: $BACKEND_PID)"
echo "日志文件: $LOG_DIR/backend.log"

# 等待服务启动
sleep 3

# 检查服务状态
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ 后端服务健康检查通过"
else
    echo "✗ 后端服务健康检查失败"
    echo "查看日志: tail -f $LOG_DIR/backend.log"
fi