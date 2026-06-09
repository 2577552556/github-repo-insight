#!/bin/bash
# 后端服务启动脚本
# 使用方法: bash scripts/start-backend.sh
#
# 功能:
# 1. 检查并终止现有后端进程
# 2. 等待端口释放
# 3. 启动新后端服务
# 4. 健康检查

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"
PID_FILE="$PROJECT_DIR/backend/.pid"
BACKEND_DIR="$PROJECT_DIR/backend"

# 创建日志目录
mkdir -p "$LOG_DIR"

# ============================================
# 停止现有后端进程
# ============================================
stop_existing_process() {
    echo "检查现有后端进程..."

    # 方法1: 检查 PID 文件
    if [ -f "$PID_FILE" ]; then
        OLD_PID=$(cat "$PID_FILE")
        if [ -n "$OLD_PID" ]; then
            echo "  发现 PID 文件: $OLD_PID"
            if ps -p "$OLD_PID" > /dev/null 2>&1; then
                echo "  终止 PID $OLD_PID 的进程..."
                cmd //c "taskkill /F /PID $OLD_PID" 2>/dev/null || true
            fi
        fi
        rm -f "$PID_FILE"
    fi

    # 方法2: 通过 wmic 查找 uvicorn 进程
    echo "  通过进程特征查找 uvicorn 进程..."
    for pid in $(wmic process where "name='python.exe' and commandline like '%uvicorn%8000%'" get processid 2>/dev/null | tr -d '\r' | grep -oE "[0-9]+"); do
        echo "  终止进程 $pid (uvicorn)"
        cmd //c "taskkill /F /PID $pid" 2>/dev/null || true
    done
}

# ============================================
# 等待端口释放
# ============================================
wait_for_port_release() {
    local port=$1
    local max_attempts=5
    local attempt=1

    echo "  等待端口 $port 释放..."
    while [ $attempt -le $max_attempts ]; do
        if ! netstat -ano | grep -q ":$port.*LISTENING"; then
            echo "  端口 $port 已释放"
            return 0
        fi
        echo "    等待中... ($attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done

    echo "  警告: 端口 $port 释放超时，尝试强制终止..."
    # 强制终止所有在监听该端口的进程
    for pid in $(netstat -ano | grep ":$port.*LISTENING" | awk '{print $5}' | sort -u); do
        if [ -n "$pid" ] && [ "$pid" != "0" ]; then
            echo "    强制终止 PID $pid"
            cmd //c "taskkill /F /PID $pid" 2>/dev/null || true
        fi
    done
    sleep 2
    return 0
}

# ============================================
# 启动后端服务
# ============================================
start_backend() {
    echo "启动后端服务 (端口 8000)..."

    # 设置 Python 环境变量，使用 UTF-8 编码
    export PYTHONIOENCODING=utf-8
    export PYTHONUTF8=1

    cd "$BACKEND_DIR"

    # 使用 chcp 65001 确保 cmd 使用 UTF-8 编码
    # 然后启动 uvicorn
    cmd //c "chcp 65001 >nul 2>&1 && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --log-level info" > "$LOG_DIR/backend.log" 2>&1 &

    # 获取新进程 PID
    # 注意：$! 在 cmd //c 中可能不准确，我们使用其他方法获取
    sleep 3

    # 查找新启动的进程并记录 PID
    NEW_PID=$(wmic process where "name='python.exe' and commandline like '%uvicorn%8000%'" get processid 2>/dev/null | tr -d '\r' | grep -oE "[0-9]+" | head -1)

    if [ -n "$NEW_PID" ]; then
        echo "$NEW_PID" > "$PID_FILE"
        echo "后端服务已启动 (PID: $NEW_PID)"
    else
        echo "警告: 无法获取进程 PID"
    fi

    echo "日志文件: $LOG_DIR/backend.log"
}

# ============================================
# 健康检查
# ============================================
health_check() {
    echo "执行健康检查..."

    local max_attempts=5
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo "✓ 后端服务健康检查通过"
            return 0
        fi
        echo "    等待服务启动... ($attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done

    echo "✗ 后端服务健康检查失败"
    echo "查看日志: tail -f $LOG_DIR/backend.log"
    return 1
}

# ============================================
# 主流程
# ============================================
echo "=========================================="
echo "后端服务启动脚本"
echo "=========================================="

# 停止现有进程
stop_existing_process

# 等待端口释放
wait_for_port_release 8000

# 启动新服务
start_backend

# 健康检查
health_check

echo "=========================================="
echo "启动流程完成"
echo "=========================================="