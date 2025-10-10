#!/bin/bash

# py-picToWork 启动脚本

echo "============================================================"
echo "  py-picToWork - 图像识别自动化工具"
echo "============================================================"
echo ""

# 检查虚拟环境是否存在
if [ ! -d "backend/venv" ]; then
    echo "❌ 虚拟环境不存在，正在创建..."
    python3 -m venv backend/venv
    echo "✅ 虚拟环境创建成功"
    echo ""
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source backend/venv/bin/activate

# 检查依赖是否安装
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 检测到依赖未安装，正在安装..."
    pip install -r backend/requirements.txt
    echo "✅ 依赖安装完成"
    echo ""
fi

echo "🚀 启动后端服务..."
echo ""
echo "📍 服务地址: http://localhost:8899"
echo "📖 API 文档: http://localhost:8899/docs"
echo ""
echo "提示: 按 Ctrl+C 停止服务"
echo "============================================================"
echo ""

# 启动服务
cd backend
python main.py










