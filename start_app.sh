#!/bin/bash

# 启动后端服务
echo \"启动后端服务...\"
cd /Users/wangxt/myspace/SearchPhoto/backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!

# 启动前端开发服务器
echo \"启动前端服务...\"
cd /Users/wangxt/myspace/SearchPhoto/frontend
npm run dev &
FRONTEND_PID=$!

# 等待进程
echo \"前端和后端服务已启动\"
echo \"前端PID: $FRONTEND_PID\"
echo \"后端PID: $BACKEND_PID\"

# 捕获退出信号并清理子进程
trap \"kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit\" SIGINT SIGTERM

# 等待任意键退出
read -p \"按任意键停止服务...\" -n1 -s

# 清理进程
kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
echo -e \"\\n服务已停止\"