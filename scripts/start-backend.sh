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
# 启动后端服务
# ============================================
start_backend() {
    echo "启动后端服务 (端口 8000)..."

    # 设置环境变量
    export PYTHONIOENCODING=utf-8
    export PYTHONUTF8=1

    cd "$BACKEND_DIR"

    # 确定 Python 解释器路径（优先使用虚拟环境）
    if [ -d "$BACKEND_DIR/.venv" ]; then
        if [ "$OS_TYPE" = "windows" ]; then
            PYTHON_CMD="$BACKEND_DIR/.venv/Scripts/python"
        else
            PYTHON_CMD="$BACKEND_DIR/.venv/bin/python"
        fi
    else
        PYTHON_CMD=python
    fi

    # 启动 uvicorn
    if [ "$OS_TYPE" = "windows" ]; then
        # 将 Git Bash 路径 /d/Code/... 转换为 Windows D:\Code\...
        BACKEND_DIR_WIN="D:${BACKEND_DIR#/d}"
        BACKEND_DIR_WIN=$(echo "$BACKEND_DIR_WIN" | tr '/' '\\')
        PYTHON_CMD_WIN="D:${PYTHON_CMD#/d}"
        PYTHON_CMD_WIN=$(echo "$PYTHON_CMD_WIN" | tr '/' '\\')
        cmd //c "chcp 65001 >nul 2>&1 && cd /d $BACKEND_DIR_WIN && $PYTHON_CMD_WIN -m uvicorn main:app --host 0.0.0.0 --port 8000 --log-level info" > "$LOG_DIR/backend.log" 2>&1 &
    else
        cd "$BACKEND_DIR"
        nohup $PYTHON_CMD -m uvicorn main:app --host 0.0.0.0 --port 8000 --log-level info > "$LOG_DIR/backend.log" 2>&1 &
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
echo "--- 启动后端服务 ---"
start_backend

echo ""
echo "--- 健康检查 ---"
health_check

echo ""
echo "=========================================="
echo "启动流程完成"
echo "=========================================="