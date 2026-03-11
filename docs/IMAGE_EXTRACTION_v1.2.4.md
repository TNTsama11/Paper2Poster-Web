# 图片提取增强报告 v1.2.4

## 🐛 问题描述

**用户反馈**:
> "论文那么多图，为什么只处理了几个图，而且关键的公式怎么处理的。这些都是可以摆到海报上的内容。"

**核心问题**:
1. **图片数量限制过严**: 只分析前6张图片
2. **图片尺寸过滤过严**: min_size=200px，公式图片被过滤掉
3. **缺少公式识别**: 没有专门识别和处理数学公式
4. **显示数量不足**: 模板只显示少量图片

---

## 📊 问题分析

### 问题 1: 图片提取被过滤

**原因**:
```python
# harvester.py
min_width = 200, min_height = 200  # 公式通常小于200px
if width < min_width or height < min_height:
    continue  # 被过滤掉
```

**影响**: 大量公式、小图表被忽略

### 问题 2: 分析数量限制

**原因**:
```python
# editor.py
max_images = 6  # 只分析前6张

# vision_analyzer.py
filenames_to_analyze = image_filenames[:max_images]
```

**影响**: 论文有15张图，只分析6张，丢失大量内容

### 问题 3: 缺少公式识别

**原因**:
- 视觉分析提示词没有包含"公式"类型
- 图片分类没有"equation"类别
- 模板没有针对公式的特殊展示

**影响**: 公式不被重视，可能被忽略或错误分类

### 问题 4: 模板显示限制

**原因**:
```html
<!-- academic_panels.html -->
{% for fig in extra_figures[:2] %}  <!-- 只显示2张额外图片 -->
```

**影响**: 即使提取了很多图，也只显示少量

---

## ✅ 修复方案

### 1. 降低图片尺寸阈值

**文件**: `src/harvester.py`, `config.py`

**修改**:
```python
# 修复前
min_width = 200, min_height = 200

# 修复后
min_width = 100, min_height = 100  # 降低50%，包含公式
```

**新增过滤**:
```python
# 过滤过大的图片（可能是全页扫描）
if width > 3000 or height > 3000:
    logger.debug(f"跳过过大图片 ({width}x{height})")
    continue
```

**效果**: 
- ✅ 100x100px 以上的公式图片可以提取
- ✅ 小型图表不会被过滤
- ✅ 过大图片（全页扫描）被过滤

---

### 2. 增加分析数量上限

**文件**: `src/editor.py`, `src/vision_analyzer.py`, `config.py`

**修改**:
```python
# 修复前
max_images = 6

# 修复后
max_images = 15  # 增加到15张
MAX_IMAGES_ANALYZE = int(os.getenv("MAX_IMAGES_ANALYZE", "15"))
```

**命令行参数**:
```python
# main.py
parser.add_argument(
    "--max-images",
    type=int,
    default=15,
    help="最多分析的图片数量（默认15张，包含图表和公式）"
)
```

**效果**:
- ✅ 最多分析15张图片（vs 之前6张）
- ✅ 可通过命令行调整
- ✅ 可通过环境变量配置

---

### 3. 添加公式识别功能

**文件**: `src/vision_analyzer.py`

**扩展图片类型**:
```python
# 新增
"equation": "数学公式、方程式 ⭐"

# 完整列表
figure_type = {
    "equation": "数学公式、方程式 ⭐",        # 新增
    "architecture": "系统架构图、模型结构图",
    "flowchart": "流程图、算法流程",
    "result": "实验结果图、对比图、性能图",
    "table": "表格",
    "chart": "图表、柱状图、折线图",
    "cover": "期刊封面、logo（无关内容）",
    "general": "其他类型图片"
}
```

**优先级调整**:
```python
type_priority = {
    "result": 8,
    "equation": 7,      # 公式也很重要 ✅
    "architecture": 7,
    "flowchart": 6,
    "chart": 5,
    "table": 4,
    "general": 3,
    "cover": 0
}
```

**提示词增强**:
```python
"""
**特别提示**: 如果是数学公式/方程式，请设置 figure_type="equation"，
并根据其重要性评分（核心公式 8-10分）
"""
```

**简单分析fallback**:
```python
# 基于文件名推测
if 'eq' in filename_lower or 'formula' in filename_lower:
    figure_type = "equation"
    placement = "methods"
    priority = 7
```

---

### 4. 扩展模板显示能力

**文件**: `templates/academic_panels.html`

**增加额外面板**:
```html
<!-- 修复前 -->
{% for fig in extra_figures[:2] %}  <!-- 只显示2张 -->

<!-- 修复后 -->
{% set extra_figures = figures_by_placement['results'][1:] + 
                       figures_by_placement['methods'][2:] + 
                       figures_by_placement['any'] %}
{% for fig in extra_figures[:5] %}  <!-- 显示5张 -->
```

**公式特殊标题**:
```html
<div class="panel-title">
    {% if fig.figure_type == 'equation' %}
        Equation {{ loop.index }}  ✅ 公式专用
    {% else %}
        Figure {{ loop.index + 5 }}
    {% endif %}
</div>
```

**新增样式**:
```css
.badge-equation {
    background: #e7f3ff;
    color: #0056b3;
    font-weight: 700;
}
```

---

### 5. 新增命令行参数

**文件**: `main.py`

**新参数**:
```bash
--max-images 20              # 最多分析20张图片
--min-image-size 80          # 最小尺寸降到80px，提取更多公式
```

**完整示例**:
```bash
python main.py paper.pdf \
    -t academic_panels.html \
    --enable-vision \
    --max-images 20 \
    --min-image-size 80 \
    --width 1200 --height 2000
```

---

## 📐 修复对比

### 提取数量对比

| 指标 | 修复前 | 修复后 | 改善 |
|------|--------|--------|------|
| **最小尺寸** | 200x200px | 100x100px | 可提取2倍面积的小图 |
| **分析数量** | 6张 | 15张 (可配置) | +150% |
| **模板显示** | 6-8张 | 10-14张 | +75% |
| **公式识别** | ❌ 无 | ✅ 有专门分类 | +100% |

### 典型论文示例

**场景**: 一篇包含 20张图片的论文（3个公式，5个结果图，4个架构图，8个其他）

| 阶段 | 修复前 | 修复后 |
|------|--------|--------|
| **PDF提取** | 15张 (3个公式被过滤) | 20张 (全部提取) |
| **视觉分析** | 前6张 | 前15张 |
| **公式识别** | 0个 (无此类型) | 3个 (正确识别) |
| **海报显示** | 6张 | 12张 |

---

## 🎯 使用示例

### 基本使用（默认配置）

```bash
# 自动分析15张图片，包含公式
python main.py paper.pdf \
    -t academic_panels.html \
    --enable-vision
```

### 图片很多的论文

```bash
# 分析20张图片，降低尺寸阈值
python main.py paper.pdf \
    -t academic_panels.html \
    --enable-vision \
    --max-images 20 \
    --min-image-size 80
```

### 公式较多的数学论文

```bash
# 分析25张，尺寸降到50px（包含行内公式）
python main.py paper.pdf \
    -t academic_panels.html \
    --enable-vision \
    --max-images 25 \
    --min-image-size 50 \
    --height 2000  # 增加高度以容纳更多内容
```

### 快速预览（少量图片）

```bash
# 只分析前5张，快速生成
python main.py paper.pdf \
    -t simple_grid.html \
    --max-images 5
```

---

## 💡 最佳实践

### 1. 选择合适的参数

**根据论文类型**:
- **理论论文** (公式多): `--min-image-size 50 --max-images 25`
- **实验论文** (图表多): `--min-image-size 100 --max-images 20`
- **综述论文** (图少): `--min-image-size 150 --max-images 10`

### 2. 平衡质量和成本

**VLM API调用成本**:
```
分析 6 张图片  ≈ $0.01 - $0.03
分析 15 张图片 ≈ $0.025 - $0.075
分析 25 张图片 ≈ $0.04 - $0.125
```

**建议**:
1. 首次生成用少量图片测试 (`--max-images 5`)
2. 满意后再用完整配置 (`--max-images 15-20`)

### 3. 检查提取效果

```bash
# 查看提取的图片
ls -lh output/images/

# 查看日志
tail -50 output/poster.log | grep -E "提取图片|跳过"

# 关键日志：
# ✅ "提取图片: img_01.png (450x180)"
# ⚠️ "跳过小图片 (80x60)"
```

### 4. 优化海报高度

更多图片需要更大的海报：

```bash
# 6-10张图片
--width 1200 --height 1600

# 11-15张图片
--width 1200 --height 1800  ⭐ 推荐

# 16-25张图片
--width 1200 --height 2000
```

---

## 📋 环境变量配置

在 `.env` 文件中配置默认值：

```bash
# 图片提取配置
MIN_IMAGE_WIDTH=100          # 最小宽度 (默认100)
MIN_IMAGE_HEIGHT=100         # 最小高度 (默认100)
MAX_IMAGES_ANALYZE=15        # 最多分析数量 (默认15)

# 示例：数学论文配置
# MIN_IMAGE_WIDTH=50
# MIN_IMAGE_HEIGHT=50
# MAX_IMAGES_ANALYZE=25
```

---

## 🎨 视觉效果

### 公式显示示例

```html
┌────────────────────────────┐
│  Equation 1         [公式] │
│  ┌──────────────────────┐ │
│  │  E = mc²             │ │
│  │  (核心能量方程)       │ │
│  └──────────────────────┘ │
└────────────────────────────┘
```

### 多图布局

```
修复前 (6张图):
┌─────┬─────┬─────┐
│ Fig1│ Fig2│ Fig3│
├─────┼─────┼─────┤
│ Fig4│ Fig5│ Fig6│
└─────┴─────┴─────┘

修复后 (12张图):
┌─────┬─────┬─────┐
│ Fig1│ Fig2│ Eq 1│ ← 包含公式
├─────┼─────┼─────┤
│ Fig3│ Fig4│ Fig5│
├─────┼─────┼─────┤
│ Fig6│ Eq 2│ Fig7│
├─────┼─────┼─────┤
│ Fig8│ Fig9│Fig10│
└─────┴─────┴─────┘
```

---

## ⚠️ 注意事项

### 1. 图片过多的问题

**风险**: 分析25张图片耗时较长

**解决**:
- 使用更快的视觉模型（Qwen-VL比GPT-4V快）
- 分批处理：先生成预览版，再生成完整版

### 2. 公式可读性

**问题**: 小尺寸公式可能不清晰

**建议**:
- 公式图片保持原始分辨率
- 使用高分辨率海报（1400x2000或更大）
- 考虑使用 LaTeX 重新排版公式

### 3. 模板容量限制

**问题**: 太多图片会导致海报过长

**建议**:
- academic_panels 模板: 10-14张图片最佳
- 超过15张考虑分成两张海报
- 或使用多页PDF格式

---

## 📞 故障排查

### 问题 1: 公式仍未提取

**检查**:
```bash
# 查看提取的图片尺寸
ls -lh output/images/

# 如果没有小图片，尝试更低阈值
python main.py paper.pdf --min-image-size 50
```

### 问题 2: VLM未识别公式

**检查日志**:
```bash
tail -100 output/poster.log | grep -i "equation\|formula"
```

**可能原因**:
- VLM模型不支持数学公式识别
- 尝试更强大的模型：GPT-4o, Qwen2-VL-72B

### 问题 3: 图片太多无法全部显示

**解决**:
```bash
# 方案1: 增加海报高度
--height 2000 或 2400

# 方案2: 只分析重要图片
--max-images 10

# 方案3: 使用多页模板（未来功能）
```

---

## 🎉 总结

**核心改进**:
- ✅ 图片尺寸阈值: 200px → 100px (-50%)
- ✅ 分析数量: 6张 → 15张 (+150%)
- ✅ 模板显示: 6-8张 → 10-14张 (+75%)
- ✅ 新增公式识别和专门展示
- ✅ 新增命令行参数灵活控制

**建议使用**:
```bash
python main.py paper.pdf \
    -t academic_panels.html \
    --enable-vision \
    --max-images 15 \
    --min-image-size 100 \
    --width 1200 --height 1800
```

---

**修复版本**: v1.2.4  
**修复日期**: 2025-12-17  
**状态**: ✅ 已修复并增强

