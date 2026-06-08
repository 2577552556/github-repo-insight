#!/bin/bash
# 后端启动脚本 - 日志输出到 logs/backend.log

mkdir -p logs

cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --log-level info 2>&1 | tee ../logs/backend.log