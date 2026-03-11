# 测试学术会议模板修复

## 🎯 快速测试

### 1. 确认问题已修复

使用相同的PDF重新生成海报：

```bash
# 命令行方式
python main.py your_paper.pdf \
    -t academic_panels.html \
    --enable-vision \
    --vision-model gpt-4o-mini

# 或使用 Web UI
# 1. 上传相同的 PDF
# 2. 选择 "学术会议 (academic_panels) ⭐" 模板
# 3. 勾选 "启用视觉分析"
# 4. 点击生成
```

### 2. 检查修复效果

**KEY RESULTS 区域应该显示**:
- ✅ 实验结果对比图
- ✅ 性能评估图表
- ✅ 主要研究发现的图片

**不应该显示**:
- ❌ 期刊封面
- ❌ Logo
- ❌ 版权声明

---

## 🔍 详细测试步骤

### 步骤 1: 准备测试环境

```bash
cd /home/idrl/Paper2Poster/P2PW

# 确认代码已更新
git status

# 查看修改的文件
git diff templates/academic_panels.html
git diff src/vision_analyzer.py
```

### 步骤 2: 测试原PDF

```bash
# 使用学术会议模板重新生成
python main.py input/your_paper.pdf \
    -t academic_panels.html \
    --enable-vision \
    --vision-model Qwen/Qwen2-VL-7B-Instruct \
    -o output/test_fix
```

### 步骤 3: 查看日志

```bash
# 检查日志，确认图片分析过程
tail -100 output/poster.log

# 查找关键信息：
# - "图片 xxx 被识别为无关内容，已过滤" ✅ 正常
# - "分析图片: xxx" - 查看哪些图片被分析
# - "图片分析完成，保留 X 张图片" - 确认过滤效果
```

### 步骤 4: 对比生成结果

打开生成的海报，检查：

1. **KEY RESULTS 面板**
   - [ ] 显示的是实验结果图？
   - [ ] 不是期刊封面？
   - [ ] 图片清晰且相关？

2. **其他面板**
   - [ ] METHODS 显示架构图/流程图？
   - [ ] RESULTS 显示实验结果？
   - [ ] 图片分布合理？

3. **整体效果**
   - [ ] 无明显的无关图片？
   - [ ] 重要图片优先显示？
   - [ ] 空间利用率高？

---

## 📝 测试报告模板

如果发现问题，请按此格式反馈：

```
### 测试环境
- Python 版本: 
- 模型: 
- 模板: academic_panels.html
- 视觉分析: 启用/禁用

### 问题描述
[描述问题，如：KEY RESULTS 仍显示期刊封面]

### 截图
[上传海报截图]

### 日志
[粘贴相关日志，特别是图片分析部分]

### 重现步骤
1. 
2. 
3. 
```

---

## 🎨 预期效果示例

### 修复前
```
┌─────────────────────────────────────┐
│  KEY RESULTS                         │
│  ┌─────────────────────────────┐   │
│  │  Pattern Recognition         │   │ ❌ 期刊封面
│  │  [期刊 logo]                 │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

### 修复后
```
┌─────────────────────────────────────┐
│  KEY RESULTS                         │
│  ┌─────────────────────────────┐   │
│  │  [实验结果对比柱状图]        │   │ ✅ 实验结果
│  │  准确率: 95% vs 85%          │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

---

## 💡 测试技巧

### 1. 对比测试
保留旧版本生成的海报，与新版本对比：

```bash
# 生成到不同目录
python main.py paper.pdf -o output/old_version  # 修复前
python main.py paper.pdf -o output/new_version  # 修复后

# 对比
diff output/old_version/poster.html output/new_version/poster.html
```

### 2. 多PDF测试
测试不同类型的论文：

```bash
# 测试集
papers=(
    "paper_with_cover.pdf"      # 含期刊封面
    "paper_multi_figures.pdf"   # 多图论文
    "paper_few_figures.pdf"     # 少图论文
)

for pdf in "${papers[@]}"; do
    echo "Testing $pdf..."
    python main.py "input/$pdf" -t academic_panels.html --enable-vision
done
```

### 3. 视觉分析对比
测试启用/禁用视觉分析的区别：

```bash
# 禁用视觉分析 (简单分类)
python main.py paper.pdf -t academic_panels.html -o output/no_vision

# 启用视觉分析 (智能分类)
python main.py paper.pdf -t academic_panels.html --enable-vision -o output/with_vision

# 对比效果
```

---

## ⚠️ 注意事项

### 必须启用视觉分析
本修复依赖视觉模型识别图片内容，如果不启用：
- ⚠️ 仍可能显示期刊封面（基于简单的顺序分类）
- ⚠️ 图片优先级不准确
- ⚠️ 无法过滤无关图片

### 视觉模型选择
推荐模型（按识别准确性）：
1. **gpt-4o** - 最准确，但成本高
2. **gpt-4o-mini** - 平衡性价比 ⭐
3. **Qwen2-VL-7B** - 中文友好，便宜 ⭐

### API配置
确认 API 配置正确：

```bash
# 检查 .env 文件
cat .env | grep -E "VISION|API"

# 应该包含：
# VISION_MODEL=gpt-4o-mini
# VISION_API_KEY=sk-xxx
# VISION_BASE_URL=https://api.openai.com/v1
```

---

## 📞 反馈

测试完成后，请反馈：

✅ 修复成功 - KEY RESULTS 显示正确
❌ 仍有问题 - 附上截图和日志

---

**开始测试，验证修复效果！** 🚀

