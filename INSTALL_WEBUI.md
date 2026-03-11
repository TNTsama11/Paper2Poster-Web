# Web UI 安装指南

本指南将帮助你快速安装并启动 Paper2Poster-Web 的图形界面。

## 🚀 快速安装（3 步完成）

### 步骤 1: 安装 Python 依赖

如果你已经安装过命令行版本的依赖，只需额外安装 Web UI 组件：

```bash
# 安装 Web UI 依赖
pip install gradio>=4.0.0 streamlit>=1.28.0
```

如果是全新安装，运行：

```bash
# 完整安装
pip install -r requirements.txt
playwright install chromium
```

### 步骤 2: 配置 API 密钥

确保你已经创建并配置了 `.env` 文件：

```bash
# 复制模板
cp env.example .env

# 编辑 .env，填入你的 API 密钥
nano .env
```

至少需要配置：
```env
OPENAI_API_KEY=your-api-key-here
```

### 步骤 3: 启动 Web UI

```bash
# 使用启动脚本（推荐）
./start_webui.sh

# 或直接运行 Gradio UI
python webui_gradio.py

# 或直接运行 Streamlit UI
streamlit run webui_streamlit.py
```

## 🎯 选择你的界面

### Gradio UI - 推荐新手

**优点:**
- 界面简洁美观
- 操作直观易懂
- 支持生成分享链接
- 加载速度快

**启动:**
```bash
python webui_gradio.py
```

**访问:** http://localhost:7860

### Streamlit UI - 推荐高级用户

**优点:**
- 功能更丰富
- 有侧边栏文档
- 快捷配置按钮
- 数据展示专业

**启动:**
```bash
streamlit run webui_streamlit.py
```

**访问:** http://localhost:8501

## 🔧 详细安装步骤

### Windows 用户

1. **安装 Python 3.10+**
   - 从 https://www.python.org/ 下载并安装
   - 确保勾选 "Add Python to PATH"

2. **打开命令提示符 (CMD)**
   ```cmd
   cd C:\path\to\Paper2Poster\P2PW
   ```

3. **创建虚拟环境（推荐）**
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

4. **安装依赖**
   ```cmd
   pip install -r requirements.txt
   playwright install chromium
   ```

5. **配置 API**
   ```cmd
   copy env.example .env
   notepad .env
   ```

6. **启动**
   ```cmd
   start_webui.bat
   ```

### Linux/Mac 用户

1. **确保有 Python 3.10+**
   ```bash
   python3 --version
   ```

2. **克隆/进入项目目录**
   ```bash
   cd /path/to/Paper2Poster/P2PW
   ```

3. **使用自动安装脚本**
   ```bash
   ./setup.sh
   ```

4. **或手动安装**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   playwright install chromium
   ```

5. **配置 API**
   ```bash
   cp env.example .env
   nano .env
   ```

6. **启动**
   ```bash
   ./start_webui.sh
   ```

## 📦 依赖说明

### 核心依赖（命令行已安装）
- PyMuPDF - PDF 解析
- openai - LLM API
- pydantic - 数据验证
- jinja2 - 模板渲染
- playwright - 浏览器自动化

### Web UI 依赖（新增）
- **gradio** - Gradio Web UI 框架
- **streamlit** - Streamlit Web UI 框架

## 🌐 网络访问

### 局域网访问

**Gradio:**
编辑 `webui_gradio.py`，修改 `demo.launch()`:
```python
demo.launch(
    server_name="0.0.0.0",  # 允许外部访问
    server_port=7860
)
```

**Streamlit:**
```bash
streamlit run webui_streamlit.py --server.address 0.0.0.0
```

然后在局域网内通过 `http://服务器IP:端口` 访问。

### 公网访问（Gradio）

编辑 `webui_gradio.py`:
```python
demo.launch(share=True)  # 生成公网链接
```

Gradio 会生成一个临时的 `https://xxx.gradio.live` 链接，有效期 72 小时。

**⚠️ 安全提示:** 
- 公网访问请注意保护 API 密钥
- 不要在公网界面中保存敏感信息
- 建议只在需要分享时开启

## 🐛 常见问题

### Q1: 提示 "No module named 'gradio'"

**解决:**
```bash
pip install gradio streamlit
```

### Q2: 端口被占用

**Gradio (7860):**
编辑 `webui_gradio.py`:
```python
demo.launch(server_port=7861)  # 改为其他端口
```

**Streamlit (8501):**
```bash
streamlit run webui_streamlit.py --server.port 8502
```

### Q3: 浏览器无法访问

1. 检查防火墙设置
2. 确认服务已正常启动
3. 尝试使用 `127.0.0.1` 代替 `localhost`

### Q4: Playwright 错误

```bash
# 重新安装 Playwright 浏览器
playwright install chromium

# 或使用国内镜像
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/
playwright install chromium
```

### Q5: API 调用失败

1. 检查 `.env` 文件是否正确配置
2. 确认 API 密钥有效
3. 检查网络连接
4. 确认 API 账户有余额

## 📊 性能优化

### 减少内存占用

只安装需要的 UI：

```bash
# 只用 Gradio
pip install gradio

# 只用 Streamlit  
pip install streamlit
```

### 提高启动速度

使用轻量级模型（如 GPT-3.5 或 DeepSeek）可以显著提高响应速度。

### 多用户访问

如需支持多用户同时访问，建议：
1. 使用性能较好的服务器
2. 配置 Nginx 反向代理
3. 考虑使用队列系统

## 🔄 更新 Web UI

```bash
# 更新到最新版
git pull

# 更新依赖
pip install -r requirements.txt --upgrade

# 重新启动
./start_webui.sh
```

## 📖 进一步学习

- **基础使用:** 查看 [QUICKSTART.md](QUICKSTART.md)
- **详细指南:** 查看 [WEBUI_GUIDE.md](WEBUI_GUIDE.md)
- **高级用法:** 查看 [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)
- **项目说明:** 查看 [README.md](README.md)

## 💡 小贴士

1. **首次使用**
   - 推荐使用 Gradio UI
   - 先用小文件测试
   - 熟悉界面布局

2. **日常使用**
   - 选择你喜欢的界面
   - 保存常用配置到 `.env`
   - 善用快捷键（Ctrl+C 停止服务）

3. **团队协作**
   - 使用公网分享功能
   - 或部署到服务器
   - 注意保护 API 密钥

## 🎉 开始使用

现在你已经完成安装！打开浏览器，访问 Web UI，上传你的第一篇论文吧！

**Gradio UI:** http://localhost:7860  
**Streamlit UI:** http://localhost:8501

祝使用愉快！ 🚀

