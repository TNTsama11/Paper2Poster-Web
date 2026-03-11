# Paper2Poster-Web (P2P-Web)

🎯 **自动将学术论文 PDF 转换为精美学术海报**

## 项目简介

Paper2Poster-Web 是一个基于 Python 的自动化工具，能够将学术论文 PDF 智能转换为结构清晰、视觉美观的学术海报。

### 核心特性

- 📄 **智能解析**: 自动提取论文文本和图片
- 🤖 **AI 驱动**: 使用 LLM 进行内容理解和结构化重组
- 🎨 **美观模板**: 基于 TailwindCSS 的现代化设计
- 🖼️ **多格式导出**: 支持 PDF 和 PNG 格式
- 🔧 **高度可配置**: 支持自定义 LLM API 和模板

### 技术架构

```
PDF 解析 → LLM 结构化总结 → Jinja2 模板渲染 → Playwright 导出
```

三大核心模块：
1. **素材收割机 (Harvester)**: 提取文本和图片
2. **智能编辑部 (Editor)**: LLM 生成结构化内容
3. **排版印刷厂 (Renderer)**: 渲染和导出海报

## 技术栈

- **Python 3.10+**
- **PDF 解析**: PyMuPDF (fitz)
- **AI 引擎**: OpenAI API（兼容自定义 API）
- **数据验证**: Pydantic
- **模板引擎**: Jinja2 + TailwindCSS
- **浏览器自动化**: Playwright

## 使用方式

Paper2Poster-Web 提供了三种使用方式：

1. **🎨 Web UI (推荐)** - 友好的图形界面，无需命令行
2. **⌨️ 命令行** - 灵活强大，适合批处理和自动化
3. **🔧 API 调用** - 集成到你的应用中

## 快速开始

### 方式 1: Web UI (推荐新手)

1. **安装依赖**

```bash
# 克隆项目
cd Paper2Poster-Web

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API 配置：

```env
# OpenAI API 配置
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4-turbo-preview

# 或使用其他兼容 OpenAI API 的服务
# OPENAI_BASE_URL=https://api.deepseek.com/v1
# OPENAI_MODEL=deepseek-chat
```

### 3. 启动 Web UI

```bash
# 使用启动脚本（推荐）
./start_webui.sh  # Linux/Mac
# 或
start_webui.bat   # Windows

# 或直接运行
python webui_gradio.py        # Gradio UI (推荐)
streamlit run webui_streamlit.py  # Streamlit UI
```

然后在浏览器中访问：
- Gradio UI: http://localhost:7860
- Streamlit UI: http://localhost:8501

**详细 Web UI 使用指南:** 查看 [WEBUI_GUIDE.md](WEBUI_GUIDE.md)

### 方式 2: 命令行

适合批处理和自动化场景。

**基本用法:**

```bash
# 基本用法
python main.py input/your_paper.pdf

# 指定输出格式为 PNG
python main.py input/your_paper.pdf -f png

# 自定义输出文件名
python main.py input/your_paper.pdf -o my_poster

# 保存 JSON 数据
python main.py input/your_paper.pdf --save-json

# 查看所有选项
python main.py --help
```

## 命令行参数

```
positional arguments:
  pdf_path              输入的 PDF 文件路径

optional arguments:
  -h, --help            显示帮助信息
  -f, --format {pdf,png}
                        输出格式 (默认: pdf)
  -o, --output OUTPUT   输出文件名（不含扩展名）
  -t, --template TEMPLATE
                        HTML 模板文件名 (默认: simple_grid.html)
  --no-backup          不备份已存在的输出文件
  --save-json          保存 LLM 生成的 JSON 数据
```

## 🌟 Web UI 特性

### Gradio UI (推荐)
- ✅ 简洁现代的界面设计
- ✅ 拖拽上传 PDF 文件
- ✅ 实时进度显示
- ✅ 自动文件下载
- ✅ 支持生成公网分享链接
- ✅ 内置详细使用说明

### Streamlit UI
- ✅ 功能丰富的布局
- ✅ 侧边栏详细说明
- ✅ 快捷配置按钮
- ✅ 内容预览功能
- ✅ 专业的数据展示

**选择建议:**
- 🎯 快速使用/演示 → Gradio UI
- 📊 日常工作 → Streamlit UI  
- ⚡ 批量处理 → 命令行

## 项目结构

```
Paper2Poster-Web/
├── input/                  # 输入 PDF 文件目录
├── output/                 # 输出目录
│   ├── images/            # 提取的图片
│   ├── poster.html        # 生成的 HTML
│   └── final_poster.pdf   # 最终海报
├── backups/               # 文件备份
├── src/                   # 源代码
│   ├── __init__.py
│   ├── harvester.py       # PDF 解析模块
│   ├── editor.py          # LLM 编辑模块
│   ├── renderer.py        # 渲染导出模块
│   ├── models.py          # 数据模型
│   └── logger.py          # 日志模块
├── templates/             # HTML 模板
│   └── simple_grid.html   # 默认三栏布局模板
├── config.py              # 配置文件
├── main.py                # 主程序入口（命令行）
├── webui_gradio.py        # Gradio Web UI
├── webui_streamlit.py     # Streamlit Web UI
├── start_webui.sh         # Web UI 启动脚本 (Linux/Mac)
├── start_webui.bat        # Web UI 启动脚本 (Windows)
├── requirements.txt       # 依赖列表
├── env.example            # 环境变量示例
├── .gitignore
├── README.md              # 项目说明
├── WEBUI_GUIDE.md         # Web UI 详细指南
└── USAGE_EXAMPLES.md      # 使用示例
```

## 自定义配置

### 修改海报尺寸

编辑 `config.py`：

```python
# 海报尺寸配置 (像素)
POSTER_WIDTH = 1920   # 修改宽度
POSTER_HEIGHT = 1440  # 修改高度
```

### 使用自定义 LLM API

项目支持任何兼容 OpenAI API 格式的服务，例如：

- DeepSeek API
- Azure OpenAI
- 本地部署的 LLM（如 Ollama + litellm）

只需在 `.env` 中配置对应的 `OPENAI_BASE_URL` 和 `OPENAI_MODEL`。

### 自定义模板

1. 复制 `templates/simple_grid.html` 创建新模板
2. 使用 Jinja2 语法访问 `poster` 对象的所有字段
3. 运行时使用 `-t your_template.html` 指定模板

可用的数据结构：
```
poster.title              # 标题
poster.authors            # 作者
poster.affiliation        # 机构
poster.abstract           # 摘要
poster.introduction       # 引言 {title, content}
poster.methods            # 方法 {title, content}
poster.results            # 结果 {title, content}
poster.conclusion         # 结论 {title, content}
poster.main_figure_path   # 主图文件名
poster.main_figure_caption # 主图说明
poster.references         # 参考文献列表
```

## 常见问题

### 1. 中文字体显示问题

模板已使用 Google Fonts 的 Noto Sans SC，支持中文。如需离线字体，可下载字体文件到 `templates/` 目录并修改 CSS。

### 2. Playwright 安装失败

```bash
# 手动安装浏览器
python -m playwright install chromium

# 如果网络问题，设置镜像
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/
```

### 3. LLM 生成内容不理想

- 尝试更换更强大的模型（如 GPT-4）
- 调整 `config.py` 中的 `TEMPERATURE` 参数
- 检查输入 PDF 的文本质量

### 4. 图片提取失败

- 确保 PDF 包含图片（而非扫描件）
- 调整 `config.py` 中的 `MIN_IMAGE_WIDTH` 和 `MIN_IMAGE_HEIGHT`

## 优化建议

### 性能优化
- 对于超长论文，可以预先裁剪 PDF 至关键章节
- 使用更快的 LLM API（如 DeepSeek）降低成本

### 质量优化
- 使用高质量的 PDF 文件
- 确保 PDF 文本可复制（非图片扫描）
- 为重要论文手动审核 JSON 输出

## 开发指南

### 添加新模板

1. 在 `templates/` 目录创建新的 `.html` 文件
2. 使用 Jinja2 语法和 TailwindCSS 样式
3. 确保包含 `<script src="https://cdn.tailwindcss.com"></script>`

### 扩展功能

项目采用模块化设计，可轻松扩展：

- **Harvester**: 添加更多 PDF 解析逻辑
- **Editor**: 自定义 Prompt 或使用其他 LLM
- **Renderer**: 支持更多导出格式（如 SVG）

## 许可证

MIT License

## 致谢

- PyMuPDF: PDF 处理
- OpenAI: AI 能力
- Playwright: 浏览器自动化
- TailwindCSS: 现代化样式

---

**注意**: 本项目生成的海报仅供学术交流使用，请遵守相关版权规定。

