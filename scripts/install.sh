#!/bin/bash
# 依赖安装脚本
# 跨平台兼容：支持 Linux/macOS/Windows (Git Bash/MSYS2)
# 使用方法: bash scripts/install.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 加载公共函数库
source "$SCRIPT_DIR/common.sh"

echo "=========================================="
echo "依赖安装脚本"
echo "=========================================="
echo "操作系统: $(detect_os)"
echo ""

# ============================================
# 1. 环境检查
# ============================================
echo "--- 环境检查 ---"

# 检查 Python
python_ok=false
if check_python; then
    python_ok=true
fi

# 检查 Node.js
node_ok=false
if check_node; then
    node_ok=true
fi

# 检查 npm
npm_ok=false
if check_npm; then
    npm_ok=true
fi

# ============================================
# 2. 安装 Python 依赖
# ============================================
echo ""
echo "--- 安装 Python 依赖 ---"
if [ "$python_ok" = true ]; then
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
else
    echo "⚠ Python 未正确安装，跳过"
fi

# ============================================
# 3. 安装 Node.js 依赖
# ============================================
echo ""
echo "--- 安装 Node.js 依赖 ---"
if [ "$node_ok" = true ] && [ "$npm_ok" = true ]; then
    if [ -f "$PROJECT_DIR/frontend/package.json" ]; then
        cd "$PROJECT_DIR/frontend"
        echo "安装 Node.js 依赖..."
        npm install
        cd "$PROJECT_DIR"
    else
        echo "⚠ package.json 不存在，跳过"
    fi
else
    echo "⚠ Node.js 或 npm 未正确安装，跳过"
fi

echo ""
echo "=========================================="
echo "依赖安装完成"
echo "=========================================="