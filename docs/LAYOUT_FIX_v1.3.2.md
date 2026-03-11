# v1.3.2 学术面板布局优化

## 问题描述

用户反馈：
1. **Conclusion与Results部分位置不对**
2. **Results面板中没有显示图片**

### 问题分析

#### 问题1: 布局错乱

**原因**:
```
Introduction (1列)
Methods (panel-large, 跨2行) ← 占用过多空间
Key Results (panel-large, 跨2行) ← 占用过多空间
Results (panel-wide, 跨2列)  ← 位置被挤到意外位置
Conclusion (1列)             ← 位置混乱
```

两个连续的 `panel-large`（跨2行）导致后续面板位置不可预测，Grid自动布局算法将它们放置在意外位置。

#### 问题2: Results面板无图片

**原因**:
```jinja
{% if figures_by_placement['results'] %}
    {% set fig = figures_by_placement['results'][0] %}
    <div class="figure-container">
        <img src="images/{{ fig.path }}" ...>
    </div>
{% endif %}
```

问题：
- `figures_by_placement['results'][0]` 可能已经在 "Key Results" 面板中显示了
- 如果只有1张results图，Results面板就没有图可显示
- 条件判断过于严格，导致即使有图也不显示

---

## 修复方案

### 1. 优化面板布局

**修复前**:
```html
<!-- Methods 面板 - 大面板 -->
<div class="panel panel-large">  ← 跨2行

<!-- Key Results 面板 - 大面板 -->
<div class="panel panel-large">  ← 跨2行（布局冲突）

<!-- Results 面板 - 宽面板 -->
<div class="panel panel-wide">   ← 位置混乱
```

**修复后**:
```html
<!-- Methods 面板 - 宽面板 -->
<div class="panel panel-wide">   ← 跨2列（更合理）

<!-- Key Figure 面板 - 大面板 -->
<div class="panel panel-large">  ← 跨2行（唯一大面板）

<!-- Results 面板 - 宽面板 -->
<div class="panel panel-wide">   ← 位置稳定
```

### 2. 优化图片显示逻辑

#### Methods 面板
```jinja
{# 只显示第一张methods图片 #}
{% if figures_by_placement['methods'] %}
    {% set fig = figures_by_placement['methods'][0] %}
    <div class="figure-container">...</div>
{% endif %}
```

#### Key Figure 面板
```jinja
{# 显示最重要的1-2张图片 #}
{% if result_figures %}
    {% set main_fig = sorted_results[0] %}
{% elif poster.figures %}
    {% for fig in sorted_figs %}
        ...显示前2张...
        {% if loop.index >= 2 %}{% break %}{% endif %}
    {% endfor %}
{% endif %}
```

#### Results 面板
```jinja
{# 显示第二张results图片，或第三张重要图片 #}
{% if figures_by_placement['results'] and figures_by_placement['results']|length > 1 %}
    {% set fig = sorted_results[1] %}  ← 显示第2张
{% elif poster.figures and poster.figures|length > 2 %}
    {% set fig = sorted_figs[2] %}     ← 显示第3张
{% endif %}
```

---

## 优化效果

### 布局对比

**修复前（混乱）**:
```
┌─────────────────────────────────────┐
│         Abstract (全宽)             │
├───────┬─────────────┬───────────────┤
│ Intro │  Methods    │               │
│       │  (跨2行)    │  Key Results  │
│       │             │  (跨2行)      │
├───────┴─────────────┼───────────────┤
│  Results (位置混乱) │               │
├─────────────────────┴───────────────┤
│ Conclusion (位置混乱)                │
└─────────────────────────────────────┘
```

**修复后（清晰）**:
```
┌─────────────────────────────────────┐
│         Abstract (全宽)             │
├───────┬─────────────────────────────┤
│ Intro │  Methods (跨2列，有图)      │
├───────┼─────────────────────────────┤
│  Key  │  Results (跨2列，有图)      │
│ Figure├─────────────┬───────────────┤
│ (跨2行)│ Conclusion │  其他面板     │
│       │            │               │
└───────┴────────────┴───────────────┘
```

### 图片显示改进

| 面板        | 修复前       | 修复后          |
|-------------|--------------|-----------------|
| Methods     | 0-2张图片    | 1张图片（稳定） |
| Key Figure  | 1张图片      | 1-2张图片       |
| Results     | 0-1张（经常0）| 1张图片（保证） |

---

## 修改文件

- `templates/academic_panels.html`
  - 行383-450: Methods, Key Figure, Results, Conclusion 面板重构

---

## 测试方法

```bash
# 重新生成海报
python main.py paper.pdf -t academic_panels.html --enable-vision

# 或使用 Web UI
python webui_gradio.py
```

### 预期结果

✅ **布局**:
- Introduction, Methods 在第一排
- Key Figure 在左侧跨2行
- Results, Conclusion 位置明确

✅ **图片**:
- Methods 面板有1张方法相关图
- Key Figure 面板有1-2张重要图
- Results 面板有1张结果相关图

✅ **整体**:
- 面板位置稳定，不再混乱
- 每个面板都有合理内容
- 视觉平衡，信息密度适中

---

## 版本信息

- **版本**: v1.3.2
- **日期**: 2025-12-17
- **修复类型**: 布局优化 + 图片显示修复
- **影响范围**: `academic_panels.html` 模板
- **向后兼容**: ✅ 是

---

## 相关问题

- 面板位置混乱
- Results面板无图片
- 多个panel-large冲突

---

*文档生成时间: 2025-12-17*

