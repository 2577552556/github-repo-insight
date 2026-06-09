#!/bin/bash
# 前端服务停止脚本
# 跨平台兼容：支持 Linux/macOS/Windows (Git Bash/MSYS2)
# 使用方法: bash scripts/stop-frontend.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="$PROJECT_DIR/frontend/.pid"

# 加载公共函数库
source "$SCRIPT_DIR/common.sh"

echo "=========================================="
echo "前端服务停止脚本"
echo "=========================================="

# ============================================
# 方法1: 通过 PID 文件停止
# ============================================
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE" 2>/dev/null)
    if [ -n "$OLD_PID" ]; then
        echo "  发现 PID 文件: $OLD_PID"
        kill_process "$OLD_PID"
        echo "  已发送终止信号"
    fi
    rm -f "$PID_FILE"
fi

# ============================================
# 方法2: 查找并终止 node 进程
# ============================================
echo "  查找 node 进程..."
pids=$(find_process_pids "next.*dev")
for pid in $pids; do
    if [ -n "$pid" ]; then
        echo "  终止进程 $pid (next dev)"
        kill_process "$pid"
    fi
done

# ============================================
# 方法3: 终止占用端口的进程
# ============================================
if is_port_listening 3000; then
    port_pid=$(get_port_pid 3000)
    if [ -n "$port_pid" ] && [ "$port_pid" != "0" ]; then
        echo "  终止占用端口 3000 的进程 $port_pid"
        kill_process "$port_pid"
    fi
fi

# ============================================
# 等待端口释放
# ============================================
echo "  等待端口 3000 释放..."
if wait_for_port_release 3000 5; then
    echo "✓ 端口 3000 已释放"
else
    echo "  警告: 端口释放超时"
fi

echo "=========================================="
echo "前端服务停止完成"
echo "=========================================="