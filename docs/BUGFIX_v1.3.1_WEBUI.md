# v1.3.1 Web UI 兼容性修复

## 问题描述

用户在使用 Gradio Web UI 时遇到错误：

```
ValueError: too many values to unpack (expected 2)
  File "/home/idrl/Paper2Poster/P2PW/webui_gradio.py", line 95, in process_paper
    full_text, image_manifest = harvester.harvest()
```

### 问题原因

在 **v1.3.0** 更新中，`harvester.harvest()` 的返回值从 **2个** 改为 **3个**：

**v1.2.x (旧版本)**:
```python
full_text, image_manifest = harvester.harvest()
```

**v1.3.0+ (新版本)**:
```python
full_text, image_manifest, formula_manifest = harvester.harvest()
#                          ^^^^^^^^^^^^^^^^^ 新增公式清单
```

但 Web UI 代码未同步更新，仍使用旧的2个值接收方式，导致解包错误。

---

## 修复内容

### 1. Gradio Web UI (`webui_gradio.py`)

**修复前**:
```python
full_text, image_manifest = harvester.harvest()

progress(0.3, desc=f"✅ PDF 解析完成 (提取 {len(image_manifest)} 张图片)")
```

**修复后**:
```python
full_text, image_manifest, formula_manifest = harvester.harvest()

progress(0.3, desc=f"✅ PDF 解析完成 (提取 {len(image_manifest)} 张图片, {len(formula_manifest)} 个公式)")
```

### 2. Streamlit Web UI (`webui_streamlit.py`)

**修复前**:
```python
full_text, image_manifest = harvester.harvest()

status_text.text(f"✅ PDF 解析完成 (提取 {len(image_manifest)} 张图片)")
```

**修复后**:
```python
full_text, image_manifest, formula_manifest = harvester.harvest()

status_text.text(f"✅ PDF 解析完成 (提取 {len(image_manifest)} 张图片, {len(formula_manifest)} 个公式)")
```

### 3. 文档更新 (`TROUBLESHOOTING.md`)

更新了示例代码，使用新的3个返回值：

```python
from src.harvester import PDFHarvester
harvester = PDFHarvester("input/test.pdf", "output")
text, images, formulas = harvester.harvest()  # 新增 formulas
print(f"提取到 {len(images)} 张图片, {len(formulas)} 个公式")
```

---

## 影响范围

- ✅ `webui_gradio.py` - Gradio Web UI
- ✅ `webui_streamlit.py` - Streamlit Web UI
- ✅ `TROUBLESHOOTING.md` - 故障排除文档
- ✅ `main.py` - CLI 已在 v1.3.0 中更新（无问题）

---

## 测试方法

### 启动 Gradio Web UI

```bash
python webui_gradio.py
```

### 启动 Streamlit Web UI

```bash
streamlit run webui_streamlit.py
```

### 预期结果

1. ✅ 上传 PDF 后不再报错
2. ✅ 进度提示显示：`✅ PDF 解析完成 (提取 X 张图片, Y 个公式)`
3. ✅ 生成的海报包含公式面板（如果使用 academic_panels 模板）

---

## 向后兼容性

| 组件             | v1.2.x | v1.3.0 | v1.3.1 |
|------------------|--------|--------|--------|
| CLI (main.py)    | ✅     | ✅     | ✅     |
| Gradio Web UI    | ✅     | ❌     | ✅     |
| Streamlit Web UI | ✅     | ❌     | ✅     |
| harvester.py     | 返回2值 | 返回3值 | 返回3值 |

**结论**: v1.3.1 完全修复了 v1.3.0 引入的 Web UI 兼容性问题。

---

## 相关更新

- **v1.3.0**: 新增公式提取功能，`harvest()` 返回3个值
- **v1.3.1**: 
  - 修复 Web UI 接收返回值错误
  - 修复模板居中对齐问题

---

## 版本信息

- **版本**: v1.3.1
- **日期**: 2025-12-17
- **修复类型**: Bug Fix (兼容性)
- **优先级**: 🔴 High (阻断性错误)
- **影响用户**: 所有使用 Web UI 的用户

---

*文档生成时间: 2025-12-17*

