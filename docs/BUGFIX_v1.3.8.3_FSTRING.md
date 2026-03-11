# v1.3.8.3 F-string 格式化修复

## 🐛 问题描述

### 错误信息

```python
ValueError: Invalid format specifier ' "Introduction",
    "content": "- 要点1\n- 要点2\n- 要点3"
  ' for object of type 'str'

Traceback (most recent call last):
  File "/home/idrl/Paper2Poster/P2PW/src/editor.py", line 102, in _build_system_prompt
    "introduction": {
                    ^
    ...<2 lines>...
    },
    ^
ValueError: Invalid format specifier ...
```

---

## 🔍 根本原因

### F-string 语法冲突

**问题场景**:
1. v1.3.8.2 为了插入 `abstract_max_words` 变量，将 `_build_system_prompt()` 的返回值从普通字符串改为 f-string
2. Prompt 中包含大量 JSON 示例，用于指导 LLM 输出格式
3. JSON 使用 `{}` 花括号，与 f-string 的变量插入语法 `{variable}` 冲突
4. Python 尝试将 JSON 内容作为格式化参数处理，导致 ValueError

### F-string 工作原理

**在 f-string 中**:
- `{variable}` → 插入变量的值
- `{{` → 转义为单个 `{`
- `}}` → 转义为单个 `}`

**示例**:
```python
name = "Alice"
age = 30

# 正确：变量插入
f"Name: {name}, Age: {age}"  # → "Name: Alice, Age: 30"

# 错误：JSON 示例未转义
f"JSON: {"name": "{name}"}"  # ❌ ValueError

# 正确：JSON 示例已转义
f"JSON: {{\"name\": \"{name}\"}}"  # → "JSON: {\"name\": \"Alice\"}"
```

---

## ✅ 修复方案

### 转义所有 JSON 花括号

**修改位置**: `src/editor.py` 第 95-123 行

**修改前（错误）**:
```python
def _build_system_prompt(self, abstract_max_words: int = 130) -> str:
    return f"""...
    **重要**: 必须输出完整的 JSON，包含所有必需字段。请严格按照下面的 JSON Schema 格式输出：

    {
      "title": "海报标题（精简有力）",
      "authors": "作者1, 作者2, 作者3",
      "affiliation": "机构/学校名称",
      "abstract": "约100字的摘要...",
      "introduction": {
        "title": "Introduction",
        "content": "- 要点1\\n- 要点2\\n- 要点3"
      },
      ...
    }
    """
```

**问题分析**:
- Python 看到 f-string 中的 `{` 后，期望后面是变量名
- 但遇到的是 `"title": "..."`，这不是有效的 Python 表达式
- 导致 `ValueError: Invalid format specifier`

**修改后（正确）**:
```python
def _build_system_prompt(self, abstract_max_words: int = 130) -> str:
    return f"""...
    **重要**: 必须输出完整的 JSON，包含所有必需字段。请严格按照下面的 JSON Schema 格式输出：

    {{
      "title": "海报标题（精简有力）",
      "authors": "作者1, 作者2, 作者3",
      "affiliation": "机构/学校名称",
      "abstract": "约100字的摘要...",
      "introduction": {{
        "title": "Introduction",
        "content": "- 要点1\\n- 要点2\\n- 要点3"
      }},
      ...
    }}
    """
```

**效果**:
- `{{` 被 Python 解释为转义的 `{`
- `}}` 被 Python 解释为转义的 `}`
- 最终输出的 prompt 中显示正常的 JSON 示例
- 只有 `{abstract_max_words}` 被作为变量插入

---

## 📊 转义规则总结

### 完整的转义清单

在 f-string 中，以下所有花括号都需要转义：

| 原始字符 | 转义后 | 最终输出 |
|---------|--------|---------|
| `{` | `{{` | `{` |
| `}` | `}}` | `}` |
| `{variable}` | 保持不变 | 变量的值 |
| `{{variable}}` | `{{{{variable}}}}` | `{variable}` (字面量) |

### JSON 示例转义

**原始 JSON**:
```json
{
  "introduction": {
    "title": "Introduction"
  }
}
```

**在 f-string 中需要写为**:
```python
f"""
{{
  "introduction": {{
    "title": "Introduction"
  }}
}}
"""
```

**最终输出**:
```json
{
  "introduction": {
    "title": "Introduction"
  }
}
```

---

## 🧪 测试验证

### 验证脚本

```python
abstract_max_words = 130

# 测试转义后的 prompt
prompt = f"""
字数限制：严格控制在 **{abstract_max_words}字以内**

JSON 示例：
{{
  "title": "标题",
  "content": {{
    "text": "内容"
  }}
}}
"""

print("✅ f-string 格式化成功")
print(f"Prompt 长度: {len(prompt)} 字符")

# 检查变量插入
assert "130字以内" in prompt, "❌ 变量未插入"
print("✅ abstract_max_words 变量正确插入")

# 检查 JSON 格式
assert '{"title":' in prompt or '"title":' in prompt, "❌ JSON 格式错误"
print("✅ JSON 示例正确显示")
```

### 验证结果

- ✅ Python 语法检查通过
- ✅ f-string 格式化成功
- ✅ `abstract_max_words` 变量正确插入（"130字以内"）
- ✅ JSON 示例正确显示（花括号已转义）
- ✅ 无 linter 错误

---

## 💡 经验教训

### 教训 1: f-string 中使用 JSON 要小心

**问题**:
- f-string 非常强大，但与 JSON 的花括号语法冲突
- 如果不小心转义，会导致难以调试的错误

**解决方案**:
- ✅ 使用 f-string 时，仔细检查所有花括号
- ✅ 如果只需要插入少量变量，考虑使用 `.format()` 或 `%` 格式化
- ✅ 对于复杂的模板，考虑使用模板引擎（如 Jinja2）

### 教训 2: 逐步验证修改

**最佳实践**:
```python
# Step 1: 先用小示例测试
test_prompt = f"""{{
  "key": "value"
}}"""
assert test_prompt == '{\n  "key": "value"\n}', "转义失败"

# Step 2: 再应用到完整代码
```

### 教训 3: 替代方案

**方案 1: 使用 `.format()`**:
```python
def _build_system_prompt(self, abstract_max_words: int = 130) -> str:
    return """...
    字数限制：{abstract_max_words}字以内
    
    {
      "title": "..."
    }
    """.format(abstract_max_words=abstract_max_words)
```
- 优点：不需要转义 `{}`
- 缺点：所有 JSON 的 `{}` 都需要转义

**方案 2: 字符串拼接**:
```python
def _build_system_prompt(self, abstract_max_words: int = 130) -> str:
    return (
        "字数限制：" + str(abstract_max_words) + "字以内\n\n" +
        '{\n  "title": "..."\n}\n'
    )
```
- 优点：简单直接
- 缺点：可读性差

**方案 3: 使用模板变量标记**:
```python
def _build_system_prompt(self, abstract_max_words: int = 130) -> str:
    template = """...
    字数限制：<ABSTRACT_MAX_WORDS>字以内
    
    {
      "title": "..."
    }
    """
    return template.replace("<ABSTRACT_MAX_WORDS>", str(abstract_max_words))
```
- 优点：不需要转义，代码清晰
- 缺点：需要额外的 `.replace()` 调用

**当前选择**: 使用 f-string + 转义（方案最简洁，适合少量变量插入）

---

## 📚 相关资料

### Python 官方文档

- **F-strings**: https://docs.python.org/3/reference/lexical_analysis.html#f-strings
- **String Formatting**: https://docs.python.org/3/library/string.html#formatstrings

### 关键引用

> "A replacement field is delimited by curly braces `{}`. Anything that is not contained in braces is considered literal text. To include a brace character in the literal text, it can be escaped by doubling: `{{` and `}}`."
> 
> — Python Documentation

---

## 🚀 后续建议

### 代码审查清单

当使用 f-string 时，检查：
- [ ] 是否包含 JSON 或其他使用 `{}` 的格式？
- [ ] 所有非变量的 `{` 是否都转义为 `{{`？
- [ ] 所有非变量的 `}` 是否都转义为 `}}`？
- [ ] 变量插入是否正确（单个 `{variable}`）？
- [ ] 是否通过测试验证？

### 测试覆盖

为 `_build_system_prompt()` 添加单元测试：
```python
def test_build_system_prompt():
    editor = LLMEditor(...)
    
    # 测试变量插入
    prompt = editor._build_system_prompt(abstract_max_words=150)
    assert "150字以内" in prompt
    
    # 测试 JSON 格式
    assert '{"title":' in prompt or '"title":' in prompt
    assert prompt.count("{") == prompt.count("}")
```

---

**版本**: v1.3.8.3  
**日期**: 2025-12-18  
**修复**: F-string 格式化与 JSON 花括号冲突  
**作者**: Paper2Poster-Web 团队

