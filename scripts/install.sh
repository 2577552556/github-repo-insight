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
# 2. 创建 Python 虚拟环境
# ============================================
echo ""
echo "--- 创建 Python 虚拟环境 ---"
VENV_DIR="$PROJECT_DIR/backend/.venv"

# 确定 Python 命令
#优先使用 python，因为 python3 在 Windows Git Bash 中可能是无效的别名
if command_exists python; then
    #验证 python 是否可用
    if python -c "import sys; sys.exit(0)" 2>/dev/null; then
        PY_CMD=python
    elif command_exists python3 && python3 -c "import sys; sys.exit(0)" 2>/dev/null; then
        PY_CMD=python3
    else
        echo "❌ Python 不可用，无法创建虚拟环境"
        exit 1
    fi
elif command_exists python3; then
    PY_CMD=python3
else
    echo "❌ Python 未安装，无法创建虚拟环境"
    exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "创建虚拟环境..."
    cd "$PROJECT_DIR/backend"
    $PY_CMD -m venv .venv
    cd "$PROJECT_DIR"
    echo "✓ 虚拟环境已创建"
else
    echo "✓ 虚拟环境已存在"
fi

# ============================================
# 3. 安装 Python 依赖
# ============================================
echo ""
echo "--- 安装 Python 依赖 ---"
if [ "$python_ok" = true ]; then
    if [ -f "$PROJECT_DIR/backend/requirements.txt" ]; then
        echo "安装 Python 依赖到虚拟环境..."
        if [ "$OS_TYPE" = "windows" ]; then
            ACTIVATE_PATH="$PROJECT_DIR/backend/.venv/Scripts/activate"
            PIP_CMD="$PROJECT_DIR/backend/.venv/Scripts/pip"
        else
            ACTIVATE_PATH="$PROJECT_DIR/backend/.venv/bin/activate"
            PIP_CMD="$PROJECT_DIR/backend/.venv/bin/pip"
        fi

        # 直接使用 venv 的 pip 安装（不需要激活）
        $PIP_CMD install --upgrade pip
        $PIP_CMD install -r "$PROJECT_DIR/backend/requirements.txt"

        echo "✓ Python 依赖安装完成"
    else
        echo "⚠ requirements.txt 不存在，跳过"
    fi
else
    echo "⚠ Python 未正确安装，跳过"
fi

# ============================================
# 4. 安装 Node.js 依赖
# ============================================
echo ""
echo "--- 安装 Node.js 依赖 ---"
if [ "$node_ok" = true ] && [ "$npm_ok" = true ]; then
    if [ -f "$PROJECT_DIR/frontend/package.json" ]; then
        cd "$PROJECT_DIR/frontend"
        echo "安装 Node.js 依赖..."
        npm install
        cd "$PROJECT_DIR"
        echo "✓ Node.js 依赖安装完成"
    else
        echo "⚠ package.json 不存在，跳过"
    fi
else
    echo "⚠ Node.js 或 npm 未正确安装，跳过"
    echo ""
    echo "请安装 Node.js 18+:"
    echo "  Ubuntu/Debian: sudo apt install nodejs npm"
    echo "  CentOS/RHEL:   sudo yum install nodejs npm"
    echo "  macOS:         brew install node"
    echo "  Windows:       https://nodejs.org/"
fi

echo ""
echo "=========================================="
echo "依赖安装完成"
echo "=========================================="