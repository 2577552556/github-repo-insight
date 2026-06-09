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
    if ! $PY_CMD -m venv .venv 2>&1; then
        echo ""
        echo "❌ 虚拟环境创建失败"
        echo ""
        echo "请先安装 python3-venv 包："
        echo "  Ubuntu/Debian: sudo apt install python3.12-venv"
        echo "  CentOS/RHEL:   sudo yum install python3.12-venv"
        echo "  或使用 root权限: sudo apt install python3-full python3.12-venv"
        echo ""
        echo "安装后删除 backend/.venv 目录，重新运行此脚本"
        cd "$PROJECT_DIR"
        exit 1
    fi
    cd "$PROJECT_DIR"
    echo "✓ 虚拟环境已创建"
else
    echo "✓ 虚拟环境已存在"
fi

# 检查虚拟环境 python 是否可用
if [ "$OS_TYPE" = "windows" ]; then
    VENV_PYTHON="$PROJECT_DIR/backend/.venv/Scripts/python"
else
    VENV_PYTHON="$PROJECT_DIR/backend/.venv/bin/python"
fi

if ! $VENV_PYTHON -c "import sys; sys.exit(0)" 2>/dev/null; then
    echo ""
    echo "❌ 虚拟环境不完整，请重新创建："
    echo "  rm -rf backend/.venv"
    echo "  bash scripts/install.sh"
    echo ""
    echo "如果仍失败，请先安装 python3-venv 系统包："
    echo "  Ubuntu/Debian: sudo apt install python3.12-venv"
    exit 1
fi

# ============================================
# 3. 安装 Python 依赖
# ============================================
echo ""
echo "--- 安装 Python 依赖 ---"
if [ "$python_ok" = true ]; then
    if [ -f "$PROJECT_DIR/backend/requirements.txt" ]; then
        echo "安装 Python 依赖到虚拟环境..."

        # 直接使用 venv 的 python -m pip 安装（更可靠）
        $VENV_PYTHON -m pip install --upgrade pip
        $VENV_PYTHON -m pip install -r "$PROJECT_DIR/backend/requirements.txt"

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