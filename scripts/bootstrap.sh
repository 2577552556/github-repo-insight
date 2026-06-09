#!/bin/bash
# 环境初始化脚本
# 跨平台兼容：支持 Linux/macOS/Windows (Git Bash/MSYS2)
# 使用方法: bash scripts/bootstrap.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 加载公共函数库
source "$SCRIPT_DIR/common.sh"

echo "=========================================="
echo "环境初始化脚本"
echo "=========================================="
echo "操作系统: $(detect_os)"
echo ""

# ============================================
# 1. 环境检查
# ============================================
echo "--- 环境检查 ---"

# 检查 Python
echo ""
echo "检查 Python..."
if check_python; then
    :
fi

# 检查 Node.js
echo ""
echo "检查 Node.js..."
if check_node; then
    :
fi

# 检查 npm
echo ""
echo "检查 npm..."
if check_npm; then
    :
fi

# ============================================
# 2. 创建必要目录
# ============================================
echo ""
echo "--- 创建必要目录 ---"
ensure_directories
echo "✓ 目录创建完成"

# ============================================
# 3. 检查配置文件
# ============================================
echo ""
echo "--- 检查配置文件 ---"
CRED_KEY_FILE="$PROJECT_DIR/backend/data/.credential_key"
if [ -f "$CRED_KEY_FILE" ]; then
    echo "✓ 加密密钥已存在"
else
    echo "加密密钥将在首次启动时自动生成"
fi

DB_FILE="$PROJECT_DIR/backend/data/analysis.db"
if [ -f "$DB_FILE" ]; then
    echo "✓ 数据库已存在"
else
    echo "数据库将在首次启动时自动创建"
fi

echo ""
echo "=========================================="
echo "环境初始化完成"
echo ""
echo "下一步:"
echo "  1. bash scripts/install.sh  安装依赖 (首次)"
echo "  2. bash scripts/start.sh 启动服务"
echo "=========================================="