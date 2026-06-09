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
# 3. 安装后端依赖
# ============================================
echo ""
echo "--- 安装后端依赖 ---"
if [ -f "$PROJECT_DIR/backend/requirements.txt" ]; then
    cd "$PROJECT_DIR/backend"
    echo "安装 Python 依赖..."
    if command_exists pip3; then
        pip3 install -r requirements.txt
    elif command_exists pip; then
        pip install -r requirements.txt
    else
        echo "⚠ pip 未安装，跳过 Python 依赖安装"
    fi
    cd "$PROJECT_DIR"
else
    echo "⚠ requirements.txt 不存在，跳过"
fi

# ============================================
# 4. 安装前端依赖
# ============================================
echo ""
echo "--- 安装前端依赖 ---"
if [ -f "$PROJECT_DIR/frontend/package.json" ]; then
    cd "$PROJECT_DIR/frontend"
    echo "安装 Node.js 依赖..."
    if command_exists npm; then
        npm install
    else
        echo "⚠ npm 未安装，跳过 Node.js 依赖安装"
    fi
    cd "$PROJECT_DIR"
else
    echo "⚠ package.json 不存在，跳过"
fi

# ============================================
# 5. 生成加密主密钥（如果不存在）
# ============================================
echo ""
echo "--- 检查加密配置 ---"
CRED_KEY_FILE="$PROJECT_DIR/backend/data/.credential_key"
if [ -f "$CRED_KEY_FILE" ]; then
    echo "✓ 加密密钥已存在"
else
    echo "加密密钥将在首次启动时自动生成"
fi

# ============================================
# 6. 创建数据库（如果不存在）
# ============================================
echo ""
echo "--- 检查数据库 ---"
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
echo "下一步: 运行 'bash scripts/start.sh' 启动服务"
echo "=========================================="