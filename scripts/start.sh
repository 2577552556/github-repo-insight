#!/bin/bash
# 统一启动脚本 - 启动所有服务
# 跨平台兼容：支持 Linux/macOS/Windows (Git Bash/MSYS2)
# 使用方法: bash scripts/start.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 加载公共函数库
source "$SCRIPT_DIR/common.sh"

echo "=========================================="
echo "启动所有服务"
echo "=========================================="
echo "操作系统: $(detect_os)"

# 启动后端
echo ""
echo "--- 启动后端服务 ---"
bash "$SCRIPT_DIR/start-backend.sh"

# 启动前端
echo ""
echo "--- 启动前端服务 ---"
bash "$SCRIPT_DIR/start-frontend.sh"

echo ""
echo "=========================================="
echo "所有服务已启动"
echo "  后端: http://localhost:8000"
echo "  前端: http://localhost:3000"
echo "=========================================="