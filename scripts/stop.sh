#!/bin/bash
# 统一停止脚本 - 停止所有服务
# 跨平台兼容：支持 Linux/macOS/Windows (Git Bash/MSYS2)
# 使用方法: bash scripts/stop.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 加载公共函数库
source "$SCRIPT_DIR/common.sh"

echo "=========================================="
echo "停止所有服务"
echo "=========================================="
echo "操作系统: $(detect_os)"

# 先停止前端（依赖后端）
echo ""
echo "--- 停止前端服务 ---"
bash "$SCRIPT_DIR/stop-frontend.sh"

echo ""
echo "--- 停止后端服务 ---"
bash "$SCRIPT_DIR/stop-backend.sh"

echo ""
echo "=========================================="
echo "所有服务已停止"
echo "=========================================="