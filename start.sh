#!/bin/bash
# ChatPure 一键启动脚本 (Linux/Mac)
# 使用方法：./start.sh

set -e

echo "🚀 启动 ChatPure..."
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 Python 3"
    echo "请先安装 Python 3.8 或更高版本"
    echo "下载地址：https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✅ $PYTHON_VERSION"

# 检查后端目录
if [ ! -d "$BACKEND_DIR" ]; then
    echo "❌ 错误：后端目录不存在：$BACKEND_DIR"
    exit 1
fi

# 检查前端目录
if [ ! -d "$SCRIPT_DIR/frontend" ]; then
    echo "❌ 错误：前端目录不存在：$SCRIPT_DIR/frontend"
    exit 1
fi

echo "✅ 前端目录：$SCRIPT_DIR/frontend"
echo "✅ 后端目录：$BACKEND_DIR"
echo ""

# 提示配置
echo "📝 配置说明："
echo "   - API Key: 设置环境变量 LLM_API_KEY"
echo "   - 端口：默认 8000，可设置 PORT 环境变量"
echo ""

# 启动服务
echo "🌐 服务地址：http://localhost:8000"
echo "💡 提示：按 Ctrl+C 停止服务"
echo ""

cd "$BACKEND_DIR"
exec python3 server.py
