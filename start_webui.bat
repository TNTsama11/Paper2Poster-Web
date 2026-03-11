@echo off
REM Paper2Poster-Web UI 启动脚本 (Windows)

echo ======================================
echo Paper2Poster-Web UI 启动器
echo ======================================
echo.

REM 检查虚拟环境
if exist "venv\Scripts\activate.bat" (
    echo 检测到虚拟环境，正在激活...
    call venv\Scripts\activate.bat
)

REM 选择 UI
echo 请选择要启动的 Web UI:
echo.
echo   1^) Gradio UI ^(推荐 - 简洁易用^)
echo   2^) Streamlit UI ^(功能丰富^)
echo.

set /p choice="请输入选项 [1/2]: "

if "%choice%"=="1" (
    echo.
    echo 🚀 启动 Gradio UI...
    echo 访问: http://localhost:7860
    echo 按 Ctrl+C 停止服务
    echo.
    python webui_gradio.py
) else if "%choice%"=="2" (
    echo.
    echo 🚀 启动 Streamlit UI...
    echo 访问: http://localhost:8501
    echo 按 Ctrl+C 停止服务
    echo.
    streamlit run webui_streamlit.py
) else (
    echo 无效选项，默认启动 Gradio UI...
    python webui_gradio.py
)

pause

