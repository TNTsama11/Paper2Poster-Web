# v1.3.1 海报居中对齐修复

## 问题描述

用户反馈："生成的海报为什么有多余的边框？是不是浮动的海报卡片偏移了背景中央？"

### 问题原因

1. **未居中**: `body` 有 padding，但 `.poster-container` 没有居中对齐
2. **无对齐方式**: 容器只有固定宽高，缺少 `margin: auto` 或 flex 布局
3. **阴影过重**: `box-shadow` 阴影过大 (80px, 透明度 0.35)，可能被误认为边框

### 影响范围

所有三个模板都存在此问题：
- `academic_panels.html`
- `multi_figure_grid.html`
- `simple_grid.html`

---

## 修复方案

### 1. Body 添加 Flex 布局

```css
body {
    display: flex;
    justify-content: center;  /* 水平居中 */
    align-items: flex-start;  /* 顶部对齐 */
    min-height: 100vh;        /* 确保最小高度 */
}
```

### 2. 容器添加居中属性

```css
.poster-container {
    margin: 0 auto;  /* 确保居中 */
}
```

### 3. 减轻阴影效果

```css
.poster-container {
    box-shadow: 0 20px 60px rgba(0,0,0,0.25);  /* 减轻阴影 */
}
```

**修改前**:
- `box-shadow: 0 25px 80px rgba(0,0,0,0.35);` (academic_panels)
- `box-shadow: 0 20px 60px rgba(0,0,0,0.3);` (其他模板)

**修改后**:
- 统一为 `0 20px 60px rgba(0,0,0,0.25)`

---

## 修复效果

### 修复前
```
┌─────────────────────────────────┐
│  背景 (有padding)               │
│  ┌─────────────┐                │
│  │ 海报 (左对齐)│               │
│  └─────────────┘                │
│            过重阴影              │
└─────────────────────────────────┘
```

### 修复后
```
┌─────────────────────────────────┐
│  背景 (有padding)               │
│      ┌─────────────┐            │
│      │海报 (居中) │            │
│      └─────────────┘            │
│        适中阴影                  │
└─────────────────────────────────┘
```

---

## 修改文件

1. `templates/academic_panels.html`
2. `templates/multi_figure_grid.html`
3. `templates/simple_grid.html`

---

## 测试方法

```bash
# 重新生成海报
python main.py paper.pdf -t academic_panels.html

# 在浏览器中打开生成的 HTML
firefox output/poster.html
```

### 预期结果

✅ 海报卡片完美居中在背景中央  
✅ 左右两侧空白相等  
✅ 阴影柔和，不会被误认为边框  
✅ 在不同浏览器窗口大小下保持居中  

---

## 版本信息

- **版本**: v1.3.1
- **日期**: 2025-12-17
- **修复类型**: 样式优化 (CSS)
- **影响范围**: 全部模板
- **向后兼容**: ✅ 是

---

## 相关 Issue

- 海报卡片未居中
- 阴影被误认为边框
- 布局偏移问题

---

*文档生成时间: 2025-12-17*

