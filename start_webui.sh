#!/bin/bash
# Paper2Poster-Web UI 启动脚本

echo "======================================"
echo "Paper2Poster-Web UI 启动器"
echo "======================================"
echo ""

# 检查虚拟环境
if [ -d "venv" ]; then
    echo "检测到虚拟环境，正在激活..."
    source venv/bin/activate
fi

# 选择 UI
echo "请选择要启动的 Web UI:"
echo ""
echo "  1) Gradio UI (推荐 - 简洁易用)"
echo "  2) Streamlit UI (功能丰富)"
echo ""
read -p "请输入选项 [1/2]: " choice

case $choice in
    1)
        echo ""
        echo "🚀 启动 Gradio UI..."
        echo "访问: http://localhost:7860"
        echo "按 Ctrl+C 停止服务"
        echo ""
        python webui_gradio.py
        ;;
    2)
        echo ""
        echo "🚀 启动 Streamlit UI..."
        echo "访问: http://localhost:8501"
        echo "按 Ctrl+C 停止服务"
        echo ""
        streamlit run webui_streamlit.py
        ;;
    *)
        echo "无效选项，默认启动 Gradio UI..."
        python webui_gradio.py
        ;;
esac

