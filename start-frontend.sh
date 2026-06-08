#!/bin/bash
# 前端启动脚本 - 日志输出到 logs/frontend.log

mkdir -p logs

cd frontend
npm run dev 2>&1 | tee ../logs/frontend.log