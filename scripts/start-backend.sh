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
# 查找并杀死占用 8000 端口的进程
for pid in $(netstat -ano 2>/dev/null | grep ":8000" | grep "LISTENING" | awk '{print $5}' | sort -u); do
    taskkill /F /PID "$pid" 2>/dev/null || true
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