# 快速开始指南

## 一、安装依赖

### 方法 1: 使用自动安装脚本（推荐）

```bash
./setup.sh
```

### 方法 2: 手动安装

```bash
# 1. 创建虚拟环境（可选但推荐）
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 2. 安装 Python 依赖
pip install -r requirements.txt

# 3. 安装 Playwright 浏览器
playwright install chromium
```

## 二、配置 API 密钥

1. 复制配置文件模板：
```bash
cp env.example .env
```

2. 编辑 `.env` 文件，填入你的 API 配置：

```env
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4-turbo-preview
```

### 常用 API 配置示例

**OpenAI GPT-4:**
```env
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4-turbo-preview
```

**SiliconFlow (推荐 - 国内快速访问):**
```env
OPENAI_API_KEY=your-siliconflow-key
OPENAI_BASE_URL=https://api.siliconflow.cn/v1
OPENAI_MODEL=Qwen/Qwen2.5-72B-Instruct
```
📖 详细指南: [SILICONFLOW_GUIDE.md](SILICONFLOW_GUIDE.md)

**DeepSeek (更便宜):**
```env
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat
```

## 三、选择使用方式

Paper2Poster-Web 提供两种使用方式：

### 🎨 方式 1: Web UI (推荐新手)

**优点:** 图形界面，无需命令行，易于使用

**启动方法:**
```bash
# Linux/Mac
./start_webui.sh

# Windows
start_webui.bat

# 或直接运行
python webui_gradio.py
```

然后在浏览器访问 http://localhost:7860

**详细指南:** 查看 [WEBUI_GUIDE.md](WEBUI_GUIDE.md)

### ⌨️ 方式 2: 命令行

**优点:** 灵活强大，适合批处理

继续阅读下面的步骤。

---

## 四、验证安装

```bash
python verify_setup.py
```

如果看到 "✅ 项目设置验证通过！" 说明安装成功。

## 五、运行示例 (命令行)

### 1. 准备 PDF 文件

将你的论文 PDF 放入 `input/` 目录：

```bash
cp /path/to/your/paper.pdf input/
```

### 2. 运行转换

```bash
# 生成 PDF 海报
python main.py input/paper.pdf

# 或生成 PNG 海报
python main.py input/paper.pdf -f png
```

### 3. 查看结果

生成的海报在 `output/` 目录中：
- `output/final_poster.pdf` 或 `output/final_poster.png` - 最终海报
- `output/poster.html` - 中间 HTML 文件
- `output/images/` - 提取的图片

## 六、常见问题

### Q1: 提示 "未设置 OPENAI_API_KEY"

**解决方法**: 
1. 确保已创建 `.env` 文件（不是 `env.example`）
2. 检查 `.env` 文件中的 API 密钥是否正确填写
3. API 密钥不要有多余的空格或引号

### Q2: Playwright 安装失败

**解决方法**:
```bash
# 手动安装
python -m playwright install chromium

# 如果网络问题，使用镜像
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/
python -m playwright install chromium
```

### Q3: 生成的海报内容不理想

**解决方法**:
1. 尝试使用更强大的模型（如 GPT-4）
2. 使用 `--save-json` 保存中间数据，然后手动修改
3. 确保输入 PDF 的文本可以正常复制（不是扫描件）

### Q4: 中文显示问题

**解决方法**:
模板已使用 Google Fonts 的 Noto Sans SC 字体，支持中文。如果仍有问题，请检查网络连接是否能访问 Google Fonts。

## 七、下一步

- 🎨 阅读 [WEBUI_GUIDE.md](WEBUI_GUIDE.md) 学习 Web UI
- 📖 阅读 [README.md](README.md) 了解项目详情
- 💡 查看 [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) 学习高级用法
- 🖼️ 自定义模板：复制 `templates/simple_grid.html` 并修改
- ⚙️ 调整配置：编辑 `config.py` 修改海报尺寸等参数

## 八、获取帮助

查看所有命令行选项：
```bash
python main.py --help
```

## 完整示例

```bash
# 1. 安装
./setup.sh

# 2. 配置
cp env.example .env
nano .env  # 编辑并填入 API 密钥

# 3. 验证
python verify_setup.py

# 4. 转换
cp ~/Downloads/my_paper.pdf input/
python main.py input/my_paper.pdf -f png --save-json

# 5. 查看结果
open output/final_poster.png
```

恭喜！你已经成功完成 Paper2Poster-Web 的设置 🎉

