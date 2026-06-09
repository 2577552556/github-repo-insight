#!/bin/bash
# 停止所有服务脚本
# 使用方法: bash scripts/stop-all.sh
#
# 功能:
# 1. 停止前端服务
# 2. 停止后端服务

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "停止所有服务"
echo "=========================================="

# 先停止前端（可能依赖后端）
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