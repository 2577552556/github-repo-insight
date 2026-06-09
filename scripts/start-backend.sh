#!/bin/bash
# 后端服务启动脚本
# 跨平台兼容：支持 Linux/macOS/Windows (Git Bash/MSYS2)
# 使用方法: bash scripts/start-backend.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"
PID_FILE="$PROJECT_DIR/backend/.pid"
BACKEND_DIR="$PROJECT_DIR/backend"

# 加载公共函数库
source "$SCRIPT_DIR/common.sh"

echo "=========================================="
echo "后端服务启动脚本"
echo "=========================================="
echo "操作系统: $(detect_os)"

# 创建必要目录
ensure_directories

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
            kill_process "$OLD_PID"
        fi
        rm -f "$PID_FILE"
    fi

    # 方法2: 通过进程特征查找并终止
    echo "  查找 uvicorn 进程..."
    local pids=$(find_process_pids "uvicorn.*8000")
    for pid in $pids; do
        if [ -n "$pid" ]; then
            echo "  终止进程 $pid (uvicorn)"
            kill_process "$pid"
        fi
    done

    # 方法3: 强制终止占用端口的进程
    if is_port_listening 8000; then
        local port_pid=$(get_port_pid 8000)
        if [ -n "$port_pid" ] && [ "$port_pid" != "0" ]; then
            echo "  终止占用端口 8000 的进程 $port_pid"
            kill_process "$port_pid"
        fi
    fi
}

# ============================================
# 启动后端服务
# ============================================
start_backend() {
    echo "启动后端服务 (端口 8000)..."

    # 设置环境变量
    export PYTHONIOENCODING=utf-8
    export PYTHONUTF8=1

    cd "$BACKEND_DIR"

    # 启动 uvicorn
    if [ "$OS_TYPE" = "windows" ]; then
        cmd //c "chcp 65001 >nul 2>&1 && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --log-level info" > "$LOG_DIR/backend.log" 2>&1 &
    else
        nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 --log-level info > "$LOG_DIR/backend.log" 2>&1 &
    fi

    # 等待启动
    sleep 3

    # 查找新进程 PID 并记录
    local pids=$(find_process_pids "uvicorn.*8000")
    local new_pid=$(echo "$pids" | awk '{print $1}')
    if [ -n "$new_pid" ]; then
        echo "$new_pid" > "$PID_FILE"
        echo "后端服务已启动 (PID: $new_pid)"
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

    local max_attempts=10
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -s --connect-timeout 5 http://localhost:8000/health > /dev/null 2>&1; then
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
echo ""
echo "--- 停止现有进程 ---"
stop_existing_process

echo ""
echo "--- 等待端口释放 ---"
wait_for_port_release 8000 5

echo ""
echo "--- 启动后端服务 ---"
start_backend

echo ""
echo "--- 健康检查 ---"
health_check

echo ""
echo "=========================================="
echo "启动流程完成"
echo "=========================================="