#!/bin/bash
# 前端服务启动脚本
# 跨平台兼容：支持 Linux/macOS/Windows (Git Bash/MSYS2)
# 使用方法: bash scripts/start-frontend.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"
PID_FILE="$PROJECT_DIR/frontend/.pid"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# 加载公共函数库
source "$SCRIPT_DIR/common.sh"

echo "=========================================="
echo "前端服务启动脚本"
echo "=========================================="
echo "操作系统: $(detect_os)"

# 创建必要目录
ensure_directories

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
            kill_process "$OLD_PID"
        fi
        rm -f "$PID_FILE"
    fi

    # 方法2: 通过进程特征查找并终止
    echo "  查找 node 进程..."
    local pids=$(find_process_pids "next.*dev")
    for pid in $pids; do
        if [ -n "$pid" ]; then
            echo "  终止进程 $pid (next dev)"
            kill_process "$pid"
        fi
    done

    # 方法3: 强制终止占用端口的进程
    if is_port_listening 3000; then
        local port_pid=$(get_port_pid 3000)
        if [ -n "$port_pid" ] && [ "$port_pid" != "0" ]; then
            echo "  终止占用端口 3000 的进程 $port_pid"
            kill_process "$port_pid"
        fi
    fi
}

# ============================================
# 启动前端服务
# ============================================
start_frontend() {
    echo "启动前端服务 (端口 3000)..."

    cd "$FRONTEND_DIR"

    # 启动 Next.js
    if [ "$OS_TYPE" = "windows" ]; then
        cmd //c "chcp 65001 >nul 2>&1 && npm run dev" > "$LOG_DIR/frontend.log" 2>&1 &
    else
        nohup npm run dev > "$LOG_DIR/frontend.log" 2>&1 &
    fi

    # 等待启动
    sleep 5

    # 查找新进程 PID 并记录
    local pids=$(find_process_pids "next.*dev")
    local new_pid=$(echo "$pids" | awk '{print $1}')
    if [ -n "$new_pid" ]; then
        echo "$new_pid" > "$PID_FILE"
        echo "前端服务已启动 (PID: $new_pid)"
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

    local max_attempts=15
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -s --connect-timeout 5 http://localhost:3000 > /dev/null 2>&1; then
            echo "✓ 前端服务已就绪 (http://localhost:3000)"
            return 0
        fi

        # 检查日志中是否有端口信息
        local used_port=$(grep -o "using port [0-9]*" "$LOG_DIR/frontend.log" 2>/dev/null | grep -o "[0-9]*" | head -1)
        if [ -n "$used_port" ]; then
            if curl -s --connect-timeout 5 "http://localhost:$used_port" > /dev/null 2>&1; then
                echo "✓ 前端服务已就绪 (http://localhost:$used_port)"
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
echo ""
echo "--- 停止现有进程 ---"
stop_existing_process

echo ""
echo "--- 等待端口释放 ---"
wait_for_port_release 3000 5

echo ""
echo "--- 启动前端服务 ---"
start_frontend

echo ""
echo "--- 就绪检查 ---"
ready_check

echo ""
echo "=========================================="
echo "启动流程完成"
echo "=========================================="