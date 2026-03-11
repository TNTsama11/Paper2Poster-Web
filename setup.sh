#!/bin/bash
# Paper2Poster-Web 快速设置脚本

echo "======================================"
echo "Paper2Poster-Web 快速设置"
echo "======================================"

# 检查 Python 版本
echo "检查 Python 版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "当前 Python 版本: $python_version"

# 创建虚拟环境
echo ""
echo "创建虚拟环境..."
python3 -m venv venv

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo ""
echo "安装 Python 依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# 安装 Playwright 浏览器
echo ""
echo "安装 Playwright 浏览器..."
playwright install chromium

# 创建 .env 文件
if [ ! -f .env ]; then
    echo ""
    echo "创建 .env 文件..."
    cp .env.example .env
    echo "⚠️  请编辑 .env 文件并填入你的 API 密钥"
else
    echo ""
    echo "✓ .env 文件已存在"
fi

# 完成
echo ""
echo "======================================"
echo "✅ 设置完成！"
echo "======================================"
echo ""
echo "下一步："
echo "1. 编辑 .env 文件，填入你的 API 密钥"
echo "2. 将 PDF 文件放入 input/ 目录"
echo "3. 运行: python main.py input/your_paper.pdf"
echo ""
echo "使用虚拟环境:"
echo "  激活: source venv/bin/activate"
echo "  退出: deactivate"
echo ""

