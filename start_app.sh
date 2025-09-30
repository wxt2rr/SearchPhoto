#!/bin/bash

# 检查并处理端口占用
check_and_kill_port() {
    local port=$1
    local process_info=$(lsof -ti:$port 2>/dev/null)
    
    if [ ! -z "$process_info" ]; then
        echo "检测到端口 $port 被占用，正在终止占用进程..."
        echo "占用进程: $process_info"
        
        # 尝试优雅终止
        kill -TERM $process_info 2>/dev/null
        sleep 2
        
        # 检查是否还在运行
        local still_running=$(lsof -ti:$port 2>/dev/null)
        if [ ! -z "$still_running" ]; then
            echo "进程仍在运行，强制终止..."
            kill -KILL $still_running 2>/dev/null
            sleep 1
        fi
        
        # 最终检查
        local final_check=$(lsof -ti:$port 2>/dev/null)
        if [ -z "$final_check" ]; then
            echo "端口 $port 已释放"
        else
            echo "警告: 无法释放端口 $port"
        fi
    else
        echo "端口 $port 可用"
    fi
}

# 检查并处理端口占用
echo "检查端口占用情况..."
check_and_kill_port 9527  # 后端端口
check_and_kill_port 5173  # 前端端口（Vite默认）

# 启动后端服务
echo "启动后端服务..."
cd /Users/wangxt/myspace/SearchPhoto/backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!

# 等待后端启动
echo "等待后端服务启动..."
sleep 3

# 检查后端是否成功启动
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "错误: 后端服务启动失败"
    exit 1
fi

# 启动前端开发服务器
echo "启动前端服务..."
cd /Users/wangxt/myspace/SearchPhoto/frontend
npm run dev &
FRONTEND_PID=$!

# 等待前端启动
echo "等待前端服务启动..."
sleep 3

# 检查前端是否成功启动
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "错误: 前端服务启动失败"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# 显示服务状态
echo ""
echo "✅ 服务启动成功!"
echo "📊 服务状态:"
echo "  后端服务 (端口9527): PID $BACKEND_PID"
echo "  前端服务 (端口5173): PID $FRONTEND_PID"
echo ""
echo "🌐 访问地址:"
echo "  前端: http://localhost:5173"
echo "  后端API: http://localhost:9527"
echo ""
echo "💡 提示: 按 Ctrl+C 或任意键停止服务"

# 捕获退出信号并清理子进程
cleanup() {
    echo ""
    echo "🛑 正在停止服务..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "✅ 服务已停止"
    exit 0
}

trap cleanup SIGINT SIGTERM

# 等待任意键退出
read -p "按任意键停止服务..." -n1 -s

# 清理进程
cleanup