# 使用示例

## 基础使用

### 1. 最简单的用法
```bash
python main.py input/paper.pdf
```
这将使用默认配置生成 PDF 格式的海报。

### 2. 生成 PNG 格式
```bash
python main.py input/paper.pdf -f png
```

### 3. 自定义输出文件名
```bash
python main.py input/paper.pdf -o my_awesome_poster
```
生成 `output/my_awesome_poster.pdf`

### 4. 保存 JSON 数据
```bash
python main.py input/paper.pdf --save-json
```
除了生成海报，还会保存 `output/poster_content.json`，方便查看 LLM 生成的结构化数据。

### 5. 使用自定义模板
```bash
python main.py input/paper.pdf -t my_custom_template.html
```

## 高级用法

### 组合多个参数
```bash
python main.py input/paper.pdf \
    -f png \
    -o conference_poster \
    --save-json \
    -t custom_two_column.html
```

### 批量处理多个 PDF
```bash
# 创建批处理脚本
for pdf in input/*.pdf; do
    echo "处理: $pdf"
    python main.py "$pdf" -o "$(basename "$pdf" .pdf)"
done
```

## 不同 LLM 服务配置示例

### 使用 OpenAI GPT-4
```env
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4-turbo-preview
```

### 使用 DeepSeek
```env
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat
```

### 使用本地 Ollama
```bash
# 1. 启动 Ollama
ollama serve

# 2. 安装 litellm 作为代理
pip install litellm
litellm --model ollama/llama2

# 3. 配置 .env
OPENAI_API_KEY=sk-dummy
OPENAI_BASE_URL=http://localhost:8000
OPENAI_MODEL=ollama/llama2
```

## 自定义模板示例

### 创建简单的两栏模板

创建 `templates/two_column.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 p-8">
    <div class="w-[{{ width }}px] h-[{{ height }}px] bg-white">
        <!-- 标题 -->
        <header class="bg-blue-600 text-white p-8 text-center">
            <h1 class="text-4xl font-bold">{{ poster.title }}</h1>
            <p class="text-xl mt-2">{{ poster.authors }}</p>
        </header>
        
        <!-- 两栏内容 -->
        <div class="grid grid-cols-2 gap-8 p-8">
            <!-- 左栏 -->
            <div>
                <h2>Abstract</h2>
                <p>{{ poster.abstract }}</p>
                <!-- 更多内容 -->
            </div>
            
            <!-- 右栏 -->
            <div>
                <img src="images/{{ poster.main_figure_path }}" />
                <!-- 更多内容 -->
            </div>
        </div>
    </div>
</body>
</html>
```

使用:
```bash
python main.py input/paper.pdf -t two_column.html
```

## 常见工作流

### 学术会议海报工作流
```bash
# 1. 准备 PDF
cp ~/Downloads/conference_paper.pdf input/

# 2. 生成海报（PNG 格式用于打印）
python main.py input/conference_paper.pdf -f png -o conference_poster

# 3. 同时保存 JSON 以便后续调整
python main.py input/conference_paper.pdf --save-json

# 4. 检查结果
open output/conference_poster.png
```

### 快速预览工作流
```bash
# 生成 HTML 后，直接在浏览器中查看
python main.py input/paper.pdf
open output/poster.html  # macOS
# 或
xdg-open output/poster.html  # Linux
```

### 批量生成多个论文海报
```bash
#!/bin/bash
# batch_convert.sh

papers=(
    "paper1.pdf"
    "paper2.pdf"
    "paper3.pdf"
)

for paper in "${papers[@]}"; do
    name=$(basename "$paper" .pdf)
    echo "正在处理: $name"
    python main.py "input/$paper" -o "$name" -f png
    echo "完成: output/${name}.png"
    echo "---"
done

echo "全部完成！"
```

## 调试技巧

### 查看 LLM 生成的原始数据
```bash
python main.py input/paper.pdf --save-json
cat output/poster_content.json | python -m json.tool
```

### 检查提取的图片
```bash
python main.py input/paper.pdf
ls -lh output/images/
```

### 测试模板渲染（不调用 LLM）
```python
# test_template.py
from src.renderer import PosterRenderer
from src.models import PosterContent, Section
import config

# 创建测试数据
test_data = PosterContent(
    title="测试海报",
    authors="张三, 李四",
    affiliation="某某大学",
    abstract="这是一个测试摘要" * 10,
    introduction=Section(title="Introduction", content="- 测试要点1\n- 测试要点2"),
    methods=Section(title="Methods", content="- 方法1\n- 方法2"),
    results=Section(title="Results", content="- 结果1\n- 结果2"),
    conclusion=Section(title="Conclusion", content="- 结论1\n- 结论2"),
    main_figure_path=None,
    main_figure_caption="测试图片",
    references=["Ref 1", "Ref 2", "Ref 3"]
)

# 渲染
renderer = PosterRenderer(config.TEMPLATES_DIR, config.OUTPUT_DIR)
renderer.render_html(test_data)
print("测试 HTML 已生成: output/poster.html")
```

## 性能优化

### 减少 API 调用成本
```python
# 在 config.py 中调整
MAX_TOKENS = 2048      # 降低 token 数
TEMPERATURE = 0.1      # 降低随机性
```

### 使用更便宜的模型
```env
# DeepSeek 更便宜
OPENAI_MODEL=deepseek-chat

# 或使用 GPT-3.5
OPENAI_MODEL=gpt-3.5-turbo
```

## 质量优化

### 获得更好的结果
1. 使用高质量 PDF（文字清晰可复制）
2. 使用更强大的模型（GPT-4）
3. 调整 temperature 为 0.2-0.3
4. 手动编辑 JSON 后重新渲染

### 手动修正 JSON 后重新渲染
```python
# manual_render.py
import json
from src.renderer import PosterRenderer
from src.models import PosterContent
import config

# 加载并修改 JSON
with open('output/poster_content.json', 'r') as f:
    data = json.load(f)

# 修改数据
data['title'] = '修改后的标题'

# 重新渲染
poster = PosterContent(**data)
renderer = PosterRenderer(config.TEMPLATES_DIR, config.OUTPUT_DIR)
renderer.render(poster, export_format='pdf')
```

