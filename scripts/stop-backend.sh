#!/bin/bash
# 后端服务停止脚本
# 使用方法: bash scripts/stop-backend.sh
#
# 功能:
# 1. 读取 PID 文件终止进程
# 2. 扫描 uvicorn 进程并终止
# 3. 等待端口 8000 释放

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="$PROJECT_DIR/backend/.pid"

echo "=========================================="
echo "后端服务停止脚本"
echo "=========================================="

# ============================================
# 方法1: 通过 PID 文件停止
# ============================================
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE" 2>/dev/null)
    if [ -n "$OLD_PID" ]; then
        echo "  发现 PID 文件: $OLD_PID"
        if ps -p "$OLD_PID" > /dev/null 2>&1; then
            echo "  终止 PID $OLD_PID 的进程..."
            cmd //c "taskkill /F /PID $OLD_PID" 2>/dev/null || true
        fi
    fi
    rm -f "$PID_FILE"
    echo "  已删除 PID 文件"
fi

# ============================================
# 方法2: 扫描 uvicorn 进程
# ============================================
echo "  扫描 uvicorn 进程..."
KILLED=0
for pid in $(wmic process where "name='python.exe' and commandline like '%uvicorn%8000%'" get processid 2>/dev/null | tr -d '\r' | grep -oE "[0-9]+"); do
    echo "  终止进程 $pid (uvicorn)"
    cmd //c "taskkill /F /PID $pid" 2>/dev/null || true
    KILLED=1
done

if [ "$KILLED" = "0" ]; then
    echo "  未发现运行中的 uvicorn 进程"
fi

# ============================================
# 等待端口释放
# ============================================
echo "  等待端口 8000 释放..."
for attempt in 1 2 3 4 5; do
    if ! netstat -ano | grep -q ":8000.*LISTENING"; then
        echo "✓ 端口 8000 已释放"
        echo "=========================================="
        echo "后端服务已停止"
        echo "=========================================="
        exit 0
    fi
    echo "    等待中... ($attempt/5)"
    sleep 1
done

echo "  警告: 端口 8000 释放超时，尝试强制终止..."
for pid in $(netstat -ano | grep ":8000.*LISTENING" | awk '{print $5}' | sort -u); do
    if [ -n "$pid" ] && [ "$pid" != "0" ]; then
        echo "    强制终止 PID $pid"
        cmd //c "taskkill /F /PID $pid" 2>/dev/null || true
    fi
done

echo "=========================================="
echo "后端服务停止完成"
echo "=========================================="