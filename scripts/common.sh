#!/bin/bash
# ============================================
# 跨平台通用函数库
# 供所有脚本调用
# ============================================

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# ============================================
# 操作系统检测
# ============================================
detect_os() {
    case "$(uname -s)" in
        Linux*)     echo "linux" ;;
        Darwin*)    echo "macos" ;;
        MINGW*)     echo "windows" ;;
        MSYS*)      echo "windows" ;;
        CYGWIN*)    echo "windows" ;;
        *)          echo "unknown" ;;
    esac
}

OS_TYPE=$(detect_os)

# ============================================
# 跨平台进程终止
# ============================================
kill_process() {
    local pid=$1
    if [ -z "$pid" ]; then
        return
    fi

    if [ "$OS_TYPE" = "windows" ]; then
        cmd //c "taskkill /F /PID $pid" 2>/dev/null || true
    else
        kill -9 "$pid" 2>/dev/null || true
    fi
}

# ============================================
# 跨平台进程查找 - 返回 PID 列表
# ============================================
find_process_pids() {
    local pattern=$1
    local pids=""

    if [ "$OS_TYPE" = "windows" ]; then
        # Windows: 使用 wmic
        for pid in $(wmic process where "name='python.exe' and commandline like '%$pattern%'" get processid 2>/dev/null | tr -d '\r' | grep -oE "[0-9]+"); do
            pids="$pids $pid"
        done
        for pid in $(wmic process where "name='node.exe' and commandline like '%$pattern%'" get processid 2>/dev/null | tr -d '\r' | grep -oE "[0-9]+"); do
            pids="$pids $pid"
        done
    else
        # Unix: 使用 pgrep 或 ps
        if command -v pgrep &> /dev/null; then
            pids=$(pgrep -f "$pattern" 2>/dev/null | tr '\n' ' ')
        elif command -v ps &> /dev/null; then
            pids=$(ps aux 2>/dev/null | grep "$pattern" | grep -v grep | awk '{print $2}' | tr '\n' ' ')
        fi
    fi

    echo "$pids" | xargs
}

# ============================================
# 跨平台端口检测 - 检查端口是否被占用
# ============================================
is_port_listening() {
    local port=$1

    if [ "$OS_TYPE" = "windows" ]; then
        netstat -ano 2>/dev/null | grep -q ":$port.*LISTENING"
    else
        # 优先使用 ss，其次 lsof，最后 netstat
        if command -v ss &> /dev/null; then
            ss -tlnp 2>/dev/null | grep -q ":$port "
        elif command -v lsof &> /dev/null; then
            lsof -i :$port &> /dev/null
        elif command -v netstat &> /dev/null; then
            netstat -tlnp 2>/dev/null | grep -q ":$port "
        else
            return 1
        fi
    fi
}

# ============================================
# 获取占用端口的进程 PID
# ============================================
get_port_pid() {
    local port=$1

    if [ "$OS_TYPE" = "windows" ]; then
        netstat -ano 2>/dev/null | grep ":$port.*LISTENING" | awk '{print $5}' | head -1
    else
        if command -v ss &> /dev/null; then
            ss -tlnp 2>/dev/null | grep ":$port " | sed -n 's/.*pid=\([0-9]*\).*/\1/p' | head -1
        elif command -v lsof &> /dev/null; then
            lsof -t -i :$port 2>/dev/null | head -1
        elif command -v netstat &> /dev/null; then
            netstat -tlnp 2>/dev/null | grep ":$port " | awk '{print $7}' | cut -d'/' -f1 | head -1
        fi
    fi
}

# ============================================
# 等待端口释放
# ============================================
wait_for_port_release() {
    local port=$1
    local max_attempts=${2:-10}
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if ! is_port_listening "$port"; then
            return 0
        fi
        echo "    等待端口 $port 释放... ($attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done

    # 超时后强制终止
    local pid=$(get_port_pid "$port")
    if [ -n "$pid" ] && [ "$pid" != "0" ]; then
        echo "    强制终止占用端口 $port 的进程 PID=$pid"
        kill_process "$pid"
        sleep 2
    fi

    return 0
}

# ============================================
# 创建必要目录
# ============================================
ensure_directories() {
    mkdir -p "$PROJECT_DIR/logs"
    mkdir -p "$PROJECT_DIR/backend/data"
}

# ============================================
# 检测命令是否存在
# ============================================
command_exists() {
    command -v "$1" &> /dev/null
}

# ============================================
# 检测 Python 版本
# ============================================
check_python() {
    if command_exists python3; then
        PYTHON_CMD=python3
    elif command_exists python; then
        PYTHON_CMD=python
    else
        echo "❌ Python 未安装"
        return 1
    fi

    local version=$($PYTHON_CMD --version 2>&1 | grep -oE "[0-9]+\.[0-9]+" | head -1)
    local major=$(echo "$version" | cut -d. -f1)
    local minor=$(echo "$version" | cut -d. -f2)

    if [ "$major" -eq 3 ] && [ "$minor" -ge 9 ]; then
        echo "✓ Python $version 已安装"
        return 0
    else
        echo "⚠ Python 版本过低 ($version)，建议 3.9+"
        return 0  # 仍继续尝试
    fi
}

# ============================================
# 检测 Node.js 版本
# ============================================
check_node() {
    if command_exists node; then
        local version=$(node --version 2>&1 | grep -oE "v[0-9]+" | head -1)
        local major=$(echo "$version" | sed 's/v//' | cut -d. -f1)

        if [ "$major" -ge 18 ]; then
            echo "✓ Node.js $version 已安装"
            return 0
        else
            echo "⚠ Node.js 版本过低 ($version)，建议 18+"
            return 0
        fi
    else
        echo "❌ Node.js 未安装"
        return 1
    fi
}

# ============================================
# 检测 npm
# ============================================
check_npm() {
    if command_exists npm; then
        echo "✓ npm 已安装"
        return 0
    else
        echo "❌ npm 未安装"
        return 1
    fi
}

# ============================================
# 导出公共变量
# ============================================
export -f detect_os
export -f kill_process
export -f find_process_pids
export -f is_port_listening
export -f get_port_pid
export -f wait_for_port_release
export -f ensure_directories
export -f command_exists
export -f check_python
export -f check_node
export -f check_npm