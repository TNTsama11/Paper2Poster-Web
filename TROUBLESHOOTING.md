# 故障排查指南

本指南帮助你解决使用 Paper2Poster-Web 时遇到的常见问题。

## 🔴 LLM 相关错误

### 错误 1: "Pydantic Validation Error"

**症状:**
```
ValidationError: 8 validation errors for PosterContent
authors: Input should be a valid string
affiliation: Field required
...
```

**原因:** LLM 返回的 JSON 格式不符合要求

**解决方法:**

1. **使用更强大的模型**（推荐）
   ```env
   # 使用 GPT-4 而不是 GPT-3.5
   OPENAI_MODEL=gpt-4-turbo-preview
   
   # 或使用 DeepSeek
   OPENAI_MODEL=deepseek-chat
   ```

2. **降低 Temperature**
   - 在 Web UI 中将 Temperature 设为 0.2-0.3
   - 或修改 `config.py`:
     ```python
     TEMPERATURE = 0.2
     ```

3. **检查论文质量**
   - 确保 PDF 文本可以复制
   - 避免使用扫描版 PDF
   - 尝试更短或更结构化的论文

4. **已自动修复的问题**
   - v1.1.0+ 版本已添加自动数据修复
   - `authors` 列表自动转为字符串
   - 缺失字段自动填充默认值

### 错误 2: "JSON 解析失败"

**症状:**
```
JSONDecodeError: Expecting value: line 1 column 1
```

**原因:** LLM 返回的不是有效的 JSON

**解决方法:**

1. **检查模型配置**
   ```env
   # 确保使用支持 JSON 模式的模型
   OPENAI_MODEL=gpt-4-turbo-preview  # ✅ 支持
   OPENAI_MODEL=gpt-3.5-turbo        # ⚠️ 可能不稳定
   ```

2. **检查 API 响应**
   - 使用 `--save-json` 查看原始输出
   - 检查 API 是否正常工作

3. **网络问题**
   - 检查网络连接
   - 尝试使用代理

### 错误 3: "LLM 调用失败: Connection Error"

**原因:** 无法连接到 API 服务

**解决方法:**

1. **检查网络连接**
   ```bash
   # 测试连接
   curl -I https://api.openai.com
   ```

2. **检查 API URL**
   ```env
   # 确保 URL 正确
   OPENAI_BASE_URL=https://api.openai.com/v1  # 注意末尾的 /v1
   ```

3. **使用代理**（如果需要）
   ```bash
   export HTTP_PROXY=http://proxy:port
   export HTTPS_PROXY=http://proxy:port
   ```

### 错误 4: "API Key Error"

**症状:**
```
AuthenticationError: Invalid API key
```

**解决方法:**

1. **检查 API 密钥**
   - 确保密钥正确无误
   - 注意不要有多余的空格
   - 密钥格式通常是 `sk-...`

2. **检查账户状态**
   - 登录 API 服务提供商网站
   - 检查账户是否有余额
   - 检查密钥是否已过期

3. **重新创建密钥**
   - 删除旧密钥
   - 创建新密钥
   - 更新 `.env` 文件

## 📄 PDF 相关错误

### 错误 5: "PDF 文件不存在"

**解决方法:**
- 检查文件路径是否正确
- 确保文件有读取权限
- 文件名避免中文和特殊字符

### 错误 6: "提取的图片数量为 0"

**原因:** PDF 中没有可提取的图片

**解决方法:**

1. **检查 PDF 类型**
   - 确保不是扫描版
   - 图片应该是嵌入的，而不是背景

2. **调整图片尺寸阈值**
   编辑 `config.py`:
   ```python
   MIN_IMAGE_WIDTH = 100   # 从 200 降低到 100
   MIN_IMAGE_HEIGHT = 100  # 从 200 降低到 100
   ```

3. **手动添加图片**
   - 将图片放入 `output/images/` 目录
   - 命名为 `img_01.png`, `img_02.png` 等

## 🎨 渲染相关错误

### 错误 7: "Playwright Error"

**症状:**
```
playwright._impl._api_types.Error: Browser closed
```

**解决方法:**

1. **重新安装 Playwright**
   ```bash
   playwright install chromium
   ```

2. **使用国内镜像**
   ```bash
   export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/
   playwright install chromium
   ```

3. **检查系统依赖**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libgbm1
   ```

### 错误 8: "字体显示问题"

**症状:** 中文显示为方块或乱码

**解决方法:**

1. **检查网络连接**
   - 模板使用 Google Fonts
   - 需要能访问 Google

2. **使用本地字体**
   编辑 `templates/simple_grid.html`:
   ```html
   <!-- 删除或注释掉 Google Fonts -->
   <!-- @import url('https://fonts.googleapis.com/...'); -->
   
   <!-- 改用系统字体 -->
   <style>
   body {
       font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
   }
   </style>
   ```

## 🌐 Web UI 相关错误

### 错误 9: "端口被占用"

**症状:**
```
OSError: [Errno 98] Address already in use
```

**解决方法:**

1. **使用其他端口**
   
   **Gradio:**
   编辑 `webui_gradio.py`:
   ```python
   demo.launch(server_port=7861)  # 改为其他端口
   ```
   
   **Streamlit:**
   ```bash
   streamlit run webui_streamlit.py --server.port 8502
   ```

2. **关闭占用端口的进程**
   ```bash
   # 查找进程
   lsof -i :7860
   
   # 关闭进程
   kill -9 <PID>
   ```

### 错误 10: "无法访问 Web UI"

**解决方法:**

1. **检查防火墙**
   ```bash
   # Ubuntu
   sudo ufw allow 7860
   sudo ufw allow 8501
   ```

2. **检查服务状态**
   - 确认终端中显示 "Running on..."
   - 检查是否有错误信息

3. **尝试不同的地址**
   - `http://localhost:7860`
   - `http://127.0.0.1:7860`
   - `http://服务器IP:7860`

## 📦 依赖相关错误

### 错误 11: "ModuleNotFoundError"

**解决方法:**

1. **检查虚拟环境**
   ```bash
   # 确保已激活
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. **重新安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **检查 Python 版本**
   ```bash
   python --version  # 应该是 3.10+
   ```

### 错误 12: "版本冲突"

**解决方法:**

1. **创建新的虚拟环境**
   ```bash
   # 删除旧环境
   rm -rf venv
   
   # 创建新环境
   python3 -m venv venv
   source venv/bin/activate
   
   # 安装依赖
   pip install -r requirements.txt
   ```

2. **更新依赖**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

## 🔍 调试技巧

### 启用详细日志

编辑 `src/logger.py` 或在代码中：
```python
logger.setLevel(logging.DEBUG)  # 显示调试信息
```

### 保存中间数据

```bash
# 命令行模式
python main.py input/paper.pdf --save-json

# Web UI 模式
勾选 "保存 JSON 数据"
```

### 查看原始输出

检查生成的文件：
- `output/poster_content.json` - LLM 生成的数据
- `output/poster.html` - HTML 源文件
- 终端日志 - 详细的处理过程

### 测试单个模块

```python
# 测试 PDF 解析
from src.harvester import PDFHarvester
harvester = PDFHarvester("input/test.pdf", "output")
text, images, formulas = harvester.harvest()
print(f"提取到 {len(images)} 张图片, {len(formulas)} 个公式")

# 测试 LLM
from src.editor import LLMEditor
editor = LLMEditor(api_key="...", model="gpt-4")
# ... 测试
```

## 📞 获取更多帮助

如果以上方法都无法解决问题：

1. **查看日志**
   - 完整阅读终端输出
   - 查找 ERROR 和 WARNING 信息

2. **检查配置**
   - 验证 `.env` 文件
   - 运行 `python verify_setup.py`

3. **查看文档**
   - [README.md](README.md)
   - [QUICKSTART.md](QUICKSTART.md)
   - [WEBUI_GUIDE.md](WEBUI_GUIDE.md)

4. **提交 Issue**
   - 描述问题和错误信息
   - 提供使用的配置
   - 附上日志输出

## 🎯 性能优化建议

### 提高生成质量

1. **使用更好的模型**
   - GPT-4 > DeepSeek > GPT-3.5

2. **优化 PDF**
   - 使用文本清晰的 PDF
   - 避免复杂的排版

3. **调整参数**
   - Temperature: 0.2-0.3（更稳定）
   - Max Tokens: 4096（足够长）

### 提高处理速度

1. **使用更快的 API**
   - DeepSeek 响应较快
   - 或使用本地模型

2. **减少论文长度**
   - 只保留核心章节
   - 系统会自动截断超长文本

3. **优化网络**
   - 使用有线网络
   - 选择就近的 API 服务器

---

**提示:** 大部分问题可以通过使用更好的模型（GPT-4）和检查配置来解决。

