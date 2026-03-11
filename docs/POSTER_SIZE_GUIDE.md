# 海报尺寸配置指南

## 问题背景

用户反馈："References和Conclusion被挤到最下面窗口外面去了。是不是海报尺寸应该跟模板有联动？"

**核心问题**:
- 固定的 1600×1200 像素尺寸对于内容丰富的学术论文不够用
- 不同模板（simple_grid, multi_figure_grid, academic_panels）需要不同的尺寸
- 缺少学术海报常用尺寸的预设选项

---

## 解决方案

### 1. 提高默认高度

**修改前**:
```python
POSTER_WIDTH = 1600
POSTER_HEIGHT = 1200  # 太小，内容容易溢出
```

**修改后**:
```python
POSTER_WIDTH = 1600
POSTER_HEIGHT = 1800  # +50%，适应更多内容
```

### 2. 添加学术海报尺寸预设

```python
POSTER_PRESETS = {
    "default": (1600, 1800, "默认尺寸 (适合大多数场景)"),
    "a0_portrait": (3370, 4768, "A0 纵向 (841×1189mm, 标准学术海报)"),
    "a0_landscape": (4768, 3370, "A0 横向 (1189×841mm)"),
    "a1_portrait": (2384, 3370, "A1 纵向 (594×841mm)"),
    "a1_landscape": (3370, 2384, "A1 横向 (841×594mm)"),
    "36x48": (3600, 4800, "36\"×48\" 纵向 (914×1219mm, 北美常用)"),
    "48x36": (4800, 3600, "48\"×36\" 横向 (1219×914mm)"),
    "screen_4k": (3840, 2160, "4K 屏幕 (16:9, 适合展示)"),
    "screen_hd": (1920, 1080, "1080p 屏幕 (16:9, 轻量级)"),
    "compact": (1400, 1600, "紧凑型 (适合简短论文)"),
    "extended": (1600, 2400, "加长型 (适合内容丰富的论文)"),
}
```

### 3. 模板推荐尺寸联动

```python
TEMPLATE_RECOMMENDED_SIZES = {
    "academic_panels.html": "extended",      # 多面板，需要更大高度
    "multi_figure_grid.html": "default",     # 多图展示，默认即可
    "simple_grid.html": "compact",           # 简单布局，紧凑型
}
```

---

## 使用方法

### CLI 命令行

#### 1. 使用预设尺寸
```bash
# 学术会议海报 (A0 纵向)
python main.py paper.pdf -t academic_panels.html --preset a0_portrait

# 加长型 (适合内容丰富的论文)
python main.py paper.pdf -t academic_panels.html --preset extended

# 屏幕展示 (4K)
python main.py paper.pdf -t simple_grid.html --preset screen_4k
```

#### 2. 手动指定尺寸
```bash
python main.py paper.pdf --width 2000 --height 2800
```

#### 3. 自动选择 (默认)
```bash
# 不指定尺寸，自动根据模板推荐
python main.py paper.pdf -t academic_panels.html
# → 自动使用 "extended" (1600×2400)
```

### Web UI (Gradio)

1. **选择尺寸预设**:
   - 在"📐 海报尺寸"部分选择预设
   - 选项：`a0_portrait`, `36x48`, `extended`, etc.

2. **手动指定**:
   - 在"宽度"和"高度"输入框中输入数值
   - 会覆盖预设值

3. **自动选择** (推荐):
   - 选择"自动 (根据模板推荐)"
   - 系统根据模板自动选择最佳尺寸

---

## 尺寸推荐表

### 按使用场景

| 场景 | 推荐预设 | 尺寸 (宽×高 px) | 说明 |
|------|---------|-----------------|------|
| **学术会议现场** | `a0_portrait` | 3370×4768 | 国际标准，适合打印 |
| **学术会议现场 (北美)** | `36x48` | 3600×4800 | 北美常用尺寸 |
| **在线展示 (4K)** | `screen_4k` | 3840×2160 | 高清屏幕展示 |
| **在线展示 (1080p)** | `screen_hd` | 1920×1080 | 轻量级，快速加载 |
| **内容丰富的论文** | `extended` | 1600×2400 | 多图表、多公式 |
| **简短论文** | `compact` | 1400×1600 | 紧凑布局 |
| **一般用途** | `default` | 1600×1800 | 平衡之选 |

### 按模板推荐

| 模板 | 自动选择 | 原因 |
|------|---------|------|
| `academic_panels.html` | `extended` (1600×2400) | 多面板布局，内容密集 |
| `multi_figure_grid.html` | `default` (1600×1800) | 多图展示，默认适中 |
| `simple_grid.html` | `compact` (1400×1600) | 三栏简单布局，紧凑 |

### 按论文特点

| 论文特点 | 推荐尺寸 | 预设 |
|---------|---------|------|
| 图片多 (>10张) | 1600×2400 | `extended` |
| 公式多 (>10个) | 1600×2400 | `extended` |
| 文字量大 | 1600×2400 | `extended` |
| 简短会议摘要 | 1400×1600 | `compact` |
| 标准长度论文 | 1600×1800 | `default` |

---

## 尺寸选择优先级

系统按以下优先级确定最终尺寸：

```
1. 手动指定 (--width, --height)
   ↓ 如果未指定
2. 预设尺寸 (--preset)
   ↓ 如果未指定
3. 模板推荐 (TEMPLATE_RECOMMENDED_SIZES)
   ↓ 如果模板无推荐
4. 默认尺寸 (default 预设: 1600×1800)
```

---

## 打印尺寸对照

### 像素 → 物理尺寸 (300 DPI)

| 像素尺寸 | 物理尺寸 (cm) | 物理尺寸 (英寸) | 标准纸张 |
|---------|--------------|----------------|---------|
| 3370×4768 | 84.1×119.9 | 33.1×47.2 | A0 |
| 2384×3370 | 59.4×84.1 | 23.4×33.1 | A1 |
| 3600×4800 | 91.4×121.9 | 36×48 | 36"×48" |
| 1600×1800 | 40.6×45.7 | 16×18 | 自定义 |

**注意**: 
- 打印需要至少 **300 DPI** 分辨率
- 屏幕展示通常 **72-96 DPI** 即可

---

## 常见问题

### Q1: 内容溢出怎么办？

**方案1**: 使用更大的预设
```bash
python main.py paper.pdf --preset extended
```

**方案2**: 手动增加高度
```bash
python main.py paper.pdf --height 2400
```

**方案3**: 启用溢出检测 (需要vision模型)
```bash
python main.py paper.pdf --check-overflow --enable-vision
```

### Q2: 如何选择最合适的尺寸？

1. **先用默认尺寸生成一次**
2. **检查是否有内容被裁剪**
   - 如果 References/Conclusion 看不见 → 增加高度
   - 如果空白太多 → 减小高度
3. **根据用途调整**
   - 打印 → 使用 A0/A1 标准尺寸
   - 屏幕 → 使用 screen_4k/screen_hd
   - 一般 → 使用 default/extended

### Q3: 尺寸越大越好吗？

**不是**。尺寸过大会导致：
- 文件体积大，加载慢
- 渲染时间长
- 不必要的空白区域

**建议**: 根据实际内容量选择合适尺寸。

### Q4: 如何为所有模板设置默认尺寸？

修改 `config.py`:
```python
POSTER_WIDTH = 2000  # 增加宽度
POSTER_HEIGHT = 2400  # 增加高度
```

---

## 修改文件

- `config.py` - 添加 `POSTER_PRESETS`, `TEMPLATE_RECOMMENDED_SIZES`
- `main.py` - 添加 `--preset`, `--width`, `--height` 参数和自动选择逻辑
- `webui_gradio.py` - 添加预设选择下拉框和尺寸确定逻辑

---

## 版本信息

- **版本**: v1.3.4
- **日期**: 2025-12-17
- **类型**: 功能增强 (Feature)
- **影响范围**: 全部模板

---

*文档生成时间: 2025-12-17*

