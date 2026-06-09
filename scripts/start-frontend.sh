#!/bin/bash
# 前端服务启动脚本
# 使用方法: bash scripts/start-frontend.sh
#
# 功能:
# 1. 检查并终止现有前端进程
# 2. 启动新前端服务
# 3. 验证服务就绪

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"
PID_FILE="$PROJECT_DIR/frontend/.pid"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# 创建日志目录
mkdir -p "$LOG_DIR"

# ============================================
# 停止现有前端进程
# ============================================
stop_existing_process() {
    echo "检查现有前端进程..."

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

    # 方法2: 通过 wmic 查找 node 进程 (next dev)
    echo "  通过进程特征查找 node 进程..."
    for pid in $(wmic process where "name='node.exe' and commandline like '%next%dev%'" get processid 2>/dev/null | tr -d '\r' | grep -oE "[0-9]+"); do
        echo "  终止进程 $pid (next dev)"
        cmd //c "taskkill /F /PID $pid" 2>/dev/null || true
    done

    # 也杀掉直接包含 frontend 路径的 node 进程
    for pid in $(wmic process where "name='node.exe' and commandline like '%github-repo-insight%frontend%'" get processid 2>/dev/null | tr -d '\r' | grep -oE "[0-9]+"); do
        echo "  终止进程 $pid (frontend path)"
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

    echo "  警告: 端口 $port 释放超时"
    return 0
}

# ============================================
# 启动前端服务
# ============================================
start_frontend() {
    echo "启动前端服务 (端口 3000)..."

    cd "$FRONTEND_DIR"

    # 使用 chcp 65001 确保 cmd 使用 UTF-8 编码
    cmd //c "chcp 65001 >nul 2>&1 && npm run dev" > "$LOG_DIR/frontend.log" 2>&1 &

    # 等待启动
    sleep 5

    # 查找新启动的进程并记录 PID
    NEW_PID=$(wmic process where "name='node.exe' and commandline like '%next%dev%'" get processid 2>/dev/null | tr -d '\r' | grep -oE "[0-9]+" | head -1)

    if [ -n "$NEW_PID" ]; then
        echo "$NEW_PID" > "$PID_FILE"
        echo "前端服务已启动 (PID: $NEW_PID)"
    else
        echo "警告: 无法获取进程 PID"
    fi

    echo "日志文件: $LOG_DIR/frontend.log"
}

# ============================================
# 服务就绪检查
# ============================================
ready_check() {
    echo "检查前端服务状态..."

    local max_attempts=10
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            echo "✓ 前端服务已就绪 (http://localhost:3000)"
            return 0
        fi

        # 检查日志中是否有端口信息（next 可能自动切换端口）
        USED_PORT=$(grep -o "using port [0-9]*" "$LOG_DIR/frontend.log" 2>/dev/null | grep -o "[0-9]*" | head -1)
        if [ -n "$USED_PORT" ]; then
            if curl -s "http://localhost:$USED_PORT" > /dev/null 2>&1; then
                echo "✓ 前端服务已就绪 (http://localhost:$USED_PORT)"
                return 0
            fi
        fi

        echo "    等待服务启动... ($attempt/$max_attempts)"
        sleep 3
        attempt=$((attempt + 1))
    done

    echo "✓ 前端服务启动命令已执行"
    echo "查看日志: tail -f $LOG_DIR/frontend.log"
    return 0
}

# ============================================
# 主流程
# ============================================
echo "=========================================="
echo "前端服务启动脚本"
echo "=========================================="

# 停止现有进程
stop_existing_process

# 等待端口释放
wait_for_port_release 3000

# 启动新服务
start_frontend

# 就绪检查
ready_check

echo "=========================================="
echo "启动流程完成"
echo "=========================================="