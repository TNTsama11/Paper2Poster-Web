# 从 Paper2Poster 项目借鉴的改进点

## 🎯 参考项目分析

**项目**: Paper2Poster (NeurIPS 2025 Dataset and Benchmark Track)
**路径**: `/home/idrl/Paper2Poster/Paper2Poster`
**论文**: https://arxiv.org/abs/2505.21497

## 🌟 核心优势对比

| 特性 | Paper2Poster | P2P-Web (我们) | 改进方向 |
|------|--------------|----------------|----------|
| **输出格式** | PPTX (可编辑) | HTML/PDF | ✅ 我们更轻量 |
| **内容溢出处理** | deoverflow 专门模块 | ❌ 无 | ⭐ 需要添加 |
| **布局算法** | binary-tree layout | grid layout | 🔄 可借鉴 |
| **配置方式** | YAML 文件 | Python config | 🔄 可改进 |
| **多轮优化** | Painter-Commenter loop | 单次生成 | 🔄 可添加 |
| **依赖** | LibreOffice, poppler | Playwright | ✅ 我们更简单 |
| **模板系统** | LaTeX Beamer | Jinja2 HTML | ✅ 我们更灵活 |

---

## 🎯 立即可以改进的5个点

### 1. ⭐ **Overflow 检测和处理** (高优先级)

**问题**: 用户反馈"画面被截断"，我们虽然改了CSS，但没有主动检测和处理overflow

**Paper2Poster 的方案**:
```python
# deoverflow.py - 使用VLM检测溢出并重新生成
def deoverflow(args, actor_config, critic_config):
    # 1. 截图当前海报
    # 2. VLM 检测是否有内容溢出
    # 3. 如果溢出，调整内容或布局
    # 4. 重新生成
```

**我们的实现建议**:
```python
# src/overflow_detector.py
class OverflowDetector:
    def detect_overflow(self, html_path, vision_model):
        """使用VLM检测内容是否溢出"""
        # 1. 截图
        screenshot = self.capture_screenshot(html_path)
        
        # 2. VLM分析
        prompt = """
        检查这张海报是否有以下问题：
        1. 文字被截断或显示不完整
        2. 图片超出边界
        3. 内容重叠
        
        返回JSON: {"has_overflow": bool, "issues": [str]}
        """
        
        result = vision_model.analyze(screenshot, prompt)
        return result
    
    def fix_overflow(self, poster_content, issues):
        """根据检测结果调整内容"""
        if "text_too_long" in issues:
            # 压缩文字
            poster_content = self.compress_text(poster_content)
        
        if "image_too_large" in issues:
            # 调整图片尺寸
            poster_content = self.resize_images(poster_content)
        
        return poster_content
```

---

### 2. 🎨 **YAML 配置支持** (中优先级)

**Paper2Poster 的方案**:
```yaml
# poster.yaml
main_text_font_size: 60
section_title_font_size: 80
poster_title_font_size: 85
title_text_color: [0, 0, 0]
main_text_color: [47, 85, 151]
section_title_vertical_align: "bottom"
section_title_symbol: "▶ "
```

**我们的实现建议**:
```python
# config/templates/academic_panels.yaml
poster:
  width: 1200
  height: 1800
  
  fonts:
    title: 2.1rem
    section_title: 1.2rem
    content: 0.88rem
    caption: 0.8rem
  
  colors:
    primary: "#667eea"
    secondary: "#764ba2"
    text: "#333"
    
  spacing:
    panel_gap: 12px
    panel_padding: 16px
    
  layout:
    columns: 3
    auto_rows: minmax(180px, auto)
```

**使用方式**:
```python
# main.py
--config poster.yaml  # 自定义配置
--theme academic      # 预设主题
```

---

### 3. 🌳 **Binary-Tree 布局算法** (中优先级)

**Paper2Poster 的方案**:
- 使用二叉树结构组织面板
- 保持阅读顺序
- 自动平衡空间

**当前问题**:
```html
<!-- 我们当前是固定的 grid 布局 -->
<div class="panels-container">
    <div class="panel panel-abstract">...</div>
    <div class="panel">Introduction</div>
    <div class="panel panel-large">Methods</div>
    <!-- 固定结构，不够灵活 -->
</div>
```

**改进建议**:
```python
# src/layout_planner.py
class BinaryTreeLayout:
    def plan_layout(self, sections, images):
        """
        根据内容量动态规划布局
        
        Args:
            sections: [{"title": "Introduction", "content": "...", "priority": 8}]
            images: [Figure对象列表]
            
        Returns:
            布局树结构
        """
        # 1. 计算每个section的内容量
        weights = self.calculate_weights(sections, images)
        
        # 2. 构建二叉树
        tree = self.build_tree(sections, weights)
        
        # 3. 转换为 grid 坐标
        grid_layout = self.tree_to_grid(tree)
        
        return grid_layout
```

---

### 4. 🔄 **多轮优化循环** (低优先级)

**Paper2Poster 的方案**:
```python
# Painter-Commenter Loop
for iteration in range(max_iterations):
    # Painter: 生成/更新海报
    poster = painter.generate(content, layout)
    
    # Commenter: VLM 评论
    feedback = commenter.critique(poster)
    
    # 如果满意，退出
    if feedback['score'] > threshold:
        break
    
    # 根据反馈调整
    content, layout = adjust(content, layout, feedback)
```

**我们的实现建议**:
```python
# src/optimizer.py
class PosterOptimizer:
    def optimize(self, poster_content, max_iterations=3):
        """
        多轮优化海报质量
        """
        for i in range(max_iterations):
            # 1. 渲染
            html_path = self.render(poster_content)
            
            # 2. VLM 评估
            score, feedback = self.evaluate(html_path)
            
            logger.info(f"Round {i+1}: Score = {score}/10")
            
            # 3. 如果足够好，退出
            if score >= 8.5:
                break
            
            # 4. 根据反馈调整
            poster_content = self.apply_feedback(
                poster_content, 
                feedback
            )
        
        return poster_content
```

---

### 5. 📐 **智能内容压缩** (中优先级)

**Paper2Poster 的方案**:
- 文本压缩：保留关键信息
- 图片选择：优先级排序
- 自适应调整：根据空间动态调整

**我们的实现建议**:
```python
# src/content_optimizer.py
class ContentOptimizer:
    def compress_if_needed(self, poster_content, target_size):
        """
        智能压缩内容以适应目标尺寸
        """
        # 1. 评估当前内容量
        estimated_height = self.estimate_height(poster_content)
        
        if estimated_height > target_size:
            # 2. 压缩文本
            for section in poster_content.sections:
                section.content = self.compress_text(
                    section.content,
                    max_bullets=5  # 最多5个要点
                )
            
            # 3. 减少图片
            poster_content.figures = self.select_top_figures(
                poster_content.figures,
                max_count=10  # 最多10张图
            )
        
        return poster_content
    
    def compress_text(self, text, max_bullets=5):
        """
        压缩文本要点
        """
        bullets = text.split('\n')
        if len(bullets) > max_bullets:
            # 使用LLM选择最重要的要点
            selected = self.llm_select_important(bullets, max_bullets)
            return '\n'.join(selected)
        return text
```

---

## 🛠️ 实现优先级

### Phase 1: 紧急修复 (1-2天)
1. ✅ ~~图片提取增强~~ (已完成 v1.2.4)
2. ✅ ~~布局优化~~ (已完成 v1.2.3)
3. 🔄 **Overflow 检测和修复** (v1.3.0)

### Phase 2: 功能增强 (3-5天)
4. 🔄 **YAML 配置支持** (v1.3.0)
5. 🔄 **智能内容压缩** (v1.3.1)

### Phase 3: 高级优化 (1周)
6. 🔄 **Binary-Tree 布局** (v1.4.0)
7. 🔄 **多轮优化循环** (v1.4.0)

---

## 📝 具体实现计划

### v1.3.0: Overflow 检测和 YAML 配置

**新增文件**:
```
src/overflow_detector.py    - Overflow 检测
src/content_optimizer.py    - 内容优化
config/themes/              - 主题配置目录
├── academic.yaml
├── modern.yaml
└── classic.yaml
```

**修改文件**:
```
main.py                     - 添加 --config 参数
src/renderer.py             - 集成 overflow 检测
src/editor.py               - 内容预压缩
```

**使用示例**:
```bash
# 使用自定义配置
python main.py paper.pdf \
    --config config/themes/academic.yaml \
    --enable-vision \
    --check-overflow

# 使用预设主题
python main.py paper.pdf \
    --theme modern \
    --enable-vision
```

---

## 🎯 预期效果

### 添加 Overflow 检测后:
- ✅ 自动检测内容是否被截断
- ✅ 智能调整字体大小或内容量
- ✅ 最多3轮迭代优化
- ✅ 用户可禁用自动优化 `--no-auto-fix`

### 添加 YAML 配置后:
- ✅ 用户可自定义所有样式参数
- ✅ 预设多种主题（学术、现代、经典）
- ✅ 支持机构/会议品牌定制
- ✅ 配置可复用和分享

---

## 📊 对比总结

| 特性 | Paper2Poster | P2P-Web (当前) | P2P-Web (v1.3+) |
|------|--------------|----------------|-----------------|
| Overflow 处理 | ✅ | ❌ | ✅ |
| 可配置性 | ✅ YAML | 🟡 Config.py | ✅ YAML |
| 多轮优化 | ✅ | ❌ | ✅ |
| 输出格式 | PPTX | HTML/PDF | HTML/PDF ✅ |
| 依赖复杂度 | 高 | 低 | 低 ✅ |
| 生成速度 | 慢 (~5min) | 快 (~1min) | 中 (~2min) |

---

## 🚀 开始实现

想要开始实现这些改进吗？我建议从最紧迫的 **Overflow 检测** 开始！

