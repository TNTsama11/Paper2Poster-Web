# Paper2Poster-Web 项目摘要

## 项目概述
**项目代号**: Paper2Poster-Web (P2P-Web)  
**功能**: 自动将学术论文 PDF 转换为精美的学术海报  
**版本**: 1.1.0  
**开发语言**: Python 3.10+  
**界面**: 命令行 + Web UI (Gradio/Streamlit)

## 核心原理
PDF 解析 → LLM 结构化总结 → Jinja2 模板渲染 → Playwright 导出

## 技术栈
- **PDF 解析**: PyMuPDF (fitz)
- **AI 引擎**: OpenAI API（支持兼容接口）
- **数据验证**: Pydantic
- **模板渲染**: Jinja2
- **样式框架**: TailwindCSS (CDN)
- **导出引擎**: Playwright (无头浏览器)
- **其他**: python-dotenv, colorlog, Pillow, markdown

## 核心模块

### 1. 素材收割机 (Harvester) - `src/harvester.py`
**功能**: 从 PDF 中提取文本和图片
- 使用 PyMuPDF 解析 PDF
- 提取全文文本并清洗（去除页眉页脚）
- 提取所有分辨率 ≥ 200x200 的图片
- 输出: (full_text: str, image_manifest: List[str])

### 2. 智能编辑部 (Editor) - `src/editor.py`
**功能**: 调用 LLM 生成结构化内容
- 支持自定义 OpenAI 兼容 API
- 使用精心设计的 Prompt 引导 LLM
- 强制 JSON 格式输出
- 使用 Pydantic 验证数据结构
- 输出: PosterContent 对象

### 3. 排版印刷厂 (Renderer) - `src/renderer.py`
**功能**: 渲染 HTML 并导出为 PDF/PNG
- Jinja2 模板引擎渲染 HTML
- Playwright 无头浏览器导出
- 支持自定义海报尺寸
- 支持 PDF 和 PNG 两种格式

## 数据模型

### Section (章节)
```python
{
    "title": str,        # 章节标题
    "content": str       # Markdown 格式内容
}
```

### PosterContent (海报内容)
```python
{
    "title": str,                    # 海报标题
    "authors": str,                  # 作者列表
    "affiliation": str,              # 机构名称
    "abstract": str,                 # 摘要
    "introduction": Section,         # 引言
    "methods": Section,              # 方法
    "results": Section,              # 结果
    "conclusion": Section,           # 结论
    "main_figure_path": str | None,  # 主图文件名
    "main_figure_caption": str,      # 主图说明
    "references": List[str]          # 参考文献
}
```

## 使用方式

### 1. Web UI (推荐)
- **Gradio UI**: 简洁易用，`python webui_gradio.py`
- **Streamlit UI**: 功能丰富，`streamlit run webui_streamlit.py`
- 启动脚本: `./start_webui.sh` 或 `start_webui.bat`

### 2. 命令行
- 基本: `python main.py input/paper.pdf`
- 高级: 支持多种参数和批处理

### 3. API 调用
- 导入模块直接调用核心功能

## 文件结构
```
P2PW/
├── input/              # PDF 输入目录
├── output/             # 海报输出目录
│   └── images/        # 提取的图片
├── backups/           # 备份目录
├── src/               # 核心代码
│   ├── __init__.py
│   ├── harvester.py   # 模块1: PDF解析
│   ├── editor.py      # 模块2: LLM交互
│   ├── renderer.py    # 模块3: 渲染导出
│   ├── models.py      # 数据模型
│   └── logger.py      # 日志模块
├── templates/         # HTML 模板
│   └── simple_grid.html  # 默认三栏布局
├── main.py                # 主程序入口（命令行）
├── webui_gradio.py        # Gradio Web UI
├── webui_streamlit.py     # Streamlit Web UI
├── start_webui.sh         # Web UI 启动脚本
├── start_webui.bat        # Windows 启动脚本
├── config.py              # 配置文件
├── requirements.txt       # 依赖列表
├── env.example            # 环境变量示例
├── .gitignore
├── README.md              # 项目说明
├── WEBUI_GUIDE.md         # Web UI 使用指南
└── USAGE_EXAMPLES.md      # 使用示例
```

## 主要配置 (config.py)

```python
# API 配置
OPENAI_API_KEY        # 从 .env 读取
OPENAI_BASE_URL       # 默认: https://api.openai.com/v1
OPENAI_MODEL          # 默认: gpt-4-turbo-preview

# 图片过滤
MIN_IMAGE_WIDTH = 200
MIN_IMAGE_HEIGHT = 200

# 海报尺寸
POSTER_WIDTH = 1600
POSTER_HEIGHT = 1200

# LLM 参数
MAX_TOKENS = 4096
TEMPERATURE = 0.3     # 低温度保证稳定性
```

## 使用流程

1. **准备**: 放置 PDF 到 `input/` 目录
2. **配置**: 创建 `.env` 文件并填写 API 密钥
3. **运行**: `python main.py input/paper.pdf`
4. **输出**: 在 `output/` 目录获取海报

## 命令行参数
```bash
python main.py <pdf_path> [-f pdf|png] [-o output_name] 
               [-t template.html] [--save-json] [--no-backup]
```

## 扩展点

### 1. 自定义模板
- 复制 `templates/simple_grid.html`
- 修改 HTML 结构和 CSS 样式
- 使用 Jinja2 语法访问 `poster.*` 数据

### 2. 自定义 LLM
- 支持任何兼容 OpenAI API 的服务
- 修改 `.env` 中的 `OPENAI_BASE_URL` 和 `OPENAI_MODEL`

### 3. 优化 Prompt
- 编辑 `src/editor.py` 中的 `_build_system_prompt()`
- 调整生成策略和输出要求

### 4. 调整海报布局
- 修改 `templates/simple_grid.html` 的 CSS Grid 配置
- 可改为两栏、四栏或自由布局

## 关键特性

✅ **稳定性优先**: 使用成熟的技术栈  
✅ **模块化设计**: 三大模块独立解耦  
✅ **强类型约束**: Pydantic 保证数据质量  
✅ **高度可配置**: 支持自定义 API、模板、尺寸  
✅ **自动备份**: 防止覆盖已有文件  
✅ **详细日志**: 彩色日志输出便于调试  

## 已知限制

1. **文本长度**: 超长论文会被截断（可调整）
2. **图片识别**: 依赖 LLM 选择主图
3. **布局固定**: 默认为三栏布局
4. **语言支持**: 主要测试中英文

## 依赖安装

```bash
pip install -r requirements.txt
playwright install chromium
```

## 项目维护

- 配置文件: `config.py`, `.env`
- 日志位置: 控制台彩色输出
- 备份目录: `backups/`
- 中间文件: `output/poster.html`, `output/images/`

---

## Web UI 特性

### Gradio UI
- 现代化界面设计
- 拖拽上传文件
- 实时进度显示
- 自动文件下载
- 支持公网分享链接
- 内置详细说明

### Streamlit UI
- 功能丰富布局
- 侧边栏详细文档
- 快捷配置按钮
- 内容预览功能
- 专业数据展示

**访问地址:**
- Gradio: http://localhost:7860
- Streamlit: http://localhost:8501

---

**版本**: v1.1.0  
**最后更新**: 2025-12-17

