#!/bin/bash
# 前端服务启动脚本
# 使用方法: bash scripts/start-frontend.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 停止现有前端进程
echo "停止现有前端进程..."
pkill -f "next dev" 2>/dev/null || true
pkill -f "node.*next" 2>/dev/null || true
sleep 1

# 启动前端服务
echo "启动前端服务 (端口 3000)..."
cd "$PROJECT_DIR/frontend"
npm run dev >> "$LOG_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!

echo "前端服务已启动 (PID: $FRONTEND_PID)"
echo "日志文件: $LOG_DIR/frontend.log"

# 等待服务启动
sleep 5

# 检查服务状态
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✓ 前端服务已就绪 (http://localhost:3000)"
else
    # 可能端口被占用，尝试检测
    USED_PORT=$(grep -o "using available port [0-9]*" "$LOG_DIR/frontend.log" 2>/dev/null | grep -o "[0-9]*" || echo "3000")
    echo "✓ 前端服务已启动 (http://localhost:$USED_PORT)"
fi