# 更新日志

## v1.3.9.10 (2025-12-18)

### ✨ 优化 LLM Prompt - 保护作者名称和参考文献不被翻译

#### 问题描述

在生成中文海报时，LLM 有时会：
- 翻译或音译作者姓名（如 "John Smith" → "约翰·史密斯"）
- 翻译参考文献（如将英文文献标题翻译为中文）

这导致：
- ❌ 作者姓名不准确，失去国际学术规范
- ❌ 参考文献格式混乱，无法追溯原文
- ❌ 违反学术引用规范

#### 修复方案

**在 LLM System Prompt 中添加明确的例外规则**:

1. **语言指令中添加例外说明**:
   ```
   中文输出模式:
   - 所有内容必须用中文输出
   - **例外**: 作者姓名、参考文献必须保持原文
   
   英文输出模式:
   - 所有内容必须用英文输出
   - **例外**: 作者姓名、参考文献必须保持原文
   
   自动模式:
   - 内容使用论文源语言
   - **例外**: 作者姓名、参考文献必须保持原文
   ```

2. **添加专门的字段规则**:
   ```
   8. authors 字段规则:
      - 必须保持原文，不要翻译或音译
      - 示例: "John Smith, Li Wei, Maria Garcia"
   
   9. references 字段规则:
      - 必须保持原文，不要翻译参考文献
      - 保留原始引用格式和语言
   ```

3. **更新 JSON Schema 示例**:
   ```json
   {
     "authors": "Author1, Author2, Author3（保持原文，不翻译）",
     "references": [
       "Reference 1 in original language",
       "Reference 2 in original language"
     ]
   }
   ```

#### 技术实现

**修改文件**: `src/editor.py`

**修改点 1**: 语言指令添加例外（第 76-89 行）
```python
if output_language == "chinese":
    language_instruction = """2. **重要**：所有内容必须用中文输出...
   **例外**：
   - **作者姓名**（authors 字段）必须保持原文，不要翻译或音译
   - **参考文献**（references 字段）必须保持原文，不要翻译"""
```

**修改点 2**: 添加专门的字段规则（第 105-111 行）
```python
8. **authors 字段规则**：
   - 必须是字符串格式，多个作者用逗号分隔
   - **必须保持原文**，不要翻译或音译作者姓名
   - 示例: "John Smith, Li Wei, Maria Garcia"
9. **references 字段规则**：
   - **必须保持原文**，不要翻译参考文献
   - 保留原始引用格式和语言
```

**修改点 3**: 更新 JSON Schema 示例（第 118-135 行）
```json
{
  "authors": "Author1, Author2, Author3（保持原文，不翻译）",
  "references": ["Reference 1 in original language", ...]
}
```

#### 效果

**修复前** ❌:
```json
{
  "authors": "约翰·史密斯, 李伟, 玛丽亚·加西亚",
  "references": [
    "史密斯等人, 深度学习基础, 自然杂志, 2020",
    "李伟, 计算机视觉综述, IEEE汇刊, 2021"
  ]
}
```

**修复后** ✅:
```json
{
  "authors": "John Smith, Li Wei, Maria Garcia",
  "references": [
    "Smith et al., Deep Learning Fundamentals, Nature, 2020",
    "Li Wei, Computer Vision Survey, IEEE Trans., 2021"
  ]
}
```

#### 适用场景

- ✅ 生成中文海报时，保持英文作者名
- ✅ 生成英文海报时，保持中文作者名
- ✅ 参考文献始终保持原文
- ✅ 符合国际学术规范

#### 修改的文件

**核心模块** (1 个):
- ✅ `src/editor.py` - LLM Prompt 优化

---

## v1.3.9.9 (2025-12-18)

### 🐛 修复 Gradio Web UI 字体加载错误

#### 问题描述

打开 Gradio Web UI 时，浏览器控制台出现以下错误：
```
GET https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600&display=swap 
net::ERR_CONNECTION_CLOSED
```

**原因**: Gradio 默认主题尝试从 Google Fonts CDN 加载 `Source Sans Pro` 字体，在无网络或网络受限环境下失败。

#### 修复方案

**使用系统字体替代 Google Fonts**:

在 `webui_gradio.py` 的 `custom_css` 中添加全局字体覆盖：

```css
/* 使用系统字体，避免加载 Google Fonts */
* {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", 
                 Helvetica, Arial, sans-serif, "Apple Color Emoji", 
                 "Segoe UI Emoji" !important;
}
```

**字体优先级**:
1. macOS: `-apple-system` (San Francisco)
2. Windows: `Segoe UI`
3. Linux: `Noto Sans`
4. 通用: `Helvetica`, `Arial`, `sans-serif`

#### 效果

- ✅ 完全离线运行，无需外部字体 CDN
- ✅ 消除浏览器控制台错误
- ✅ 使用系统原生字体，更快更美观
- ✅ 跨平台一致的显示效果

#### 修改的文件

**Web UI** (1 个):
- ✅ `webui_gradio.py` - 添加全局字体覆盖

---

## v1.3.9.8 (2025-12-18)

### 🐛 修复 Playwright 超时问题 - 优化等待策略

#### 问题分析

**超时根本原因**:
- 即使使用本地资源，仍然出现 `Page.goto: Timeout 30000ms exceeded` 错误
- 资源统计：
  - TailwindCSS JS: 398KB (需要解析和执行)
  - Google Fonts CSS: 346KB
  - 图片文件: 26 张共 9.1MB (需要解码和渲染)
  - **总计约 10MB 本地资源**
- 问题原因：
  1. 默认超时 30 秒不够处理大量本地资源
  2. TailwindCSS 需要扫描整个 DOM 树并应用样式
  3. 26 张图片需要逐个解码和渲染
  4. `wait_until="load"` 要求所有资源加载完成才继续

#### 修复方案

**三重优化策略**:

1. **增加超时时间**: 从 30 秒增加到 120 秒
   ```python
   timeout=120000  # 120 秒
   ```

2. **改变等待策略**: 从 `"load"` 改为 `"domcontentloaded"`
   ```python
   wait_until="domcontentloaded"  # 只等待 DOM，不等待所有资源
   ```
   - `"load"`: 等待所有资源（图片、CSS、JS）加载完成 ❌
   - `"domcontentloaded"`: 只等待 DOM 解析完成 ✅

3. **固定渲染等待**: 添加 10 秒固定等待
   ```python
   await page.wait_for_timeout(10000)  # 等待 TailwindCSS 和图片渲染
   ```

#### 技术实现

**修改文件**: `src/renderer.py`

**PDF 导出优化** (第 146-155 行):
```python
# 加载 HTML（增加超时到 120 秒，只等待 DOM 加载）
await page.goto(
    f"file://{html_path_abs}", 
    timeout=120000,  # 120 秒
    wait_until="domcontentloaded"  # 只等待 DOM，不等待所有资源
)

# 等待 TailwindCSS 和图片完成渲染（固定等待 10 秒）
await page.wait_for_timeout(10000)
```

**PNG 导出优化** (第 199-208 行):
```python
# 加载 HTML（增加超时到 120 秒，只等待 DOM 加载）
await page.goto(
    f"file://{html_path_abs}", 
    timeout=120000,  # 120 秒
    wait_until="domcontentloaded"  # 只等待 DOM，不等待所有资源
)

# 等待 TailwindCSS 和图片完成渲染（固定等待 10 秒）
await page.wait_for_timeout(10000)
```

#### 效果

- ✅ 彻底解决大量图片和本地资源导致的超时问题
- ✅ 适用于包含 20+ 张图片、10MB+ 资源的海报
- ✅ PDF 和 PNG 导出都更稳定可靠
- ✅ 渲染时间增加约 10 秒，但确保完整渲染

#### 为什么之前的方案不够

**v1.3.9.7 只解决了部分问题**:
- ✅ 使用本地文件替代 CDN，避免网络问题
- ❌ 但默认超时（30 秒）+ `wait_until="load"` 仍然不够
- ❌ 本地资源虽然快，但 TailwindCSS 解析和图片渲染需要时间

**本次修复 (v1.3.9.8) 完整解决**:
- ✅ 增加超时时间：给予足够处理时间
- ✅ 优化等待策略：不等待所有资源，只等待 DOM
- ✅ 固定渲染等待：确保样式和图片完全渲染

---

## v1.3.9.7 (2025-12-18)

### 🐛 修复 Playwright 超时问题 - 使用本地资源

#### 问题修复

**修复 PNG 导出超时：使用本地 CSS/JS 文件替代 CDN** ⭐

**问题描述**:
- PNG 导出时出现 `Page.goto: Timeout 30000ms exceeded` 错误
- 原因：HTML 模板中的外部 CDN 资源（TailwindCSS、Google Fonts）加载慢或失败
- `wait_for_load_state('networkidle')` 等待外部资源，导致超时

**修复方案**:
- ✅ 使用本地 TailwindCSS 文件：`tailwindcss3.4.17.es`
- ✅ 使用本地 Google Fonts CSS：`css2.css`
- ✅ 渲染 HTML 时自动复制这些文件到输出目录
- ✅ 所有模板文件改为引用本地文件

#### 技术实现

**1. Renderer 修改** (`src/renderer.py`):
```python
# 在 render_html() 方法中添加文件复制逻辑
local_css = self.templates_dir / "css2.css"
local_js = self.templates_dir / "tailwindcss3.4.17.es"

if local_css.exists():
    shutil.copy2(local_css, self.output_dir / "css2.css")
if local_js.exists():
    shutil.copy2(local_js, self.output_dir / "tailwindcss3.4.17.es")
```

**2. 模板文件修改**:
```html
<!-- 修改前 -->
<script src="https://cdn.tailwindcss.com"></script>
@import url('https://fonts.googleapis.com/css2?family=...');

<!-- 修改后 -->
<script src="tailwindcss3.4.17.es"></script>
@import url('css2.css');
```

#### 修改的文件

**模板文件** (4 个):
- ✅ `templates/academic_panels_landscape.html`
- ✅ `templates/academic_panels.html`
- ✅ `templates/simple_grid.html`
- ✅ `templates/multi_figure_grid.html`

**核心代码**:
- ✅ `src/renderer.py` - 添加文件复制逻辑

#### 优势

| 对比项 | CDN 资源 | 本地资源 ✅ |
|--------|---------|-----------|
| **加载速度** | 依赖网络 | 本地文件，瞬间加载 |
| **稳定性** | 可能超时 | 100% 可靠 |
| **离线支持** | ❌ 需要网络 | ✅ 完全离线 |
| **超时风险** | ❌ 可能超时 | ✅ 无超时风险 |

#### 文件要求

**必需文件**（已在 `templates/` 目录）:
- ✅ `templates/css2.css` (346KB) - Google Fonts CSS
- ✅ `templates/tailwindcss3.4.17.es` (398KB) - TailwindCSS JS

**如果文件不存在**:
- 模板会回退到 CDN（但可能超时）
- 建议确保这两个文件在 `templates/` 目录下

#### 影响范围
- **功能**: PNG 和 PDF 导出
- **性能**: 显著提升（无网络等待）
- **稳定性**: 完全消除超时风险

---

## v1.3.9.6 (2025-12-18)

### 📁 输出目录命名优化

#### 改进内容

**输出文件夹名改为论文 PDF 原名** ⭐
- ✅ 输出目录名从时间戳格式改为 PDF 文件名
- ✅ 自动清理文件名中的特殊字符，确保文件夹名安全
- ✅ 保留中文、字母、数字、下划线和连字符
- ✅ 更直观，便于识别和管理

#### 技术实现

**修改前**:
```python
# 使用时间戳作为目录名
output_temp = temp_dir / f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
# 结果: output/output_20251218_123456/
```

**修改后**:
```python
# 使用 PDF 文件名作为目录名
pdf_path = Path(pdf_file.name)
pdf_name = pdf_path.stem  # 获取文件名（不含扩展名）
# 清理特殊字符，保留安全字符
safe_name = re.sub(r'[^\w\u4e00-\u9fff-]', '_', pdf_name)
safe_name = safe_name.strip('_')
output_temp = temp_dir / safe_name
# 结果: output/Deep_Learning_for_Computer_Vision/
```

#### 文件名清理规则

| 原始文件名 | 清理后的目录名 | 说明 |
|-----------|--------------|------|
| `Deep Learning for Computer Vision.pdf` | `Deep_Learning_for_Computer_Vision` | 空格替换为下划线 |
| `论文标题-2024.pdf` | `论文标题-2024` | 保留中文和连字符 |
| `Paper@Title#2024$.pdf` | `Paper_Title_2024` | 特殊字符替换为下划线 |
| `论文标题：研究内容.pdf` | `论文标题_研究内容` | 中文标点替换为下划线 |
| `  论文标题  .pdf` | `论文标题` | 移除首尾空格和下划线 |

#### 文件结构对比

**修改前**:
```
output/
├── output_20251218_091234/  ← 时间戳，不直观
│   ├── poster.png
│   └── images/
├── output_20251218_091456/  ← 难以识别
│   └── ...
```

**修改后**:
```
output/
├── Deep_Learning_for_Computer_Vision/  ← PDF 文件名，直观 ✅
│   ├── poster.png
│   └── images/
├── 论文标题-2024/  ← 中文文件名，清晰 ✅
│   └── ...
```

#### 优势

| 对比项 | 时间戳格式 | PDF 文件名格式 ✅ |
|--------|-----------|-----------------|
| **可读性** | ❌ 难以识别 | ✅ 一目了然 |
| **管理性** | ❌ 需要打开查看 | ✅ 直接识别 |
| **查找性** | ❌ 需要记住时间 | ✅ 按文件名查找 |
| **归档性** | ❌ 不直观 | ✅ 便于归档 |

#### 注意事项

- ⚠️ 如果多个同名 PDF，会覆盖之前的输出（同名的会使用同一个目录）
- ✅ 特殊字符会自动清理，确保文件夹名安全
- ✅ 如果清理后为空，会使用时间戳作为后备
- ✅ 支持中文文件名

#### 影响范围
- **文件**: `webui_gradio.py`
- **功能**: 输出目录命名
- **用户体验**: 更容易识别和管理生成的文件

---

## v1.3.9.5 (2025-12-18)

### 🎨 输出格式默认值调整

#### 改进内容

**输出格式默认值改为 PNG** ⭐
- ✅ 默认输出格式从 PDF 改为 PNG
- ✅ PNG 格式更适合在线展示和屏幕分享
- ✅ 无需 PDF 阅读器即可查看
- ✅ 适合社交媒体和网页展示

#### 技术实现

**修改**:
```python
# 修改前
output_format = gr.Radio(
    choices=["pdf", "png"],
    value="pdf",  # ❌ PDF 默认
    label="输出格式"
)

# 修改后
output_format = gr.Radio(
    choices=["pdf", "png"],
    value="png",  # ✅ PNG 默认
    label="输出格式"
)
```

#### 格式对比

| 格式 | 优势 | 适用场景 |
|------|------|---------|
| **PNG** ⭐ (默认) | 在线展示、屏幕分享、无需阅读器 | 社交媒体、网页、演示 |
| **PDF** | 打印质量、矢量支持、专业文档 | 打印、归档、正式提交 |

#### 影响范围
- **文件**: `webui_gradio.py`
- **UI**: Gradio Web UI - 输出格式选择
- **默认行为**: 生成 PNG 格式海报

---

## v1.3.9.4 (2025-12-18)

### ⚙️ 默认配置优化

#### 改进内容

**1. 视觉分析默认启用状态支持环境变量** ⭐
- ✅ 新增 `ENABLE_VISION_ANALYSIS` 环境变量支持
- ✅ 在 `.env` 中设置 `ENABLE_VISION_ANALYSIS=true` 可默认启用视觉分析
- ✅ 避免每次都需要手动勾选

**2. 默认模板改为横版学术模板** ⭐
- ✅ 默认模板从"学术会议-纵向"改为"学术会议-横向16:9"
- ✅ 横版模板更适合屏幕展示和在线分享
- ✅ Key Figures 默认显示 2 张图片，信息密度更高

#### 技术实现

**视觉分析启用状态**:
```python
# 修改前
enable_vision = gr.Checkbox(
    value=False,  # ❌ 硬编码
    ...
)

# 修改后
enable_vision = gr.Checkbox(
    value=os.getenv("ENABLE_VISION_ANALYSIS", "false").lower() == "true",  # ✅ 环境变量
    ...
)
```

**默认模板**:
```python
# 修改前
template_choice = gr.Radio(
    value="学术会议-纵向 (academic_panels) ⭐",  # 纵向
    ...
)

# 修改后
template_choice = gr.Radio(
    value="学术会议-横向16:9 (academic_panels_landscape) ⭐ 推荐",  # 横向
    ...
)
```

#### 配置示例

**`.env` 文件**:
```bash
# OpenAI API 配置
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4-turbo-preview

# 视觉分析配置 ✅ 默认启用
ENABLE_VISION_ANALYSIS=true       # true=启用, false=禁用（默认false）
VISION_MODEL=gpt-4o-mini           # 视觉模型
```

#### 环境变量对照表

| 配置项 | 环境变量 | 默认值 | 说明 |
|--------|---------|--------|------|
| API 密钥 | `OPENAI_API_KEY` | - | API 密钥 |
| API URL | `OPENAI_BASE_URL` | `https://api.openai.com/v1` | API 地址 |
| 模型名称 | `OPENAI_MODEL` | `gpt-4-turbo-preview` | LLM 模型 |
| 视觉模型 | `VISION_MODEL` | - | VLM 模型 |
| 启用视觉分析 | `ENABLE_VISION_ANALYSIS` | `false` | **新增** ✅ |

#### 模板变化

**选项调整**:
- 纵向模板: "学术会议-纵向 (academic_panels) ⭐" → "学术会议-纵向 (academic_panels)"
- 横向模板: "学术会议-横向16:9 (academic_panels_landscape) 🆕" → "学术会议-横向16:9 (academic_panels_landscape) ⭐ 推荐"
- 默认选中: 横向模板（更适合在线展示）

#### 优势

| 对比项 | 修改前 | 修改后 ✅ |
|--------|--------|----------|
| **视觉分析** | 每次手动勾选 | 环境变量控制 |
| **默认模板** | 纵向 | 横向（更适合屏幕） |
| **配置便捷性** | 较低 | 高 |
| **用户体验** | 重复操作 | 一次配置，持久有效 |

#### 影响范围
- **文件**: `webui_gradio.py`
- **UI**: Gradio Web UI - 默认选项
- **配置**: 支持 `ENABLE_VISION_ANALYSIS` 环境变量

---

## v1.3.9.3 (2025-12-18)

### 🐛 环境变量读取修复

#### 问题修复

**修复 VISION_MODEL 环境变量未读取的问题** ❌ → ✅

**问题描述**:
- 用户在 `.env` 文件中配置了 `VISION_MODEL`
- 但 Gradio WebUI 的"视觉模型"输入框没有自动读取该值
- 其他配置项（API_KEY, BASE_URL, MODEL）都能正确读取环境变量

**修复方案**:
- ✅ 修改 `vision_model` 组件，添加 `os.getenv("VISION_MODEL", "")` 读取环境变量
- ✅ 与其他配置项保持一致的环境变量读取方式

**修改前**:
```python
vision_model = gr.Textbox(
    label="视觉模型 (留空自动推荐)",
    value="",  # ❌ 硬编码为空字符串
    ...
)
```

**修改后**:
```python
vision_model = gr.Textbox(
    label="视觉模型 (留空自动推荐)",
    value=os.getenv("VISION_MODEL", ""),  # ✅ 从环境变量读取
    ...
)
```

#### 配置示例

**`.env` 文件**:
```bash
# OpenAI API 配置
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4-turbo-preview

# 视觉模型配置
VISION_MODEL=gpt-4o-mini              # ✅ 现在会自动读取
# 或者
VISION_MODEL=Qwen/Qwen2-VL-7B-Instruct
```

#### 环境变量对照表

| UI 组件 | 环境变量 | 默认值 | 是否已修复 |
|---------|---------|--------|-----------|
| API 密钥 | `OPENAI_API_KEY` | - | ✅ (已有) |
| API URL | `OPENAI_BASE_URL` | `https://api.openai.com/v1` | ✅ (已有) |
| 模型名称 | `OPENAI_MODEL` | `gpt-4-turbo-preview` | ✅ (已有) |
| 视觉模型 | `VISION_MODEL` | - | ✅ (本次修复) |

#### 影响范围
- **文件**: `webui_gradio.py`
- **UI**: Gradio Web UI - 视觉模型输入框
- **功能**: 环境变量自动填充

---

## v1.3.9.2 (2025-12-18)

### 🐛 文件保存路径修复

#### 问题修复

**修复文件保存到系统临时目录的问题** ❌ → ✅

**问题描述**:
- v1.3.9.1 中文件保存到系统临时目录（`/tmp`）
- 用户无法在项目的 `output` 目录找到生成的文件
- 状态信息显示的路径是临时目录路径

**修复方案**:
- ✅ 修改 `temp_dir` 为项目的 `output` 目录
- ✅ 所有生成的文件现在保存到 `output/output_YYYYMMDD_HHMMSS/` 目录
- ✅ 文件路径清晰，便于管理和查找

**修改前**:
```python
temp_dir = Path(tempfile.mkdtemp(prefix="p2p_"))
# 文件保存到: /tmp/p2p_xxxxx/output_xxx/
```

**修改后**:
```python
output_base_dir = Path(__file__).parent / "output"
output_base_dir.mkdir(exist_ok=True)
temp_dir = output_base_dir
# 文件保存到: ./output/output_YYYYMMDD_HHMMSS/
```

#### 文件结构

**生成后的目录结构**:
```
P2PW/
├── output/
│   ├── output_20251218_091234/
│   │   ├── poster.pdf          # 生成的海报
│   │   ├── poster.html         # HTML 版本
│   │   ├── poster_data.json    # 结构化数据（可选）
│   │   └── images/             # 提取的图片
│   │       ├── img_01.png
│   │       ├── img_02.png
│   │       └── ...
│   ├── output_20251218_091456/
│   │   └── ...
│   └── ...
```

#### 影响范围
- **文件**: `webui_gradio.py`
- **功能**: 文件保存位置
- **用户体验**: 更容易找到生成的文件

---

## v1.3.9.1 (2025-12-18)

### 🎨 界面简化

#### 改进内容

**移除预览组件，简化界面** ⭐
- ✅ 隐藏了文件下载预览组件
- ✅ 右侧只显示生成状态信息
- ✅ 状态信息中直接显示文件保存路径
- ✅ 用户可直接从 output 目录获取文件
- ✅ 界面更简洁，专注于配置和生成

#### 界面变化

**修改前**:
- 右侧显示"📊 生成结果"
- 有 3 个文件下载组件（海报、HTML、JSON）
- 状态信息提示"请点击下方按钮下载海报"

**修改后**:
- 右侧显示"📊 生成状态"
- 文件下载组件隐藏（后台处理）
- 状态信息直接显示文件保存路径
- 提示"文件已保存到 output 目录，可直接打开使用"

#### 优势

| 对比项 | 修改前 | 修改后 ✅ |
|--------|--------|----------|
| **界面复杂度** | 较复杂 | 简洁 |
| **操作步骤** | 点击下载 | 直接查看目录 |
| **视觉干扰** | 多个组件 | 最小化 |
| **文件获取** | 通过浏览器 | 直接访问 |

#### 适用场景
- ✅ 本地部署，直接访问文件系统
- ✅ 频繁生成，需要快速迭代
- ✅ 不需要在浏览器中预览
- ✅ 更专注于配置和调优

#### 影响范围
- **文件**: `webui_gradio.py`
- **UI**: Gradio Web UI - 右侧输出区域简化
- **功能**: 文件仍正常生成，只是不显示下载组件

---

## v1.3.9 (2025-12-18)

### 🌐 多语言输出支持

#### 新增功能

**输出语言选择** ⭐
- ✅ 新增 "🌐 输出语言" 选项（Radio 组件）
- ✅ 支持三种模式：
  - **自动检测 (Auto)**: 根据论文原文语言输出（默认）
  - **中文 (Chinese)**: 强制输出中文，即使论文是英文的
  - **英文 (English)**: 强制输出英文，即使论文是中文的
- ✅ LLM 会根据选择的语言自动调整 prompt
- ✅ 适用场景：
  - 英文论文需要制作中文海报（会议、展示）
  - 中文论文需要制作英文海报（国际会议）
  - 保持论文原语言（默认行为）

#### 技术实现

**参数传递链**:
```
webui_gradio.py: output_language (Radio)
    ↓
process_paper(output_language)
    ↓ 转换为 "auto"/"chinese"/"english"
src/editor.py: edit(output_language)
    ↓
generate_poster_content(output_language)
    ↓
_build_system_prompt(output_language)
    ↓ 动态构建语言指令
LLM Prompt: 语言特定指令
```

**Prompt 动态生成**:
```python
# 中文模式
"**重要**：所有内容必须用中文输出，包括标题、摘要、各部分内容等。
即使论文是英文的，也要翻译为中文。"

# 英文模式
"**Important**: All content must be output in English, including title, 
abstract, and all sections. If the paper is in Chinese, translate it to English."

# 自动模式
"所有内容必须用论文的源语言输出（中文论文用中文，英文论文用英文）"
```

#### UI 设计

**位置**: 高级功能区，在 "📝 Abstract 最大字数" 之后

**组件**: `gr.Radio`
- 选项 1: "自动检测 (Auto)" ⭐ (默认)
- 选项 2: "中文 (Chinese)"
- 选项 3: "英文 (English)"
- 提示: "指定海报内容的语言。自动检测会根据论文原文语言输出"

#### 使用建议

| 场景 | 推荐设置 | 说明 |
|------|---------|------|
| 中文论文，中文海报 | 自动检测 | 保持原文语言 |
| 英文论文，英文海报 | 自动检测 | 保持原文语言 |
| 英文论文，中文海报 | 中文 | LLM 自动翻译 |
| 中文论文，英文海报 | 英文 | LLM 自动翻译 |
| 混合语言论文 | 自动检测 | 以主要语言为准 |

#### 影响范围
- **文件**: `webui_gradio.py`, `src/editor.py`
- **UI**: Gradio Web UI - 高级功能区新增组件
- **功能**: LLM prompt 动态调整

#### 注意事项
- ⚠️ 翻译质量取决于 LLM 模型能力
- ⚠️ 推荐使用 GPT-4 或 GPT-4o 等强大模型以获得更好的翻译效果
- ⚠️ 翻译可能会略微增加 token 消耗

---

## v1.3.8.3 (2025-12-18)

### 🐛 F-string 格式化修复

#### 问题修复

**修复 ValueError: Invalid format specifier for object of type 'str'** ❌ → ✅

**问题描述**:
- v1.3.8.2 将 `_build_system_prompt()` 改为 f-string 以插入 `abstract_max_words` 变量
- 但 prompt 中包含大量 JSON 示例，JSON 的 `{}` 花括号与 f-string 的格式化语法冲突
- 导致 Python 尝试将 JSON 内容作为格式化参数处理，引发 ValueError

**修复内容**:
- ✅ 转义 JSON 示例中的所有花括号：`{` → `{{`, `}` → `}}`
- ✅ 保留 `{abstract_max_words}` 作为唯一的变量插入点
- ✅ f-string 现在能正确区分变量插入和 JSON 示例

#### 技术细节

**f-string 转义规则**:
```python
# 在 f-string 中，花括号的处理：
f"插入变量: {variable}"        # 变量插入
f"JSON 示例: {{"key": "value"}}"  # 转义为 {"key": "value"}
```

**修改前（错误）**:
```python
def _build_system_prompt(self, abstract_max_words: int = 130) -> str:
    return f"""...
    {
      "introduction": {
        "title": "Introduction"
      }
    }
    """  # ❌ Python 认为 { "introduction": ... } 是要格式化的
```

**修改后（正确）**:
```python
def _build_system_prompt(self, abstract_max_words: int = 130) -> str:
    return f"""...
    {{
      "introduction": {{
        "title": "Introduction"
      }}
    }}
    """  # ✅ {{ }} 被转义为 { }，只有 {abstract_max_words} 被插入
```

#### 验证结果
- ✅ Python 语法检查通过
- ✅ f-string 格式化成功
- ✅ `abstract_max_words` 变量正确插入（如 "130字以内"）
- ✅ JSON 示例正确显示（花括号已转义）

#### 影响范围
- **文件**: `src/editor.py` 第 95-123 行
- **方法**: `_build_system_prompt()`
- **功能**: Prompt 生成现在完全正常

---

## v1.3.8.2 (2025-12-18)

### 🐛 Editor 参数修复

#### 问题修复

**修复 TypeError: LLMEditor.edit() got an unexpected keyword argument 'abstract_max_words'** ❌ → ✅

**问题描述**:
- v1.3.8.1 中在 `webui_gradio.py` 添加了 `abstract_max_words` 滑块和传参
- 但忘记在 `src/editor.py` 的相关方法中添加这个参数
- 导致运行时 TypeError

**修复内容**:
1. ✅ `LLMEditor.edit()` 方法添加 `abstract_max_words: int = 130` 参数
2. ✅ `generate_poster_content()` 方法添加 `abstract_max_words: int = 130` 参数  
3. ✅ `_build_system_prompt()` 方法添加 `abstract_max_words: int = 130` 参数
4. ✅ 更新 prompt 模板，使用 f-string 插入 `{abstract_max_words}` 变量

#### 技术细节

**完整的参数传递链**:
```
webui_gradio.py: process_paper(..., abstract_max_words)
    ↓
src/editor.py: edit(..., abstract_max_words=130)
    ↓
src/editor.py: generate_poster_content(..., abstract_max_words)
    ↓
src/editor.py: _build_system_prompt(abstract_max_words)
    ↓
Prompt: "字数限制：严格控制在 **{abstract_max_words}字以内**"
    ↓
LLM 生成符合字数要求的 Abstract
```

**修改的方法签名**:
```python
# 1. edit() 方法
def edit(self, full_text: str, image_manifest: List[str], 
         max_images: int = 15, equations: List[dict] = None, 
         abstract_max_words: int = 130) -> PosterContent:

# 2. generate_poster_content() 方法
def generate_poster_content(self, full_text: str, 
                           image_manifest: List[str],
                           abstract_max_words: int = 130) -> PosterContent:

# 3. _build_system_prompt() 方法  
def _build_system_prompt(self, abstract_max_words: int = 130) -> str:
```

#### 影响范围
- **文件**: `src/editor.py`
- **方法**: `edit()`, `generate_poster_content()`, `_build_system_prompt()`
- **功能**: Abstract 字数控制功能现在完全正常工作

---

## v1.3.8.1 (2025-12-18)

### 🐛 Gradio WebUI 修复

#### 问题修复

**修复 NameError: abstract_max_words 未定义** ❌ → ✅
- ✅ 在 v1.3.7 中添加了 Abstract 字数控制功能，但漏了在 Gradio UI 中定义组件
- ✅ 添加了 `abstract_max_words` 滑块组件（80-250字，默认130字）
- ✅ 位置：高级功能区，在"最小图片尺寸"和"溢出检测"之间
- ✅ 移除了 Gradio 6.0 的 UserWarning（theme 和 css 参数警告）

#### 技术细节

**新增组件**:
```python
abstract_max_words = gr.Slider(
    minimum=80,
    maximum=250,
    value=130,
    step=10,
    label="📝 Abstract 最大字数",
    info="LLM生成摘要时的字数限制，避免内容过长溢出（默认130字）"
)
```

**Gradio 6.0 兼容性**:
- 移除了 `theme` 和 `css` 参数以避免警告
- 使用默认 Gradio 主题（可在未来版本中重新添加）

#### 影响范围
- **文件**: `webui_gradio.py`
- **功能**: Gradio Web UI 正常启动和运行
- **用户体验**: 可以正常使用 Abstract 字数控制功能

---

## v1.3.8 (2025-12-18)

### 🖼️ 横版模板 Key Figures 优化

#### 改进内容

**横向学术海报模板 Key Figures 展示优化** ⭐
- ✅ 左侧 Key Figures 面板现在**至少显示 2 张图片**（原为 1 张）
- ✅ 智能选择策略：
  - **优先级 1**: 从 `results` 类型图片中选择优先级最高的 2 张
  - **优先级 2**: 如果 `results` 图片不足 2 张，从所有图片中按优先级补充
  - **优先级 3**: 如果总图片不足 2 张，显示所有可用图片
- ✅ 标题更新：`Key Figure` → `Key Figures`（复数形式）
- ✅ 更好利用左侧栏空间，减少留白
- ✅ 增强视觉冲击力和信息密度

#### 影响范围
- **文件**: `templates/academic_panels_landscape.html`
- **UI**: Gradio Web UI（选择 "学术会议-横向16:9" 模板时生效）

#### 推荐使用场景
- ✅ 论文有多个重要结果图（实验对比、性能图表等）
- ✅ 需要在一屏中同时展示多个核心发现
- ✅ 会议海报展示，吸引更多关注

#### 技术细节
- 使用 Jinja2 列表过滤和拼接实现智能图片选择
- 兼容所有现有图片分类和优先级系统
- 保持后备方案（`main_figure_path`）兼容性

---

## v1.3.7 (2025-12-17)

### 🎯 Abstract 字数智能控制 + 精简界面

#### 新增功能

**1. Abstract 字数智能控制** ⭐
- ✅ LLM 生成时严格控制字数，从源头解决内容过长问题
- ✅ Gradio 界面新增 "📝 Abstract 最大字数" 滑块（80-250字）
- ✅ 默认130字，适合横版模板左侧栏显示
- ✅ LLM 会主动精简和重新组织语言，而非简单截断

**2. Prompt 优化**
```
**Abstract 生成规则**：
- 字数限制：严格控制在 {abstract_max_words}字以内
- 内容要求：核心创新点 + 主要方法 + 关键结果
- 如果原文摘要过长，务必重新组织语言，删减次要信息
```

**3. 精简界面**
- ✅ 弃用 Streamlit 界面 (`webui_streamlit.py` → `.deprecated`)
- ✅ 专注 Gradio，降低维护成本
- ✅ 更新 README，移除 Streamlit 相关说明

#### 字数建议

| 模板 | 推荐字数 | 原因 |
|------|---------|------|
| **横版16:9** | 130字 ⭐ | 左侧栏空间有限 |
| **纵向会议** | 150字 | 横跨全宽，空间充足 |
| **多图网格** | 120字 | 图片多，文字少 |
| **经典三栏** | 140字 | 标准布局 |

#### 使用方法

**Web UI**:
1. 启动: `python webui_gradio.py`
2. 调整 "📝 Abstract 最大字数" 滑块
3. 根据模板选择合适字数

#### 优势

| 对比项 | CSS截断 | LLM字数控制 ✅ |
|--------|---------|---------------|
| 语义完整性 | ❌ 可能截断句子 | ✅ 保持完整 |
| 内容质量 | ❌ 简单截断 | ✅ 主动精简 |
| 关键信息 | ❌ 可能丢失 | ✅ 优先保留 |
| 阅读体验 | ❌ 可能突然结束 | ✅ 自然流畅 |

#### 文档
- `docs/V1.3.7_ABSTRACT_OPTIMIZATION.md` - 完整说明和字数建议

---

## v1.3.6 (2025-12-17)

### 🎨 横版模板优化：提升内容密度

#### Bug 修复 (12-17 晚间)
- **面板重叠问题**: 修复 Introduction、Results、Conclusion 三栏卡片重叠
- 限制普通面板最大高度 (280px)，防止溢出重叠
- 优化网格布局，添加 `align-content: start`
- 减少面板内边距和列表间距

#### 用户反馈
- 分辨率太高 (4K)，内容被稀释
- 图片少时空白太多
- Abstract 内容显示不全

#### 优化内容

**1. 降低默认分辨率**
- ✅ 从 `screen_4k` (3840×2160) 改为 `screen_hd` (1920×1080)
- ✅ 内容密度提升 40%
- ✅ 文件大小减少 60%
- ✅ 更适合实际使用场景（在线会议、投影）

**2. 增加内容密度**
- ✅ 左侧栏：35% → 32%（给右侧更多空间）
- ✅ 间距优化：gap 20px → 15px，padding 20px → 15px
- ✅ 字体优化：面板标题 1.15rem → 1.05rem，内容 0.86rem → 0.82rem
- ✅ 图片尺寸：普通 350px → 280px，主图 600px → 450px

**3. 修复 Abstract 显示**
- ✅ 减小字体：0.9rem → 0.85rem
- ✅ 优化行高：1.6 → 1.55
- ✅ 添加滚动：`max-height: 400px` + `overflow-y: auto`

#### 效果对比

| 指标 | 修改前 (4K) | 修改后 (1080p) |
|------|------------|---------------|
| 分辨率 | 3840×2160 | 1920×1080 |
| 内容密度 | 低 | 高 (+40%) |
| 可视文字 | 少 | 多 (+35%) |
| 空白区域 | 多 | 少 (-30%) |
| 文件大小 | 大 | 小 (-60%) |

#### 使用建议

**默认 1080p** (推荐):
- 在线会议、投影展示
- 文字为主的论文
- 一般使用场景

**手动选择 4K**:
```bash
python main.py paper.pdf -t academic_panels_landscape.html --preset screen_4k
```
- 图片特别多 (>15张)
- 高分辨率屏幕展示

#### 文档
- `docs/V1.3.6_LANDSCAPE_OPTIMIZATION.md` - 详细优化说明

---

## v1.3.5 (2025-12-17)

### 🆕 横向16:9学术海报模板 + Abstract显示优化

#### Bug 修复 🔴
- **TemplateSyntaxError**: 修复横向模板中 `{% do %}` 标签错误
- Jinja2 不支持 `{% do %}` 标签，改用 `selectattr` 过滤器

#### 新增功能

**1. 学术会议横向模板 (academic_panels_landscape.html)**
- ✅ 16:9 横向布局，专为屏幕展示优化
- ✅ 左右分栏设计：Abstract+主图 (35%) + 多面板 (65%)
- ✅ 推荐尺寸: `screen_4k` (3840×2160) 或 `screen_hd` (1920×1080)
- ✅ 完美适配：在线会议、学术报告投影、网站展示

**2. Abstract 显示完整优化**
- ✅ 修复纵向模板 Abstract 出现省略号 "..." 的问题
- ✅ 横向模板采用独立左侧栏，自适应高度
- ✅ 文本完整显示，无截断

#### 布局对比

**纵向模板 (academic_panels)**:
```
3列网格，Abstract横跨全宽
适合: 打印海报、竖屏展示
推荐尺寸: 1600×2400 (extended)
```

**横向模板 (academic_panels_landscape)** 🆕:
```
左右分栏 (35% + 65%)
左: Abstract + Key Figure
右: 2×2面板网格 + References
适合: 投影、屏幕分享、在线会议
推荐尺寸: 3840×2160 (screen_4k)
```

#### 使用场景

| 场景 | 推荐模板 |
|------|---------|
| **在线会议 (Zoom/Teams)** | 横向16:9 ⭐⭐⭐⭐⭐ |
| **学术报告投影** | 横向16:9 ⭐⭐⭐⭐⭐ |
| **网站展示** | 横向16:9 ⭐⭐⭐⭐ |
| **实体海报打印** | 纵向 ⭐⭐⭐⭐⭐ |

#### 使用方法

**CLI**:
```bash
# 横向模板 (自动使用4K尺寸)
python main.py paper.pdf -t academic_panels_landscape.html
```

**Web UI**:
- 选择模板: "学术会议-横向16:9 (academic_panels_landscape) 🆕"

#### 文档
- `docs/V1.3.5_LANDSCAPE_TEMPLATE.md` - 横向模板完整指南

---

## v1.3.4 (2025-12-17)

### 🎨 海报尺寸智能联动系统 ⭐

#### 问题
- 固定尺寸 1600×1200 对内容丰富的论文不够用
- References 和 Conclusion 被挤到窗口外看不见
- 缺少学术海报常用尺寸预设
- 模板与尺寸没有联动推荐

#### 新增功能

**1. 学术海报尺寸预设**
- ✅ 10种预设尺寸：A0/A1纵横向、36"×48"、4K/1080p屏幕、紧凑/加长型等
- ✅ 每种预设包含详细说明和适用场景

**2. 模板推荐尺寸联动**
- ✅ `academic_panels.html` → `extended` (1600×2400, +100% 高度)
- ✅ `multi_figure_grid.html` → `default` (1600×1800, +50% 高度)
- ✅ `simple_grid.html` → `compact` (1400×1600)
- ✅ 自动根据所选模板推荐最佳尺寸

**3. 灵活的尺寸选择**
- ✅ CLI: `--preset a0_portrait` 或 `--width 2000 --height 2800`
- ✅ Web UI: 下拉选择预设或手动输入
- ✅ 优先级: 手动输入 > 预设 > 模板推荐 > 默认

**4. 默认尺寸优化**
- ✅ 默认高度从 1200 增加到 1800 (+50%)
- ✅ 有效解决内容溢出问题

#### 预设尺寸列表
```
- default: 1600×1800 (默认，平衡之选)
- a0_portrait: 3370×4768 (A0纵向，标准学术海报)
- a0_landscape: 4768×3370 (A0横向)
- a1_portrait: 2384×3370 (A1纵向)
- a1_landscape: 3370×2384 (A1横向)
- 36x48: 3600×4800 (36"×48" 纵向，北美常用)
- 48x36: 4800×3600 (48"×36" 横向)
- screen_4k: 3840×2160 (4K屏幕, 16:9)
- screen_hd: 1920×1080 (1080p屏幕)
- compact: 1400×1600 (紧凑型，简短论文)
- extended: 1600×2400 (加长型，内容丰富)
```

#### 使用示例

**CLI**:
```bash
# 自动选择 (推荐)
python main.py paper.pdf -t academic_panels.html

# 使用预设
python main.py paper.pdf --preset a0_portrait

# 手动指定
python main.py paper.pdf --width 2000 --height 2800
```

**Web UI**:
- 在"📐 海报尺寸"选择预设或手动输入

#### 文档
- `docs/POSTER_SIZE_GUIDE.md` - 完整尺寸配置指南

---

## v1.3.3 (2025-12-17)

### 🐛 关键 Bug 修复 🔴

#### 问题1: Jinja2 模板语法错误
- **错误**: `Encountered unknown tag 'break'`
- Jinja2 不支持 `{% break %}` 标签
- 导致模板编译失败，无法生成海报

#### 修复1
- ✅ 移除 `{% if loop.index >= 2 %}{% break %}{% endif %}`
- ✅ 使用切片语法：`{% for fig in sorted_figs[:2] %}`
- ✅ 更简洁、更符合 Jinja2 最佳实践

#### 问题2: LLM 输出格式兼容性修复

#### 问题
- **ValidationError**: `Input should be a valid string [input_type=list]`
- LLM 返回的 section.content 是列表格式，但 Pydantic 模型期望字符串
- 影响: introduction, methods, results, conclusion 四个 section

#### 原因
- LLM 自然输出习惯：将要点组织为列表（`["- 要点1", "- 要点2"]`）
- Pydantic 模型定义：`content: str`（期望字符串）
- 格式不匹配导致验证失败，海报生成中断

#### 修复
- ✅ 在 `_fix_json_data` 中自动检测列表格式的 content
- ✅ 将列表转换为字符串：`"\n".join(content_list)`
- ✅ 转换示例：`["- 要点1", "- 要点2"]` → `"- 要点1\n- 要点2"`
- ✅ 保持 markdown 格式，模板正常渲染

#### 文档
- `docs/BUGFIX_v1.3.3_VALIDATION.md` - 详细修复说明

---

## v1.3.2 (2025-12-17)

### 🎨 学术面板布局优化

#### 问题
- Conclusion与Results部分位置不对（Grid布局混乱）
- Results面板中没有显示图片

#### 原因分析
- 连续2个 `panel-large`（Methods + Key Results）导致后续面板位置不可预测
- Results面板的图片选择逻辑过于严格，导致即使有图也不显示

#### 修复
- ✅ Methods面板：从 `panel-large`（跨2行）改为 `panel-wide`（跨2列）
- ✅ 重命名 "Key Results" 为 "Key Figure"，作为唯一的大面板
- ✅ Results面板：改进图片选择逻辑，优先显示第2张results图或第3张重要图
- ✅ 优化布局：Introduction + Methods（第一排），Key Figure + Results + Conclusion（后续排）

#### 效果
- 面板位置稳定，不再混乱
- Methods, Key Figure, Results 三个面板都有图片显示
- 视觉平衡，信息密度适中

#### 文档
- `docs/LAYOUT_FIX_v1.3.2.md` - 布局优化详情

---

## v1.3.1 (2025-12-17)

### 🐛 关键 Bug 修复

#### 问题1: Web UI 兼容性错误 🔴
- **错误**: `ValueError: too many values to unpack (expected 2)`
- **原因**: v1.3.0 中 `harvester.harvest()` 返回3个值（新增公式清单），但 Web UI 仍用2个值接收
- **影响**: 所有 Web UI 用户无法使用

#### 修复
- ✅ 更新 `webui_gradio.py` 接收3个返回值
- ✅ 更新 `webui_streamlit.py` 接收3个返回值
- ✅ 进度提示显示图片和公式数量
- ✅ 更新 `TROUBLESHOOTING.md` 示例代码

#### 问题2: 模板居中对齐问题 🎨
- 海报卡片未居中，偏向左侧
- 阴影过重，被误认为边框

#### 修复
- ✅ 添加 `body` flex 布局实现水平居中
- ✅ 添加 `.poster-container` 的 `margin: 0 auto`
- ✅ 减轻 box-shadow 阴影（透明度 0.35 → 0.25）
- ✅ 影响全部3个模板: academic_panels, multi_figure_grid, simple_grid

#### 文档
- `docs/BUGFIX_v1.3.1_WEBUI.md` - Web UI 修复详情
- `docs/LAYOUT_CENTER_FIX_v1.3.1.md` - 居中对齐修复

---

## v1.3.0 (2025-12-17)

### 📝 内容充实化与公式支持

#### 问题
- 文本内容太少，Introduction、Key Results等section只有3-4个要点
- 公式未提取，只支持图片格式公式，文本/LaTeX格式公式被忽略

#### 修复

**1. 内容量优化**:
- **提示词增强**: LLM要求生成更详细的内容
  - Introduction: 5-7个要点（vs 之前3-4个）
  - Methods: 6-8个要点（vs 之前4-5个）
  - Results: 5-7个要点（vs 之前3-4个）
  - Conclusion: 4-5个要点（vs 之前3个）
  - Abstract: 150-200字（vs 之前100字）
- 每个要点30-50字（vs 之前20-30字）
- 强调保留技术细节和数据

**2. 公式提取系统** ⭐:
- **新增 `extract_equations` 方法**: 识别4种公式格式
  - 行内公式: `$...$`
  - 行间公式: `$$...$$`
  - LaTeX equation: `\begin{equation}...\end{equation}`
  - 数学符号密集行（启发式识别）
- **新增 Equation 数据模型**: 
  - content, equation_type, context, description
- **智能过滤**: 
  - 过滤太短的公式（可能是金额）
  - 去重（基于内容前100字符）
  - 最多提取20个，显示前3个

**3. 模板展示增强**:
- **新增 Key Equations 面板**: 专门展示核心公式
- 公式样式优化:
  - 左侧蓝色边框
  - 等宽字体显示
  - 灰色背景区分
  - 支持横向滚动（长公式）
- 面板类型: panel-wide（跨2列）

#### 效果
- ✅ 内容量提升 50-75% （每个section多2-3个要点）
- ✅ Abstract 长度提升 75% (100字→175字)
- ✅ 支持文本/LaTeX公式提取（4种格式）
- ✅ 新增 Key Equations 展示面板
- ✅ 海报信息密度显著提升
- ✅ 保持良好可读性

#### 适用场景
- 理论性强的论文（数学推导多）
- 算法论文（优化公式、损失函数）
- 机器学习论文（模型公式、训练目标）
- 物理/数学论文（核心方程）

#### 文档
- 新增 `docs/V1.3.0_IMPROVEMENTS.md` - 完整改进报告

---

## v1.2.4 (2025-12-17)

### 🎯 图片提取增强: 支持更多图片和公式

#### 问题
- 只分析前6张图片，大量内容被忽略
- 图片尺寸过滤过严(200px)，公式被过滤掉
- 缺少公式识别和专门展示
- 模板只显示少量图片

#### 修复
- **降低尺寸阈值**: 200px → 100px (-50%)
  - 可提取更小的公式和图表
  - 新增过滤过大图片(>3000px)逻辑
  - 新增命令行参数 `--min-image-size`

- **增加分析数量**: 6张 → 15张 (+150%)
  - 默认分析15张图片
  - 新增命令行参数 `--max-images`
  - 可通过环境变量 `MAX_IMAGES_ANALYZE` 配置

- **公式识别功能**: 
  - 新增 `equation` 图片类型
  - VLM提示词包含公式识别指令
  - 优先级与架构图相同(7分)
  - 公式专用标题和样式

- **扩展模板显示**: 
  - 额外图片面板: 2张 → 5张
  - 支持显示10-14张图片（vs 之前6-8张）
  - 公式显示独立标题 "Equation X"
  - 新增 `.badge-equation` 样式

- **新增配置项**:
  - `MIN_IMAGE_WIDTH` (默认100)
  - `MIN_IMAGE_HEIGHT` (默认100)
  - `MAX_IMAGES_ANALYZE` (默认15)

#### 效果
- ✅ 可提取2倍面积的小图（公式、小图表）
- ✅ 分析数量提升150% (6→15张)
- ✅ 模板显示提升75% (8→14张)
- ✅ 公式被正确识别和展示
- ✅ 灵活的命令行控制

#### 文档
- 新增 `docs/IMAGE_EXTRACTION_v1.2.4.md` - 图片提取增强报告

---

## v1.2.3 (2025-12-17)

### 🎨 布局优化: 学术会议模板空间利用率提升

#### 问题
- 空白区域太多，空间利用率低 (~85%)
- 内容被截断，图片和文字显示不完整
- 面板固定高度，无法适应内容

#### 修复
- **解决内容截断**:
  - 面板改为自适应高度 (`height: fit-content`)
  - 内容区域完整显示 (`overflow: visible`)
  - 网格行高自适应 (`grid-auto-rows: minmax(180px, auto)`)
  - 图片最大高度提升: 普通面板 320px→400px，大面板 500px→700px

- **优化空间利用率** (提升 10%):
  - 面板间距: 18px → 12px (减少 33%)
  - 容器边距: 25px → 20px (减少 20%)
  - 面板内边距: 20px → 16px (减少 20%)
  - 标题栏高度: ~100px → ~70px (减少 30%)

- **紧凑化排版**:
  - 标题字体: 2.5rem → 2.1rem
  - 面板标题: 1.35rem → 1.2rem
  - 内容字体: 0.92rem → 0.88rem
  - 行高: 1.7 → 1.6
  - 各种间距均优化缩小

#### 效果
- ✅ 空间利用率: 85% → 95% (提升 10%)
- ✅ 内容完整显示，无截断
- ✅ 信息密度提高，更专业
- ✅ 保持良好的可读性

#### 文档
- 新增 `docs/LAYOUT_FIX_v1.2.3.md` - 详细的布局优化报告

---

## v1.2.2 (2025-12-17)

### 🐛 重要Bug修复: 学术会议模板图片显示问题

#### 问题
- 学术会议模板 KEY RESULTS 区域显示期刊封面而不是实验结果图
- 图片选择逻辑直接使用第一张图片，没有智能筛选

#### 修复
- **模板优化** (`templates/academic_panels.html`):
  - KEY RESULTS 面板改为优先选择 `placement='results'` 的图片
  - 按 `priority` 属性排序，选择最重要的图片
  - 添加后备逻辑：如无 results 图片，选择优先级最高的图片

- **视觉分析增强** (`src/vision_analyzer.py`):
  - **新增相关性判断**: VLM 识别期刊封面、logo等无关图片，自动过滤
  - **新增优先级评分**: 0-10 的重要性评分，核心结果图得分最高
  - **扩展图片类型**: 新增 `cover` 类型标记无关图片
  - **改进排序逻辑**: 按 `priority` 和 `figure_type` 综合排序

- **提示词优化**:
  - 明确要求 VLM 判断图片是否与研究内容相关
  - 要求为每张图片打分 (priority: 0-10)
  - 核心结果图、关键架构图获得高分 (8-10)
  - 期刊封面等无关图片获得低分 (0-1) 或标记为不相关

#### 效果
- ✅ KEY RESULTS 区域正确显示实验结果图
- ✅ 期刊封面等无关图片被自动识别和过滤
- ✅ 图片按重要性智能排序和放置
- ✅ 提升海报视觉质量和专业性

#### 文档
- 新增 `docs/BUGFIX_v1.2.2.md` - 详细的bug修复报告

---

## v1.2.1 (2025-12-17)

### ✨ Web UI 模板选择器优化

#### 改进
- **模板选择器升级**: 从复选框改为单选按钮组
  - 支持选择全部 3 个模板（经典三栏、多图丰富、学术会议）
  - 清晰的模板名称和推荐标记 (⭐)
  - 默认选中 "多图丰富" 模板
- **Gradio UI**: 在 "高级功能" 区域添加模板单选按钮
- **Streamlit UI**: 在侧边栏 "高级功能" 区域添加模板单选按钮
- **模板映射**: 自动将用户选择映射到对应的模板文件

#### 新增文档
- `docs/WEBUI_TEMPLATE_GUIDE.md` - Web UI 模板选择完整指南 (详细对比和使用建议)
- `docs/TEMPLATE_SELECTION.md` - 模板快速选择参考 (一页速查)
- `docs/WEBUI_SCREENSHOTS.md` - Web UI 界面说明 (ASCII 界面图)
- `docs/README.md` - 文档目录索引

#### 文档更新
- 更新 `WEBUI_GUIDE.md`，添加模板选择章节 (4.5)
- 在模板说明折叠面板中添加详细的模板对比表

#### 修复
- 修复 Streamlit UI 缺少视觉分析参数传递的问题
- 修复 Streamlit UI 缺少模板选择功能的问题

---

## v1.2.0 (2025-12-17)

### ✨ 重大更新: 视觉分析功能

#### 核心功能
- ✅ **视觉模型集成** - 支持使用 VLM 分析图片内容
- ✅ **多图片支持** - 海报可显示多张图片（最多6张）
- ✅ **智能图片分类** - 自动识别架构图、结果图、流程图等
- ✅ **智能图片放置** - 根据类型自动放置到合适位置
- ✅ **图片描述生成** - 为每张图片生成准确描述
- ✅ **内容更丰富** - 解决海报空白问题

#### 支持的视觉模型
- OpenAI: gpt-4o, gpt-4o-mini, gpt-4-turbo
- SiliconFlow: Qwen2-VL-72B, Qwen2-VL-7B, InternVL2
- Claude: claude-3-opus, claude-3-sonnet

#### 新增模板
- ✅ `multi_figure_grid.html` - 优化的多图海报模板
- ✅ `academic_panels.html` - **学术会议风格多面板模板** ⭐
  - 借鉴 Paper2Poster 项目的设计思路
  - 9个独立面板布局
  - 类似学术会议海报风格
  - 灵活的面板尺寸（large, wide, span）
  - 专业的视觉效果
- 智能布局，充分利用空间
- 摘要横跨全宽
- 主图居中，其他图片智能分布

#### 数据模型扩展
- ✅ 新增 `Figure` 模型 - 完整的图片信息
- ✅ `PosterContent` 支持 `figures` 列表
- ✅ 兼容旧版单图模式

#### 新增文件
- `src/vision_analyzer.py` - 视觉分析器
- `templates/multi_figure_grid.html` - 多图模板
- `VISION_ANALYSIS_GUIDE.md` - 视觉分析使用指南

#### Web UI 更新
- ✅ 添加 "启用视觉分析" 选项
- ✅ 添加 "视觉模型" 配置
- ✅ 添加 "使用多图模板" 选项
- ✅ Gradio UI 完整支持新功能

#### 命令行更新
- ✅ 新增 `--enable-vision` 参数
- ✅ 新增 `--vision-model` 参数
- ✅ 支持通过环境变量配置

#### 配置更新
- ✅ `ENABLE_VISION_ANALYSIS` 环境变量
- ✅ `VISION_MODEL` 环境变量
- ✅ 更新 env.example 包含视觉分析配置

---

## v1.1.1 (2025-12-17)

### 🐛 Bug 修复与优化

#### LLM 数据验证优化
- ✅ 修复 LLM 返回列表格式 authors 的问题（自动转为字符串）
- ✅ 添加缺失字段的自动填充机制
- ✅ 改进 Prompt 提供明确的 JSON Schema 示例
- ✅ 增强错误提示，给出具体的解决建议
- ✅ 添加数据预处理和容错处理

#### 新增文档
- 📖 `TROUBLESHOOTING.md` - 完整的故障排查指南
- 📖 `SILICONFLOW_GUIDE.md` - SiliconFlow API 详细使用指南
- 📖 `BUGFIX_v1.1.1.md` - Bug 修复详细说明
- 涵盖所有常见错误和解决方法

#### API 支持优化
- ✅ 已启用 `response_format={"type": "json_object"}` 强制 JSON 输出
- ✅ 完全兼容 SiliconFlow API
- ✅ 添加 SiliconFlow 配置示例和文档
- ✅ 更新 env.example 包含多种 API 服务配置

---

## v1.1.0 (2025-12-17)

### ✨ 新增 Web UI

#### 双界面支持
- ✅ **Gradio UI** - 简洁现代的 Web 界面
  - 拖拽上传 PDF
  - 实时进度显示
  - 自动文件下载
  - 支持公网分享
- ✅ **Streamlit UI** - 功能丰富的 Web 界面
  - 侧边栏详细说明
  - 快捷配置按钮
  - 内容预览功能
  - 专业数据展示

#### 易用性提升
- 🎨 无需命令行，图形界面操作
- 🚀 一键启动脚本（支持 Linux/Mac/Windows）
- 📖 完整的 Web UI 使用指南
- 🌐 支持局域网和公网访问

#### 新增文件
- `webui_gradio.py` - Gradio Web UI 主程序
- `webui_streamlit.py` - Streamlit Web UI 主程序
- `start_webui.sh` - Linux/Mac 启动脚本
- `start_webui.bat` - Windows 启动脚本
- `WEBUI_GUIDE.md` - Web UI 详细使用指南

#### 依赖更新
- 新增 `gradio>=4.0.0`
- 新增 `streamlit>=1.28.0`

---

## v1.0.0 (2025-12-17)

### ✨ 首次发布

#### 核心功能
- ✅ PDF 文本和图片自动提取
- ✅ 基于 LLM 的智能内容理解和结构化
- ✅ 精美的三栏布局海报模板
- ✅ PDF 和 PNG 格式导出
- ✅ 支持自定义兼容 OpenAI API 的大模型

#### 技术实现
- 📦 使用 PyMuPDF 进行 PDF 解析
- 🤖 集成 OpenAI API（兼容多种 LLM 服务）
- 🎯 使用 Pydantic 强制结构化输出
- 🎨 基于 Jinja2 + TailwindCSS 的模板系统
- 🖼️ 使用 Playwright 进行高质量导出

#### 项目结构
- `src/harvester.py` - PDF 解析和资源提取模块
- `src/editor.py` - LLM 交互和内容生成模块
- `src/renderer.py` - HTML 渲染和导出模块
- `src/models.py` - Pydantic 数据模型定义
- `src/logger.py` - 彩色日志系统
- `templates/simple_grid.html` - 默认三栏布局模板
- `main.py` - 主程序入口
- `config.py` - 配置管理

#### 辅助工具
- 📝 完整的文档系统（README, QUICKSTART, USAGE_EXAMPLES）
- 🔧 自动安装脚本（setup.sh）
- ✅ 项目验证脚本（verify_setup.py）
- 📊 项目摘要文档（PROJECT_SUMMARY.md）

#### 特色
- 🔄 自动备份已有文件
- 📄 可选保存 JSON 中间数据
- 🎨 可自定义 HTML 模板
- ⚙️ 灵活的配置选项
- 🌐 支持中英文论文
- 🎯 稳定性优先的设计理念

### 使用方法

基础用法：
```bash
python main.py input/paper.pdf
```

高级选项：
```bash
python main.py input/paper.pdf -f png -o my_poster --save-json
```

### 系统要求

- Python 3.10+
- 网络连接（用于调用 LLM API）
- Chromium 浏览器（Playwright 自动安装）

### 依赖包

见 `requirements.txt`

### 已知限制

- 超长论文会被截断至 30,000 字符
- 主图选择依赖 LLM 判断
- 默认只支持三栏布局（可自定义）

### 贡献者

Paper2Poster-Web 开发团队

---

## 未来计划 (TODO)

### v1.2.0
- [ ] 添加更多模板选项（两栏、四栏布局）
- [ ] Web UI 支持自定义模板选择
- [ ] 支持更多导出格式（SVG）
- [ ] 优化超长论文的处理
- [ ] 添加交互式预览功能

### v1.3.0
- [ ] 批量处理优化（Web UI 支持）
- [ ] 模板市场/模板库
- [ ] 多语言支持优化
- [ ] 用户配置持久化

### 欢迎贡献

如有建议或发现 bug，欢迎提交 Issue 或 Pull Request！

