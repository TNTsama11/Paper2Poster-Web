# Web UI 使用指南

Paper2Poster-Web 提供了两种 Web 界面，让你无需命令行即可轻松使用。

## 🎨 两种 Web UI

### 1. Gradio UI (推荐)

**特点:**
- ✅ 简洁易用，界面现代
- ✅ 自动处理文件上传下载
- ✅ 实时进度显示
- ✅ 可生成公网分享链接
- ✅ 适合快速使用和演示

**访问地址:** http://localhost:7860

### 2. Streamlit UI

**特点:**
- ✅ 功能丰富，布局清晰
- ✅ 侧边栏详细说明
- ✅ 预览生成内容
- ✅ 快捷配置按钮
- ✅ 适合日常工作使用

**访问地址:** http://localhost:8501

## 🚀 快速启动

### 方法 1: 使用启动脚本（推荐）

**Linux/Mac:**
```bash
./start_webui.sh
```

**Windows:**
```bash
start_webui.bat
```

然后按提示选择要启动的界面：
- 输入 `1` 启动 Gradio UI
- 输入 `2` 启动 Streamlit UI

### 方法 2: 直接运行

**启动 Gradio UI:**
```bash
python webui_gradio.py
```

**启动 Streamlit UI:**
```bash
streamlit run webui_streamlit.py
```

## 📖 使用步骤

### 1. 启动服务

选择一种启动方式，等待服务启动完成。

Gradio 会显示：
```
Running on local URL:  http://localhost:7860
```

Streamlit 会自动打开浏览器。

### 2. 上传 PDF

在界面中点击或拖拽上传你的论文 PDF 文件。

**要求:**
- 文件格式: PDF
- 文本可复制（非扫描件）
- 建议大小: < 50MB

### 3. 配置 API

填写你的 LLM API 配置：

**OpenAI GPT-4 (推荐质量):**
```
API 密钥: sk-...
API URL: https://api.openai.com/v1
模型名称: gpt-4-turbo-preview
```

**DeepSeek (推荐性价比):**
```
API 密钥: sk-...
API URL: https://api.deepseek.com/v1
模型名称: deepseek-chat
```

**提示:** 
- 如果已配置 `.env` 文件，会自动填充
- 在 Streamlit UI 中可使用快捷按钮切换配置

### 4. 设置海报

**输出格式:**
- `PDF` - 适合打印和正式场合
- `PNG` - 适合在线展示和社交媒体

**海报尺寸:**
- 默认: 1600x1200 (4:3 比例)
- A1 海报: 2384x3370
- A2 海报: 1684x2384
- 自定义尺寸

**Temperature:**
- 0.0-0.3: 稳定输出（推荐）
- 0.4-0.7: 均衡
- 0.8-1.0: 创造性输出

**其他选项:**
- ☑️ 保存 JSON 数据 - 保存 LLM 生成的结构化数据，方便后续调整

### 4.5 选择海报模板 ⭐ (重要)

在 **"🎨 高级功能"** 区域中，你可以选择不同风格的海报模板：

| 模板 | 特点 | 适用场景 | 需要视觉分析 |
|------|------|---------|------------|
| **经典三栏** | 简洁清晰，单图展示 | 快速测试，图片较少 | ❌ |
| **多图丰富** ⭐ | 最多6张图，内容饱满 | 日常使用推荐 | ✅ |
| **学术会议** ⭐⭐⭐ | 9面板专业布局 | 学术会议，追求最佳效果 | ✅ |

**重要提示**: 
- "多图丰富" 和 "学术会议" 模板需要勾选 **"启用视觉分析"** 并配置视觉模型
- 详细的模板选择指南请查看: [docs/WEBUI_TEMPLATE_GUIDE.md](docs/WEBUI_TEMPLATE_GUIDE.md)
- 快速参考: [docs/TEMPLATE_SELECTION.md](docs/TEMPLATE_SELECTION.md)

### 5. 生成海报

点击 **"🚀 生成海报"** 按钮，等待处理完成。

**处理时间:**
- 短论文 (< 5 页): 30-45 秒
- 中等论文 (5-15 页): 45-90 秒
- 长论文 (> 15 页): 90-120 秒

**进度显示:**
- 📄 解析 PDF (30%)
- 🤖 LLM 生成内容 (40%)
- 🎨 渲染海报 (30%)

### 6. 下载结果

生成完成后，可以下载：
- 📥 海报文件 (.pdf 或 .png)
- 📥 HTML 源文件
- 📥 JSON 数据 (如果勾选)

## 🎯 使用技巧

### 提高成功率

1. **使用高质量 PDF**
   - 确保文本可以复制粘贴
   - 避免使用扫描版 PDF
   - 图片清晰度高

2. **选择合适的模型**
   - GPT-4: 质量最好，价格较高
   - DeepSeek: 性价比高，效果不错
   - GPT-3.5: 速度快，但效果一般

3. **调整 Temperature**
   - 科技论文: 使用 0.2-0.3
   - 人文论文: 可以用 0.4-0.5
   - 需要创意: 可以用 0.6-0.7

### 批量处理

**方式 1: 多次上传**
在 Web UI 中依次上传处理多个 PDF

**方式 2: 使用命令行**
对于大量文件，建议使用命令行批处理：
```bash
for pdf in input/*.pdf; do
    python main.py "$pdf"
done
```

### 自定义优化

1. **保存 JSON 后手动调整**
   - 勾选"保存 JSON 数据"
   - 下载 JSON 文件
   - 手动编辑优化内容
   - 使用命令行重新渲染

2. **使用自定义模板**
   - Web UI 目前只支持默认模板
   - 如需自定义，使用命令行:
     ```bash
     python main.py input/paper.pdf -t custom_template.html
     ```

## 🌐 远程访问

### 在局域网内访问

**Gradio:**
修改 `webui_gradio.py`，将 `server_name` 改为服务器 IP：
```python
demo.launch(server_name="192.168.1.100", server_port=7860)
```

**Streamlit:**
```bash
streamlit run webui_streamlit.py --server.address 0.0.0.0
```

然后在局域网内通过 `http://服务器IP:端口` 访问。

### 生成公网链接（Gradio）

修改 `webui_gradio.py`：
```python
demo.launch(share=True)  # 设为 True
```

Gradio 会生成一个临时的公网链接（有效期 72 小时）。

**注意:** 公网访问需注意安全，避免泄露 API 密钥。

## 🔧 故障排查

### 问题 1: 启动失败

**症状:** 运行启动脚本后报错

**解决方法:**
```bash
# 检查依赖是否安装
pip list | grep gradio
pip list | grep streamlit

# 重新安装
pip install -r requirements.txt
```

### 问题 2: 端口被占用

**症状:** 提示端口 7860 或 8501 已被使用

**解决方法:**

修改端口号：

**Gradio (`webui_gradio.py`):**
```python
demo.launch(server_port=7861)  # 改为其他端口
```

**Streamlit:**
```bash
streamlit run webui_streamlit.py --server.port 8502
```

### 问题 3: 生成失败

**症状:** 点击生成后报错

**可能原因及解决:**

1. **API 密钥错误**
   - 检查密钥是否正确
   - 确认 API 账户有余额

2. **网络问题**
   - 检查能否访问 API 服务
   - 尝试使用代理

3. **PDF 问题**
   - 尝试其他 PDF 文件
   - 确认 PDF 文本可复制

4. **依赖问题**
   - 检查 Playwright 是否安装:
     ```bash
     playwright install chromium
     ```

### 问题 4: 中文显示乱码

**解决方法:**
- 确保网络可访问 Google Fonts
- 或修改模板使用本地字体

## 📊 性能优化

### 加快处理速度

1. **使用更快的模型**
   - DeepSeek 响应速度较快
   - GPT-3.5 Turbo 更快但质量较低

2. **降低海报分辨率**
   - 预览时使用较低分辨率
   - 最终导出时再提高分辨率

3. **优化网络**
   - 使用稳定的网络连接
   - 必要时配置代理

### 节省 API 成本

1. **使用性价比高的服务**
   - DeepSeek: 约 $0.0007/次
   - GPT-4: 约 $0.03-0.05/次
   - GPT-3.5: 约 $0.002/次

2. **重复利用结果**
   - 保存 JSON 数据
   - 手动修改后重新渲染
   - 避免重复调用 LLM

## 🎨 界面对比

| 特性 | Gradio UI | Streamlit UI |
|------|-----------|--------------|
| 界面风格 | 现代、简洁 | 清晰、专业 |
| 易用性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 功能丰富度 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 加载速度 | 快 | 中等 |
| 进度显示 | 详细 | 标准 |
| 公网分享 | ✅ 支持 | ❌ 需配置 |
| 文档说明 | 折叠面板 | 侧边栏 |
| 快捷配置 | ❌ | ✅ |
| 推荐场景 | 演示、分享 | 日常使用 |

## 💡 最佳实践

1. **首次使用**
   - 推荐使用 Gradio UI
   - 先用小文件测试
   - 确认配置正确

2. **日常工作**
   - 推荐使用 Streamlit UI
   - 保存常用配置
   - 开启 JSON 保存

3. **批量处理**
   - 使用命令行版本
   - 编写批处理脚本
   - 自动化流程

4. **远程协作**
   - 使用 Gradio 的 share 功能
   - 生成临时分享链接
   - 注意保护 API 密钥

## 📞 获取帮助

- 📖 查看主文档: [README.md](README.md)
- 💡 使用示例: [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)
- 🚀 快速开始: [QUICKSTART.md](QUICKSTART.md)
- 🐛 问题反馈: 提交 Issue

---

**提示:** 两个 Web UI 可以同时运行，它们使用不同的端口互不干扰。

