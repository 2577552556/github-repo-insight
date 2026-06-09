#!/bin/bash
# 查看服务状态
# 跨平台兼容：支持 Linux/macOS/Windows (Git Bash/MSYS2)
# 使用方法: bash scripts/status.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 加载公共函数库
source "$SCRIPT_DIR/common.sh"

echo "=========================================="
echo "服务状态检查"
echo "=========================================="
echo "操作系统: $(detect_os)"
echo ""

# 检查后端
echo "--- 后端服务 (端口 8000) ---"
if is_port_listening 8000; then
    backend_pid=$(get_port_pid 8000)
    echo "✓ 后端服务运行中 (PID: $backend_pid)"
else
    echo "✗ 后端服务未运行"
fi

# 检查前端
echo ""
echo "--- 前端服务 (端口 3000) ---"
if is_port_listening 3000; then
    frontend_pid=$(get_port_pid 3000)
    echo "✓ 前端服务运行中 (PID: $frontend_pid)"
else
    echo "✗ 前端服务未运行"
fi

# 检查 PID 文件
echo ""
echo "--- PID 文件 ---"
if [ -f "$PROJECT_DIR/backend/.pid" ]; then
    echo "  backend/.pid: $(cat "$PROJECT_DIR/backend/.pid")"
else
    echo "  backend/.pid: 不存在"
fi

if [ -f "$PROJECT_DIR/frontend/.pid" ]; then
    echo "  frontend/.pid: $(cat "$PROJECT_DIR/frontend/.pid")"
else
    echo "  frontend/.pid: 不存在"
fi

echo ""
echo "=========================================="