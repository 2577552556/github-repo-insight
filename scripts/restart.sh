#!/bin/bash
# 重启所有服务
# 跨平台兼容：支持 Linux/macOS/Windows (Git Bash/MSYS2)
# 使用方法: bash scripts/restart.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 加载公共函数库
source "$SCRIPT_DIR/common.sh"

echo "=========================================="
echo "重启所有服务"
echo "=========================================="
echo "操作系统: $(detect_os)"

# 先停止
bash "$SCRIPT_DIR/stop.sh"

# 再启动
bash "$SCRIPT_DIR/start.sh"