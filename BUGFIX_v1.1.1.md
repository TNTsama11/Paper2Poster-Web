# Bug 修复说明 - v1.1.1

## 🐛 修复的问题

### Pydantic 验证错误

**问题描述:**
```
ValidationError: 8 validation errors for PosterContent
- authors: Input should be a valid string (got list)
- affiliation: Field required
- introduction: Field required
- ...
```

**发生原因:**
LLM 返回的 JSON 格式不完全符合 Pydantic 模型要求：
1. `authors` 字段返回列表而非字符串
2. 某些必需字段缺失

## ✅ 解决方案

### 1. 改进 Prompt

**之前:**
- 简单说明输出 JSON
- 没有明确的格式示例

**现在:**
- 提供完整的 JSON Schema 示例
- 明确说明每个字段的格式要求
- 特别强调 `authors` 必须是字符串

```python
# 新增的 Prompt 示例
{
  "title": "海报标题",
  "authors": "作者1, 作者2, 作者3",  # ← 明确指定为字符串
  "affiliation": "机构名称",
  ...
}
```

### 2. 添加自动数据修复

新增 `_fix_json_data()` 方法，自动处理常见问题：

```python
def _fix_json_data(self, data: dict, image_manifest: List[str]) -> dict:
    # 修复 authors（列表→字符串）
    if isinstance(data["authors"], list):
        data["authors"] = ", ".join(data["authors"])
    
    # 填充缺失字段
    if "affiliation" not in data:
        data["affiliation"] = "Unknown Institution"
    
    # 修复 section 结构
    # ...
```

**自动修复的问题:**
- ✅ `authors` 列表自动合并为字符串
- ✅ 缺失的 `affiliation` 自动填充
- ✅ 缺失的 section 自动补充默认值
- ✅ 无效的 `main_figure_path` 自动修正
- ✅ 缺失的 `references` 自动填充

### 3. 增强错误提示

**之前:**
```
LLM 调用失败: <原始错误>
```

**现在:**
```
LLM 返回的数据格式不完整。建议：
1. 使用更强大的模型（如 GPT-4）
2. 检查论文 PDF 质量
3. 尝试更短的论文
```

更具体的错误信息帮助用户快速定位问题。

## 📊 修复效果

### 测试场景

**场景 1: LLM 返回列表格式的 authors**
```json
{
  "authors": ["张三", "李四", "王五"]  // ← 列表格式
}
```

**修复后:**
```json
{
  "authors": "张三, 李四, 王五"  // ← 自动转为字符串
}
```

**场景 2: LLM 遗漏必需字段**
```json
{
  "title": "论文标题",
  "authors": "作者",
  // affiliation 缺失
  // introduction 缺失
  // ...
}
```

**修复后:**
```json
{
  "title": "论文标题",
  "authors": "作者",
  "affiliation": "Unknown Institution",  // ← 自动填充
  "introduction": {
    "title": "Introduction",
    "content": "- Content not available"
  },
  // ... 其他字段自动补充
}
```

## 🎯 使用建议

虽然添加了自动修复，但为了获得最佳效果，仍然建议：

### 1. 使用高质量模型

**推荐顺序:**
1. GPT-4 Turbo（最佳质量）
2. DeepSeek Chat（性价比高）
3. GPT-3.5 Turbo（速度快但可能不稳定）

### 2. 调整 Temperature

```python
# config.py 或 Web UI
TEMPERATURE = 0.2  # 更稳定的输出
```

较低的 temperature 可以减少 LLM 的随机性，提高格式一致性。

### 3. 使用高质量 PDF

- ✅ 文本可复制的 PDF
- ✅ 结构清晰的论文
- ❌ 避免扫描版 PDF
- ❌ 避免排版混乱的 PDF

## 🔍 调试方法

### 查看修复后的数据

在 `src/editor.py` 中已添加调试日志：

```python
logger.debug(f"修复后的 JSON: {json.dumps(content_dict, ...)}")
```

### 保存中间数据

**命令行:**
```bash
python main.py input/paper.pdf --save-json
```

**Web UI:**
勾选 "保存 JSON 数据" 选项

查看 `output/poster_content.json` 了解 LLM 的原始输出。

### 启用详细日志

```python
# 修改 src/logger.py
logger.setLevel(logging.DEBUG)
```

## 📝 代码变更

### 修改的文件

1. **src/editor.py**
   - 改进 `_build_system_prompt()` - 添加详细的 JSON 示例
   - 改进 `_build_user_prompt()` - 强调字段格式要求
   - 新增 `_fix_json_data()` - 自动修复数据问题
   - 改进错误处理 - 更友好的错误提示

### 新增的文件

2. **TROUBLESHOOTING.md**
   - 完整的故障排查指南
   - 涵盖所有常见错误
   - 提供详细的解决方案

3. **BUGFIX_v1.1.1.md** (本文件)
   - 详细说明修复内容

## 🚀 升级指南

如果你正在使用旧版本：

```bash
# 1. 更新代码
git pull

# 2. 无需安装新依赖
# （本次修复只更新了代码逻辑）

# 3. 重启 Web UI
./start_webui.sh
```

## 📞 反馈

如果你仍然遇到验证错误：

1. **查看日志** - 检查完整的错误信息
2. **保存 JSON** - 使用 `--save-json` 查看原始数据
3. **查看文档** - [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
4. **提交 Issue** - 附上错误日志和配置信息

---

**版本**: v1.1.1  
**修复日期**: 2025-12-17  
**状态**: ✅ 已解决

