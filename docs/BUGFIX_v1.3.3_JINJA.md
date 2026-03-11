# v1.3.3 Jinja2 模板语法错误修复

## 问题描述

用户遇到 Jinja2 模板编译错误：

```
jinja2.exceptions.TemplateSyntaxError: Encountered unknown tag 'break'. 
Jinja was looking for the following tags: 'elif' or 'else' or 'endif'. 
The innermost block that needs to be closed is 'if'.
```

**错误位置**: `templates/academic_panels.html` 第421行

### 问题原因

**使用了 Jinja2 不支持的 `{% break %}` 标签**：

```jinja
{% for fig in sorted_figs %}
    <div class="figure-container">
        <img src="images/{{ fig.path }}" ...>
    </div>
    {% if loop.index >= 2 %}{% break %}{% endif %}  ← ❌ break 不存在
{% endfor %}
```

**为什么不支持 `break`？**
- Jinja2 是一个模板语言，不是完整的编程语言
- 设计哲学：简单、安全、受限
- 不支持 `break`, `continue`, `return` 等控制流语句

---

## 修复方案

### 使用切片语法限制循环次数

**修复前** ❌:
```jinja
{% for fig in sorted_figs %}
    <div class="figure-container">
        <span class="figure-type-badge badge-{{ fig.type }}">{{ fig.type }}</span>
        <img src="images/{{ fig.path }}" alt="{{ fig.caption }}" class="figure-img">
        <div class="figure-caption">{{ fig.caption }}</div>
    </div>
    {% if loop.index >= 2 %}{% break %}{% endif %}
{% endfor %}
```

**修复后** ✅:
```jinja
{% for fig in sorted_figs[:2] %}
    <div class="figure-container">
        <span class="figure-type-badge badge-{{ fig.type }}">{{ fig.type }}</span>
        <img src="images/{{ fig.path }}" alt="{{ fig.caption }}" class="figure-img">
        <div class="figure-caption">{{ fig.caption }}</div>
    </div>
{% endfor %}
```

---

## Jinja2 循环控制最佳实践

### 1. 限制循环次数

**方法**: 使用切片

```jinja
{# 只循环前3个元素 #}
{% for item in items[:3] %}
    ...
{% endfor %}

{# 跳过第一个，取接下来3个 #}
{% for item in items[1:4] %}
    ...
{% endfor %}
```

### 2. 条件过滤

**方法**: 使用 `if` 条件

```jinja
{# 只处理满足条件的元素 #}
{% for item in items %}
    {% if item.priority > 5 %}
        ...
    {% endif %}
{% endfor %}
```

**更优**: 使用过滤器

```jinja
{% for item in items | selectattr('priority', '>', 5) %}
    ...
{% endfor %}
```

### 3. 限制显示数量

**方法**: 使用 `loop.index` 和外层条件

```jinja
{% for item in items %}
    {% if loop.index <= 3 %}
        ...
    {% endif %}
{% endfor %}
```

**注意**: 虽然能工作，但不如切片高效（仍会遍历所有元素）

---

## 为什么切片更好？

| 方法 | 性能 | 可读性 | 推荐 |
|------|------|--------|------|
| `{% break %}` | - | - | ❌ 不支持 |
| `{% if loop.index %}` | 低 | 中 | ⚠️ 仍遍历全部 |
| 切片 `[:2]` | 高 | 高 | ✅ 最佳 |

**切片优势**:
1. **性能**: 只创建需要的子列表，不遍历多余元素
2. **简洁**: 一行代码，意图明确
3. **Pythonic**: 符合 Python 习惯
4. **安全**: 越界不会报错（自动截断）

---

## 修改文件

- `templates/academic_panels.html` - 第412-422行

**具体修改**:
```diff
- {% for fig in sorted_figs %}
+ {% for fig in sorted_figs[:2] %}
      <div class="figure-container">...</div>
-     {% if loop.index >= 2 %}{% break %}{% endif %}
  {% endfor %}
```

---

## 测试方法

```bash
# 重新生成海报
python webui_gradio.py
```

### 预期结果

✅ 模板编译成功  
✅ 不再报 `TemplateSyntaxError`  
✅ Key Figure 面板显示最多2张图片  
✅ 海报正常生成  

---

## 相关知识

### Jinja2 支持的循环控制

| 功能 | 语法 | 支持 |
|------|------|------|
| 循环 | `{% for %}` | ✅ |
| 条件 | `{% if %}` | ✅ |
| 切片 | `items[:3]` | ✅ |
| 过滤 | `items \| filter` | ✅ |
| break | `{% break %}` | ❌ |
| continue | `{% continue %}` | ❌ |
| return | `{% return %}` | ❌ |

### Loop 对象变量

```jinja
{% for item in items %}
    {{ loop.index }}      {# 1, 2, 3, ... #}
    {{ loop.index0 }}     {# 0, 1, 2, ... #}
    {{ loop.first }}      {# True 如果是第一个 #}
    {{ loop.last }}       {# True 如果是最后一个 #}
    {{ loop.length }}     {# 总长度 #}
{% endfor %}
```

---

## 版本信息

- **版本**: v1.3.3
- **日期**: 2025-12-17
- **修复类型**: Bug Fix (模板语法)
- **优先级**: 🔴 Critical (阻断性错误)
- **影响范围**: `academic_panels.html` 模板

---

## 相关问题

- Jinja2 TemplateSyntaxError
- Encountered unknown tag 'break'
- 模板编译失败

---

*文档生成时间: 2025-12-17*

