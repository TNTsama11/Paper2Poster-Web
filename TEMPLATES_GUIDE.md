# 海报模板使用指南

Paper2Poster-Web 提供多种专业的海报模板，适用于不同场景。

## 📋 模板列表

### 1. simple_grid.html (默认)

**特点:**
- ✅ 经典三栏布局
- ✅ 简洁清晰
- ✅ 单张主图
- ✅ 适合图片较少的论文

**布局:**
```
┌─────────────────────────────┐
│      Title / Authors         │
├────────┬──────────┬──────────┤
│ Intro  │   Main   │ Results  │
│        │  Figure  │          │
│ Methods│          │ Conclusion│
│        │          │  Refs    │
└────────┴──────────┴──────────┘
```

**使用:**
```bash
python main.py input/paper.pdf
# 或
python main.py input/paper.pdf -t simple_grid.html
```

---

### 2. multi_figure_grid.html (推荐)

**特点:**
- ✅ 多图展示（最多6张）
- ✅ 智能图片放置
- ✅ 内容丰富饱满
- ✅ **需要视觉分析功能**

**布局:**
```
┌───────────────────────────────┐
│      Title / Authors           │
├───────────────────────────────┤
│    Abstract (横跨全宽)         │
├────────┬──────────┬───────────┤
│ Intro  │ Figure1  │  Results  │
│ Fig2   │ (主图大)  │   Fig4    │
│ Methods│ Figure3  │ Conclusion│
│        │          │   Refs    │
└────────┴──────────┴───────────┘
```

**使用:**
```bash
python main.py input/paper.pdf \
    --enable-vision \
    -t multi_figure_grid.html
```

---

### 3. academic_panels.html ⭐ (最新)

**特点:**
- ✅ **学术会议海报风格**
- ✅ 9个独立面板
- ✅ 灵活的面板尺寸
- ✅ 专业视觉效果
- ✅ 借鉴 Paper2Poster 项目设计

**布局:**
```
┌─────────────────────────────────┐
│       Title / Authors            │
├─────────────────────────────────┤
│     Abstract (横跨3列)           │
├──────┬───────────┬──────────────┤
│ Intro│  Methods  │  Key Results │
│      │  (大面板)  │   (大面板)    │
│      │           │              │
├──────┴───────────┴──────────────┤
│  Results (宽面板)  │  Conclusion │
├──────────────────┼──────────────┤
│  References       │  Extra Figs │
└──────────────────┴──────────────┘
```

**面板类型:**
- `panel-abstract` - 横跨全宽
- `panel-large` - 高度2倍（适合Methods和主图）
- `panel-wide` - 宽度2倍（适合Results）
- `panel` - 标准面板

**使用:**
```bash
python main.py input/paper.pdf \
    --enable-vision \
    -t academic_panels.html
```

---

## 🎨 模板对比

| 特性 | simple_grid | multi_figure_grid | academic_panels |
|------|-------------|-------------------|-----------------|
| 风格 | 经典简洁 | 多图丰富 | 学术会议 ⭐ |
| 图片数量 | 1张 | 最多6张 | 最多8张 |
| 布局方式 | 固定三栏 | 智能Grid | 灵活面板 |
| 空间利用 | 60% | 90% | 95% |
| 视觉效果 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 专业度 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 需要视觉分析 | ❌ | ✅ 推荐 | ✅ 推荐 |
| 适用场景 | 快速预览 | 日常使用 | 学术会议 |

---

## 🎯 选择建议

### 场景 1: 快速测试
```bash
python main.py input/paper.pdf
# 使用默认模板 simple_grid.html
```

### 场景 2: 日常使用（推荐）
```bash
python main.py input/paper.pdf \
    --enable-vision \
    -t multi_figure_grid.html
```

### 场景 3: 学术会议海报
```bash
python main.py input/paper.pdf \
    --enable-vision \
    --vision-model gpt-4o-mini \
    -t academic_panels.html \
    -f png
```

### 场景 4: 最高质量
```bash
python main.py input/paper.pdf \
    --enable-vision \
    --vision-model gpt-4o \
    -t academic_panels.html \
    -f pdf
```

---

## 🛠️ 自定义模板

### 基础结构

所有模板都遵循以下数据结构：

```python
poster = {
    "title": "海报标题",
    "authors": "作者列表",
    "affiliation": "机构",
    "abstract": "摘要",
    "introduction": {"title": "...", "content": "..."},
    "methods": {"title": "...", "content": "..."},
    "results": {"title": "...", "content": "..."},
    "conclusion": {"title": "...", "content": "..."},
    "figures": [
        {
            "path": "img_01.png",
            "caption": "图片说明",
            "type": "result",
            "placement": "results"
        }
    ],
    "references": ["参考文献1", "参考文献2"]
}
```

### 创建自定义模板

1. **复制现有模板:**
   ```bash
   cp templates/academic_panels.html templates/my_template.html
   ```

2. **修改 HTML 结构:**
   - 使用 Jinja2 语法访问 `{{ poster.* }}`
   - 使用 TailwindCSS 或自定义 CSS

3. **使用自定义模板:**
   ```bash
   python main.py input/paper.pdf -t my_template.html
   ```

### 模板开发提示

**访问数据:**
```html
{{ poster.title }}
{{ poster.authors }}
{{ poster.abstract }}
{{ poster.introduction.content | markdown | safe }}
```

**循环图片:**
```html
{% for fig in poster.figures %}
    <img src="images/{{ fig.path }}" alt="{{ fig.caption }}">
    <p>{{ fig.caption }}</p>
{% endfor %}
```

**条件判断:**
```html
{% if poster.figures %}
    <!-- 显示图片 -->
{% else %}
    <!-- 无图片时的占位 -->
{% endif %}
```

**Markdown 渲染:**
```html
{{ poster.methods.content | markdown | safe }}
```

---

## 🎨 样式定制

### 修改颜色主题

在模板的 `<style>` 部分修改：

```css
/* 主题色 */
:root {
    --primary-color: #667eea;     /* 主色调 */
    --secondary-color: #764ba2;   /* 次色调 */
    --accent-color: #ffc107;      /* 强调色 */
}

/* 标题背景渐变 */
.header-section {
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
}
```

### 修改字体

```css
@import url('https://fonts.googleapis.com/css2?family=Your+Font&display=swap');

body {
    font-family: 'Your Font', sans-serif;
}
```

### 调整海报尺寸

海报尺寸通过 Jinja2 变量控制：

```html
.poster-container {
    width: {{ width }}px;
    height: {{ height }}px;
}
```

在命令行或 Web UI 中设置：
- 默认: 1600x1200 (4:3)
- A1: 2384x3370
- A2: 1684x2384

---

## 📊 模板性能

| 模板 | 渲染时间 | 文件大小 | 复杂度 |
|------|---------|---------|--------|
| simple_grid | ~2秒 | ~500KB | 低 |
| multi_figure_grid | ~3秒 | ~800KB | 中 |
| academic_panels | ~4秒 | ~1MB | 高 |

---

## 🎓 高级技巧

### 技巧 1: 按图片类型筛选

```html
{% for fig in poster.figures %}
    {% if fig.type == 'result' %}
        <!-- 只显示结果图 -->
    {% endif %}
{% endfor %}
```

### 技巧 2: 限制图片数量

```html
{% for fig in poster.figures[:3] %}
    <!-- 只显示前3张图片 -->
{% endfor %}
```

### 技巧 3: 响应式布局

```css
@media (max-width: 1400px) {
    .panels-container {
        grid-template-columns: repeat(2, 1fr);
    }
}
```

### 技巧 4: 添加 Logo

```html
<div class="header-section">
    <img src="logo.png" class="logo">
    <div class="poster-title">{{ poster.title }}</div>
</div>
```

---

## 📖 相关文档

- **视觉分析**: [VISION_ANALYSIS_GUIDE.md](VISION_ANALYSIS_GUIDE.md)
- **Web UI**: [WEBUI_GUIDE.md](WEBUI_GUIDE.md)
- **使用示例**: [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)
- **故障排查**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 🆕 模板更新

### v1.2.0
- ✅ 新增 `academic_panels.html`
- ✅ 优化 `multi_figure_grid.html`
- ✅ 支持更多图片类型

### 计划中
- [ ] 两栏简约模板
- [ ] 四栏详细模板
- [ ] 深色主题模板
- [ ] 动态交互模板

---

**选择最适合你的模板，创建专业的学术海报！** 🎨

