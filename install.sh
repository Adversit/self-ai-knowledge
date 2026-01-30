#!/bin/bash
# Self-AI-Knowledge 安装脚本

set -e

echo "🚀 安装 Self-AI-Knowledge"
echo "========================"

# 检查 Python 版本
python3 --version || { echo "❌ Python 3 required"; exit 1; }

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 升级 pip
echo "📦 升级 pip..."
pip install --upgrade pip

# 安装项目
echo "📦 安装项目依赖..."
pip install -e ".[dev]"

# 复制配置文件
if [ ! -f "config.toml" ]; then
    echo "📝 复制配置文件..."
    cp config.example.toml config.toml
    echo "⚠️  请编辑 config.toml 配置你的 AI CLI 路径"
fi

# 初始化数据库
echo "🗄️  初始化数据库..."
acv init

echo ""
echo "✅ 安装完成！"
echo ""
echo "下一步："
echo "1. 编辑 config.toml 配置 CLI 路径"
echo "2. 运行 'acv run claude' 开始录制会话"
echo "3. 运行 'acv web' 启动前端界面"
echo ""
