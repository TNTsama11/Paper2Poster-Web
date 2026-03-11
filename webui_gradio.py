#!/usr/bin/env python3
"""
Paper2Poster-Web Gradio Web UI
提供友好的 Web 界面进行论文转海报操作
"""
import os
import sys
import re
import gradio as gr
from pathlib import Path
import tempfile
import shutil
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, Dict

# 导入配置和核心模块
import config
from src.harvester import PDFHarvester
from src.editor import LLMEditor
from src.renderer import PosterRenderer
from src.logger import setup_logger
from src.exceptions import Paper2PosterError

logger = setup_logger("WebUI")


def test_api_connection(api_key: str, api_base_url: str, model_name: str) -> str:
    """
    测试 API 连接是否正常

    Args:
        api_key: API 密钥
        api_base_url: API 基础 URL
        model_name: 模型名称

    Returns:
        测试结果信息
    """
    if not api_key or api_key.strip() == "":
        return "❌ 请输入 API 密钥"

    try:
        from openai import OpenAI
        from openai import AuthenticationError, RateLimitError, APIConnectionError

        client = OpenAI(
            api_key=api_key.strip(),
            base_url=api_base_url.strip() if api_base_url.strip() else "https://api.openai.com/v1"
        )

        # 发送一个简单的测试请求
        response = client.chat.completions.create(
            model=model_name.strip() if model_name.strip() else "gpt-4-turbo-preview",
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=5,
            timeout=10
        )

        return f"✅ API 连接成功！\n\n模型: {model_name}\n响应: {response.choices[0].message.content}"

    except AuthenticationError:
        return "❌ API 密钥认证失败\n\n💡 请检查：\n1. API 密钥是否正确\n2. API 密钥是否已过期"
    except RateLimitError:
        return "⚠️ API 请求频率超限\n\n💡 请稍等几秒后重试"
    except APIConnectionError as e:
        return f"❌ 无法连接到 API 服务\n\n💡 请检查：\n1. 网络连接是否正常\n2. API URL 是否正确\n3. 是否需要代理\n\n错误详情: {str(e)[:100]}"
    except Exception as e:
        error_str = str(e).lower()
        if "timeout" in error_str:
            return "❌ 连接超时\n\n💡 请检查网络连接或尝试其他 API 服务"
        return f"❌ 测试失败: {str(e)[:200]}"

# 全局变量存储输出目录
output_base_dir = Path(__file__).parent / "output"
output_base_dir.mkdir(exist_ok=True)
temp_dir = output_base_dir


def process_paper(
    pdf_file,
    api_key,
    api_base_url,
    model_name,
    output_format,
    poster_preset,
    poster_width,
    poster_height,
    temperature,
    save_json,
    enable_vision,
    vision_model,
    template_choice,
    max_images,
    min_image_size,
    abstract_max_words,
    output_language,
    check_overflow,
    max_iterations,
    progress=gr.Progress()
):
    """
    处理论文转海报的主流程
    
    Args:
        pdf_file: 上传的 PDF 文件
        api_key: API 密钥
        api_base_url: API 基础 URL
        model_name: 模型名称
        output_format: 输出格式
        poster_width: 海报宽度
        poster_height: 海报高度
        temperature: 温度参数
        save_json: 是否保存 JSON
        progress: Gradio 进度条
    
    Returns:
        (海报文件路径, HTML文件路径, JSON文件路径或None, 状态信息)
    """
    try:
        # 检查 API 密钥
        if not api_key or api_key.strip() == "":
            return None, None, None, "❌ 错误: 请输入 API 密钥"
        
        # 检查 PDF 文件
        if pdf_file is None:
            return None, None, None, "❌ 错误: 请上传 PDF 文件"
        
        logger.info("=" * 80)
        logger.info("Web UI: 开始处理论文")
        logger.info("=" * 80)
        
        # 从 PDF 文件名生成输出目录名
        pdf_path = Path(pdf_file.name)
        pdf_name = pdf_path.stem  # 获取文件名（不含扩展名）
        # 清理文件名：移除特殊字符，保留字母、数字、中文、下划线和连字符
        safe_name = re.sub(r'[^\w\u4e00-\u9fff-]', '_', pdf_name)
        safe_name = safe_name.strip('_')  # 移除首尾下划线
        # 如果清理后为空，使用时间戳作为后备
        if not safe_name:
            safe_name = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 创建输出目录（使用 PDF 文件名）
        output_temp = temp_dir / safe_name
        output_temp.mkdir(exist_ok=True)
        images_temp = output_temp / "images"
        images_temp.mkdir(exist_ok=True)
        
        # ============================================
        # 步骤 1: 素材收割 (20%)
        # ============================================
        progress(0.1, desc="📄 正在解析 PDF...")
        
        harvester = PDFHarvester(
            pdf_path=pdf_file.name,
            output_dir=output_temp,
            min_width=int(min_image_size),
            min_height=int(min_image_size)
        )
        
        full_text, image_manifest, formula_manifest = harvester.harvest()
        
        progress(0.3, desc=f"✅ PDF 解析完成 (提取 {len(image_manifest)} 张图片, {len(formula_manifest)} 个公式)")
        
        # ============================================
        # 步骤 2: LLM 编辑 (50%)
        # ============================================
        progress(0.4, desc="🤖 正在调用 LLM 生成内容...")
        
        editor = LLMEditor(
            api_key=api_key,
            base_url=api_base_url,
            model=model_name,
            max_tokens=config.MAX_TOKENS,
            temperature=temperature,
            enable_vision=enable_vision,
            vision_model=vision_model if vision_model.strip() else None,
            images_dir=images_temp
        )
        
        # 解析输出语言
        if "中文" in output_language:
            language = "chinese"
        elif "英文" in output_language:
            language = "english"
        else:
            language = "auto"
        
        poster_content = editor.edit(
            full_text=full_text,
            image_manifest=image_manifest,
            max_images=int(max_images),
            abstract_max_words=int(abstract_max_words),
            output_language=language
        )
        
        progress(0.7, desc="✅ 内容生成完成")
        
        # 保存 JSON（如果需要）
        json_path = None
        if save_json:
            json_path = output_temp / "poster_content.json"
            import json
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(poster_content.to_dict(), f, ensure_ascii=False, indent=2)
            logger.info(f"JSON 已保存: {json_path}")
        
        # ============================================
        # 步骤 3: 确定海报尺寸
        # ============================================
        # 根据模板确定推荐尺寸
        template_map = {
            "经典三栏 (simple_grid)": "simple_grid.html",
            "多图丰富 (multi_figure_grid)": "multi_figure_grid.html",
            "学术会议-纵向 (academic_panels)": "academic_panels.html",
            "学术会议-横向16:9 (academic_panels_landscape) ⭐ 推荐": "academic_panels_landscape.html"
        }
        template_name = template_map.get(template_choice, "simple_grid.html")
        
        # 确定最终尺寸（优先级：手动输入 > 预设 > 模板推荐）
        final_width = poster_width
        final_height = poster_height
        
        if not final_width or not final_height:
            if poster_preset and poster_preset != "自动 (根据模板推荐)":
                # 从预设中提取key
                preset_key = poster_preset.split(":")[0].strip()
                if preset_key in config.POSTER_PRESETS:
                    preset = config.POSTER_PRESETS[preset_key]
                    final_width = final_width or preset[0]
                    final_height = final_height or preset[1]
                    logger.info(f"📐 使用预设尺寸: {preset_key} ({preset[2]})")
        
        if not final_width or not final_height:
            # 使用模板推荐尺寸
            recommended_preset = config.TEMPLATE_RECOMMENDED_SIZES.get(template_name, "default")
            preset = config.POSTER_PRESETS[recommended_preset]
            final_width = final_width or preset[0]
            final_height = final_height or preset[1]
            logger.info(f"📐 模板推荐尺寸: {template_name} → {recommended_preset} ({preset[2]})")
        
        logger.info(f"📐 最终海报尺寸: {final_width}×{final_height} 像素")
        
        # ============================================
        # 步骤 4: 渲染导出 (30%)
        # ============================================
        progress(0.8, desc="🎨 正在渲染海报...")
        
        renderer = PosterRenderer(
            templates_dir=config.TEMPLATES_DIR,
            output_dir=output_temp,
            poster_width=int(final_width),
            poster_height=int(final_height)
        )
        
        # 如果启用溢出检测
        if check_overflow and enable_vision:
            from openai import OpenAI
            from src.overflow_detector import OverflowDetector
            from src.content_compressor import ContentCompressor
            
            logger.info("🔄 启用溢出检测")
            
            vision_client = OpenAI(api_key=api_key, base_url=api_base_url)
            
            overflow_detector = OverflowDetector(
                vision_client=vision_client,
                vision_model=vision_model or "gpt-4o-mini",
                enabled=True
            )
            
            content_compressor = ContentCompressor(llm_client=vision_client, model=model_name)
            
            final_path = renderer.render_with_overflow_check(
                poster_content=poster_content,
                export_format=output_format,
                template_name=template_name,
                overflow_detector=overflow_detector,
                content_compressor=content_compressor,
                max_iterations=int(max_iterations),
                quality_threshold=8.0
            )
        else:
            final_path = renderer.render(
                poster_content=poster_content,
                export_format=output_format,
                template_name=template_name
            )
        
        html_path = output_temp / "poster.html"
        
        progress(1.0, desc="✅ 海报生成完成！")
        
        # 生成状态信息
        status = f"""
✅ **转换成功！**

📊 **处理结果:**
- 论文标题: {poster_content.title}
- 作者: {poster_content.authors}
- 提取图片: {len(image_manifest)} 张
- 主图: {poster_content.main_figure_path or '无'}
- 输出格式: {output_format.upper()}
- 海报尺寸: {poster_width}x{poster_height}

📁 **文件保存位置:**
- 海报: `{final_path}`
- HTML: `{html_path}`
{f'- JSON: `{json_path}`' if json_path else ''}

💡 文件已保存到 output 目录，可直接打开使用。
"""
        
        logger.info("=" * 80)
        logger.info("✅ Web UI: 处理完成")
        logger.info("=" * 80)
        
        return final_path, str(html_path), str(json_path) if json_path else None, status
        
    except Paper2PosterError as e:
        # 使用友好异常的消息
        error_msg = f"❌ 处理失败\n\n{e.to_user_friendly()}"
        logger.error(error_msg, exc_info=True)
        return None, None, None, error_msg
    except Exception as e:
        error_msg = f"❌ 处理失败: {str(e)}\n\n💡 如果问题持续，请检查：\n1. API 配置是否正确\n2. 网络连接\n3. PDF 文件质量"
        logger.error(error_msg, exc_info=True)
        return None, None, None, error_msg


def process_single_paper_wrapper(
    pdf_path: str,
    output_dir: Path,
    api_key: str,
    api_base_url: str,
    model_name: str,
    output_format: str,
    poster_preset: str,
    poster_width: float,
    poster_height: float,
    temperature: float,
    save_json: bool,
    enable_vision: bool,
    vision_model: str,
    template_choice: str,
    max_images: int,
    min_image_size: int,
    abstract_max_words: int,
    output_language: str,
    check_overflow: bool,
    max_iterations: int
) -> Dict[str, any]:
    """
    包装单个论文处理函数，用于批量处理
    返回包含处理结果的字典
    """
    pdf_file_obj = type('obj', (object,), {'name': pdf_path})()
    
    # 创建一个简单的进度对象（批量处理时不使用）
    class DummyProgress:
        def __call__(self, value, desc=""):
            pass
    
    try:
        result = process_paper(
            pdf_file=pdf_file_obj,
            api_key=api_key,
            api_base_url=api_base_url,
            model_name=model_name,
            output_format=output_format,
            poster_preset=poster_preset,
            poster_width=poster_width,
            poster_height=poster_height,
            temperature=temperature,
            save_json=save_json,
            enable_vision=enable_vision,
            vision_model=vision_model,
            template_choice=template_choice,
            max_images=max_images,
            min_image_size=min_image_size,
            abstract_max_words=abstract_max_words,
            output_language=output_language,
            check_overflow=check_overflow,
            max_iterations=max_iterations,
            progress=DummyProgress()
        )
        
        final_path, html_path, json_path, status = result
        
        return {
            'pdf_path': pdf_path,
            'pdf_name': Path(pdf_path).name,
            'success': final_path is not None,
            'final_path': final_path,
            'html_path': html_path,
            'json_path': json_path,
            'status': status,
            'error': None
        }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"处理 {pdf_path} 时出错: {error_msg}", exc_info=True)
        return {
            'pdf_path': pdf_path,
            'pdf_name': Path(pdf_path).name,
            'success': False,
            'final_path': None,
            'html_path': None,
            'json_path': None,
            'status': f"❌ 处理失败: {error_msg}",
            'error': error_msg
        }


def process_batch_papers(
    folder_path: str,
    api_key: str,
    api_base_url: str,
    model_name: str,
    output_format: str,
    poster_preset: str,
    poster_width: float,
    poster_height: float,
    temperature: float,
    save_json: bool,
    enable_vision: bool,
    vision_model: str,
    template_choice: str,
    max_images: int,
    min_image_size: int,
    abstract_max_words: int,
    output_language: str,
    check_overflow: bool,
    max_iterations: int,
    max_workers: int,
    progress=gr.Progress()
) -> str:
    """
    批量处理文件夹中的所有PDF文件
    
    Args:
        folder_path: 文件夹路径
        其他参数与 process_paper 相同
        max_workers: 最大并行任务数
    
    Returns:
        批量处理结果的状态信息
    """
    try:
        # 检查 API 密钥
        if not api_key or api_key.strip() == "":
            return "❌ 错误: 请输入 API 密钥"
        
        # 检查文件夹路径
        if not folder_path or not folder_path.strip():
            return "❌ 错误: 请输入文件夹路径"
        
        # 处理路径（去除首尾空格和引号）
        folder_path = folder_path.strip().strip('"').strip("'")
        
        # 检查文件夹是否存在
        if not os.path.exists(folder_path):
            return f"❌ 错误: 文件夹路径不存在: `{folder_path}`"
        
        if not os.path.isdir(folder_path):
            return f"❌ 错误: 路径不是文件夹: `{folder_path}`"
        
        # 扫描文件夹中的所有PDF文件
        folder = Path(folder_path)
        pdf_files = list(folder.glob("*.pdf"))
        
        if not pdf_files:
            return f"❌ 错误: 在文件夹 `{folder_path}` 中未找到 PDF 文件"
        
        logger.info("=" * 80)
        logger.info(f"批量处理: 找到 {len(pdf_files)} 个PDF文件")
        logger.info("=" * 80)
        
        total_files = len(pdf_files)
        completed = 0
        successful = 0
        failed = 0
        results: List[Dict] = []
        
        progress(0.0, desc=f"准备处理 {total_files} 个文件...")
        
        # 使用线程池并行处理
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_pdf = {
                executor.submit(
                    process_single_paper_wrapper,
                    str(pdf_path),
                    output_base_dir,
                    api_key,
                    api_base_url,
                    model_name,
                    output_format,
                    poster_preset,
                    poster_width,
                    poster_height,
                    temperature,
                    save_json,
                    enable_vision,
                    vision_model,
                    template_choice,
                    max_images,
                    min_image_size,
                    abstract_max_words,
                    output_language,
                    check_overflow,
                    max_iterations
                ): pdf_path
                for pdf_path in pdf_files
            }
            
            # 处理完成的任务
            for future in as_completed(future_to_pdf):
                pdf_path = future_to_pdf[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    completed += 1
                    if result['success']:
                        successful += 1
                    else:
                        failed += 1
                    
                    # 更新进度
                    progress_value = completed / total_files
                    progress(progress_value, desc=f"处理中: {completed}/{total_files} (成功: {successful}, 失败: {failed})")
                    logger.info(f"[{completed}/{total_files}] {'✅' if result['success'] else '❌'} {result['pdf_name']}")
                    
                except Exception as e:
                    error_msg = f"处理 {pdf_path.name} 时发生异常: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    results.append({
                        'pdf_path': str(pdf_path),
                        'pdf_name': pdf_path.name,
                        'success': False,
                        'final_path': None,
                        'html_path': None,
                        'json_path': None,
                        'status': f"❌ 异常: {str(e)}",
                        'error': str(e)
                    })
                    completed += 1
                    failed += 1
        
        # 生成结果报告
        progress(1.0, desc="批量处理完成")
        
        logger.info("=" * 80)
        logger.info(f"批量处理完成: 总计 {total_files}, 成功 {successful}, 失败 {failed}")
        logger.info("=" * 80)
        
        # 构建状态报告
        status_lines = [
            f"## 📊 批量处理结果",
            "",
            f"**总计**: {total_files} 个文件",
            f"**成功**: ✅ {successful} 个",
            f"**失败**: ❌ {failed} 个",
            "",
            "---",
            "",
            "### 📋 详细结果",
            ""
        ]
        
        for i, result in enumerate(results, 1):
            status_lines.append(f"#### {i}. {result['pdf_name']}")
            if result['success']:
                status_lines.append(f"✅ **成功**")
                if result['final_path']:
                    status_lines.append(f"- 海报: `{result['final_path']}`")
                if result['html_path']:
                    status_lines.append(f"- HTML: `{result['html_path']}`")
            else:
                status_lines.append(f"❌ **失败**: {result['error']}")
            status_lines.append("")
        
        status_lines.append("---")
        status_lines.append("")
        status_lines.append("💡 所有文件已保存到 `output` 目录，每个论文都有独立的子目录。")
        
        return "\n".join(status_lines)
        
    except Exception as e:
        error_msg = f"❌ 批量处理失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_msg


def create_ui():
    """创建 Gradio 界面"""
    
    # 自定义 CSS
    custom_css = """
    /* 使用系统字体，避免加载 Google Fonts */
    * {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji" !important;
    }
    
    .gradio-container {
        max-width: 1200px !important;
    }
    .output-image {
        max-height: 600px;
    }
    footer {
        display: none !important;
    }
    """
    
    with gr.Blocks(title="Paper2Poster-Web", css=custom_css) as demo:
        gr.Markdown("""
        # 📄 Paper2Poster-Web
        ### 自动将学术论文转换为精美海报
        
        上传 PDF 论文，AI 自动生成结构清晰、视觉美观的学术海报。支持 PDF 和 PNG 两种格式输出。
        """)
        
        # 预设选项（两个Tab共享）
        preset_choices = ["自动 (根据模板推荐)"] + [
            f"{k}: {v[2]}" for k, v in config.POSTER_PRESETS.items()
        ]
        
        # 使用Tabs分离单文件和批量处理
        with gr.Tabs() as tabs:
            # Tab 1: 单文件处理
            with gr.Tab("📄 单文件处理"):
                with gr.Row():
                    # 左侧 - 输入配置
                    with gr.Column(scale=1):
                        gr.Markdown("## 📤 上传论文")
                        pdf_input = gr.File(
                            label="选择 PDF 文件",
                            file_types=[".pdf"],
                            type="filepath"
                        )
                        
                        gr.Markdown("## ⚙️ API 配置")
                        
                        with gr.Group():
                            api_key = gr.Textbox(
                                label="API 密钥",
                                placeholder="sk-...",
                                type="password",
                                value=os.getenv("OPENAI_API_KEY", "")
                            )
                            
                            api_base_url = gr.Textbox(
                                label="API 基础 URL",
                                placeholder="https://api.openai.com/v1",
                                value=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
                            )
                            
                            model_name = gr.Textbox(
                                label="模型名称",
                                placeholder="gpt-4-turbo-preview",
                                value=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
                            )

                            # API 测试按钮和结果显示
                            with gr.Row():
                                test_api_btn = gr.Button("🔌 测试 API 连接", variant="secondary", size="sm")
                            test_result = gr.Textbox(
                                label="测试结果",
                                visible=True,
                                interactive=False,
                                lines=4,
                                show_copy_button=True
                            )
                        
                        gr.Markdown("## 🎨 海报设置")
                        
                        with gr.Group():
                            output_format = gr.Radio(
                                choices=["pdf", "png"],
                                value="png",
                                label="输出格式"
                            )
                            
                            # 尺寸预设选择
                            gr.Markdown("**💡 提示**: 学术会议模板推荐使用加长型尺寸以容纳更多内容")
                            
                            poster_preset = gr.Dropdown(
                                label="📐 尺寸预设",
                                choices=preset_choices,
                                value="自动 (根据模板推荐)",
                                info="选择预设尺寸或手动指定"
                            )
                            
                            with gr.Row():
                                poster_width = gr.Number(
                                    label="宽度 (像素) - 留空使用预设",
                                    value=None,
                                    precision=0,
                                    info="可手动覆盖"
                                )
                                poster_height = gr.Number(
                                    label="高度 (像素) - 留空使用预设",
                                    value=None,
                                    precision=0,
                                    info="可手动覆盖"
                                )
                            
                            temperature = gr.Slider(
                                minimum=0.0,
                                maximum=1.0,
                                value=config.TEMPERATURE,
                                step=0.1,
                                label="Temperature (创造性)",
                                info="越低越稳定，越高越有创造性"
                            )
                            
                            save_json = gr.Checkbox(
                                label="保存 JSON 数据",
                                value=False,
                                info="保存 LLM 生成的结构化数据"
                            )
                        
                        gr.Markdown("## 🎨 高级功能")
                        
                        with gr.Group():
                            enable_vision = gr.Checkbox(
                                label="启用视觉分析 (推荐)",
                                value=os.getenv("ENABLE_VISION_ANALYSIS", "false").lower() == "true",
                                info="使用视觉模型分析图片内容，智能放置到海报"
                            )
                            
                            vision_model = gr.Textbox(
                                label="视觉模型 (留空自动推荐)",
                                placeholder="例如: gpt-4o-mini 或 Qwen/Qwen2-VL-7B-Instruct",
                                value=os.getenv("VISION_MODEL", ""),
                                info="支持 GPT-4V, Qwen-VL 等视觉模型"
                            )
                            
                            template_choice = gr.Radio(
                                choices=[
                                    "经典三栏 (simple_grid)",
                                    "多图丰富 (multi_figure_grid)",
                                    "学术会议-纵向 (academic_panels)",
                                    "学术会议-横向16:9 (academic_panels_landscape) ⭐ 推荐"
                                ],
                                value="学术会议-横向16:9 (academic_panels_landscape) ⭐ 推荐",
                                label="海报模板",
                                info="选择不同风格的海报模板。横向16:9适合屏幕展示"
                            )
                            
                            max_images = gr.Slider(
                                minimum=5,
                                maximum=30,
                                value=15,
                                step=1,
                                label="最多分析图片数量",
                                info="包含图表和公式，更多图片需更长时间"
                            )
                            
                            min_image_size = gr.Slider(
                                minimum=50,
                                maximum=300,
                                value=100,
                                step=10,
                                label="最小图片尺寸 (像素)",
                                info="降低可提取更多公式，默认100px"
                            )
                            
                            abstract_max_words = gr.Slider(
                                minimum=80,
                                maximum=250,
                                value=130,
                                step=10,
                                label="📝 Abstract 最大字数",
                                info="LLM生成摘要时的字数限制，避免内容过长溢出（默认130字）"
                            )
                            
                            output_language = gr.Radio(
                                choices=[
                                    "自动检测 (Auto)",
                                    "中文 (Chinese)",
                                    "英文 (English)"
                                ],
                                value="中文 (Chinese)",
                                label="🌐 输出语言",
                                info="指定海报内容的语言。自动检测会根据论文原文语言输出"
                            )
                            
                            check_overflow = gr.Checkbox(
                                label="启用溢出检测和自动修复 ⭐",
                                value=False,
                                info="使用VLM检测内容截断并自动优化（需视觉模型）"
                            )
                            
                            max_iterations = gr.Slider(
                                minimum=1,
                                maximum=5,
                                value=3,
                                step=1,
                                label="最大优化次数",
                                info="溢出检测的迭代次数，默认3次",
                                visible=False
                            )
                            
                            # 当启用溢出检测时显示迭代次数
                            check_overflow.change(
                                fn=lambda x: gr.update(visible=x),
                                inputs=[check_overflow],
                                outputs=[max_iterations]
                            )
                
                    # 生成按钮
                    generate_btn = gr.Button(
                        "🚀 生成海报",
                        variant="primary",
                        size="lg"
                    )
                
                    # 右侧 - 状态信息
                    with gr.Column(scale=1):
                        gr.Markdown("## 📊 生成状态")
                        
                        status_output = gr.Markdown(
                            "请上传 PDF 文件并配置参数后点击生成。\n\n生成完成后将自动下载文件。",
                            elem_classes=["status-output"]
                        )
                        
                        # 隐藏的输出组件（用于后台处理）
                        poster_output = gr.File(
                            label="海报文件",
                            interactive=False,
                            visible=False
                        )
                        
                        html_output = gr.File(
                            label="HTML 文件",
                            interactive=False,
                            visible=False
                        )
                        
                        json_output = gr.File(
                            label="JSON 文件",
                            interactive=False,
                            visible=False
                        )
            
            # Tab 2: 批量处理
            with gr.Tab("📁 批量处理"):
                gr.Markdown("### 批量处理文件夹中的所有PDF文件")
                gr.Markdown("选择包含PDF文件的文件夹，系统会自动处理文件夹中的所有PDF文件。支持并行处理以提高效率。")
                
                with gr.Row():
                    # 左侧 - 配置
                    with gr.Column(scale=1):
                        gr.Markdown("## 📁 选择文件夹")
                        folder_input = gr.Textbox(
                            label="文件夹路径",
                            placeholder="例如: /home/user/papers 或 C:\\Users\\Name\\papers",
                            info="输入包含PDF文件的文件夹路径。系统会自动扫描该文件夹中的所有PDF文件并批量处理。"
                        )
                        gr.Markdown("**💡 提示**: 请确保文件夹路径正确，且文件夹中包含PDF文件。支持绝对路径和相对路径。")
                        
                        gr.Markdown("## ⚙️ 并行设置")
                        max_workers = gr.Slider(
                            minimum=1,
                            maximum=10,
                            value=3,
                            step=1,
                            label="并行任务数",
                            info="同时处理的文件数量，建议根据API限制和系统性能调整"
                        )
                        
                        gr.Markdown("## 🎨 批量处理配置")
                        gr.Markdown("批量处理将使用以下配置处理所有文件。配置说明请参考单文件处理Tab。")
                        
                        # 批量处理的配置组件（与单文件处理共享参数）
                        batch_api_key = gr.Textbox(
                            label="API 密钥",
                            placeholder="sk-...",
                            type="password",
                            value=os.getenv("OPENAI_API_KEY", "")
                        )
                        
                        batch_api_base_url = gr.Textbox(
                            label="API 基础 URL",
                            placeholder="https://api.openai.com/v1",
                            value=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
                        )
                        
                        batch_model_name = gr.Textbox(
                            label="模型名称",
                            placeholder="gpt-4-turbo-preview",
                            value=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
                        )
                        
                        batch_output_format = gr.Radio(
                            choices=["pdf", "png"],
                            value="png",
                            label="输出格式"
                        )
                        
                        batch_poster_preset = gr.Dropdown(
                            label="📐 尺寸预设",
                            choices=preset_choices,
                            value="自动 (根据模板推荐)",
                            info="选择预设尺寸或手动指定"
                        )
                        
                        with gr.Row():
                            batch_poster_width = gr.Number(
                                label="宽度 (像素)",
                                value=None,
                                precision=0
                            )
                            batch_poster_height = gr.Number(
                                label="高度 (像素)",
                                value=None,
                                precision=0
                            )
                        
                        batch_temperature = gr.Slider(
                            minimum=0.0,
                            maximum=1.0,
                            value=config.TEMPERATURE,
                            step=0.1,
                            label="Temperature (创造性)"
                        )
                        
                        batch_save_json = gr.Checkbox(
                            label="保存 JSON 数据",
                            value=False
                        )
                        
                        batch_enable_vision = gr.Checkbox(
                            label="启用视觉分析",
                            value=os.getenv("ENABLE_VISION_ANALYSIS", "false").lower() == "true"
                        )
                        
                        batch_vision_model = gr.Textbox(
                            label="视觉模型",
                            placeholder="例如: gpt-4o-mini",
                            value=os.getenv("VISION_MODEL", "")
                        )
                        
                        batch_template_choice = gr.Radio(
                            choices=[
                                "经典三栏 (simple_grid)",
                                "多图丰富 (multi_figure_grid)",
                                "学术会议-纵向 (academic_panels)",
                                "学术会议-横向16:9 (academic_panels_landscape) ⭐ 推荐"
                            ],
                            value="学术会议-横向16:9 (academic_panels_landscape) ⭐ 推荐",
                            label="海报模板"
                        )
                        
                        batch_max_images = gr.Slider(
                            minimum=5,
                            maximum=30,
                            value=15,
                            step=1,
                            label="最多分析图片数量"
                        )
                        
                        batch_min_image_size = gr.Slider(
                            minimum=50,
                            maximum=300,
                            value=100,
                            step=10,
                            label="最小图片尺寸 (像素)"
                        )
                        
                        batch_abstract_max_words = gr.Slider(
                            minimum=80,
                            maximum=250,
                            value=130,
                            step=10,
                            label="Abstract 最大字数"
                        )
                        
                        batch_output_language = gr.Radio(
                            choices=[
                                "自动检测 (Auto)",
                                "中文 (Chinese)",
                                "英文 (English)"
                            ],
                            value="中文 (Chinese)",
                            label="🌐 输出语言"
                        )
                        
                        batch_check_overflow = gr.Checkbox(
                            label="启用溢出检测和自动修复",
                            value=False
                        )
                        
                        batch_max_iterations = gr.Slider(
                            minimum=1,
                            maximum=5,
                            value=3,
                            step=1,
                            label="最大优化次数",
                            visible=False
                        )
                        
                        batch_check_overflow.change(
                            fn=lambda x: gr.update(visible=x),
                            inputs=[batch_check_overflow],
                            outputs=[batch_max_iterations]
                        )
                        
                        # 批量处理按钮
                        batch_generate_btn = gr.Button(
                            "🚀 开始批量处理",
                            variant="primary",
                            size="lg"
                        )
                    
                    # 右侧 - 批量处理状态
                    with gr.Column(scale=1):
                        gr.Markdown("## 📊 批量处理状态")
                        
                        batch_status_output = gr.Markdown(
                            "请选择文件夹并配置参数后点击开始批量处理。\n\n处理过程中会显示实时进度和结果。",
                            elem_classes=["status-output"]
                        )
        
        # 说明文档
        with gr.Accordion("📖 使用说明", open=False):
            gr.Markdown("""
            ### 使用步骤:
            
            1. **上传 PDF**: 选择你的学术论文 PDF 文件
            2. **配置 API**: 填写你的 LLM API 密钥和配置
               - 支持 OpenAI、DeepSeek、Azure 等兼容 OpenAI API 的服务
               - 推荐使用 GPT-4 或 DeepSeek-Chat 以获得最佳效果
            3. **设置海报**: 选择输出格式和尺寸
               - PDF 格式适合打印
               - PNG 格式适合在线展示
               - 默认 1600x1200 适合大多数场景
            4. **点击生成**: 等待 AI 处理（通常需要 30-60 秒）
            5. **下载结果**: 生成完成后下载海报文件
            
            ### 常用 API 配置:
            
            **OpenAI GPT-4:**
            - API URL: `https://api.openai.com/v1`
            - 模型: `gpt-4-turbo-preview` 或 `gpt-4`
            
            **DeepSeek (更便宜):**
            - API URL: `https://api.deepseek.com/v1`
            - 模型: `deepseek-chat`
            
            ### 注意事项:
            
            - 确保 PDF 文本可复制（不是扫描件）
            - 处理时间取决于论文长度和 API 响应速度
            - 建议先用较小的论文测试
            - 如遇错误，请检查 API 密钥和网络连接
            """)
        
        with gr.Accordion("🎨 模板说明", open=False):
            gr.Markdown("""
            ### 📋 可用模板
            
            **1. 经典三栏 (simple_grid)**
            - 简洁清晰的三栏布局
            - 单张主图展示
            - 适合图片较少的论文
            - 快速预览推荐
            
            **2. 多图丰富 (multi_figure_grid)** ⭐
            - 显示最多6张图片
            - 智能图片放置
            - 内容丰富饱满
            - 日常使用推荐
            - **需要启用视觉分析**
            
            **3. 学术会议 (academic_panels)** ⭐⭐⭐
            - 学术会议海报风格
            - 9个独立面板布局
            - 灵活的面板尺寸
            - 最高空间利用率（95%）
            - 专业视觉效果
            - **需要启用视觉分析**
            - 借鉴 Paper2Poster 项目设计
            
            ### 💡 选择建议
            
            - **快速测试**: 选择"经典三栏"
            - **日常使用**: 选择"多图丰富"
            - **学术会议**: 选择"学术会议" (最专业)
            
            ### 📖 详细指南
            
            查看 [TEMPLATES_GUIDE.md](https://github.com) 了解：
            - 各模板详细对比
            - 自定义模板教程
            - 高级技巧
            
            ### 模板数据结构
            
            模板可访问以下数据：
            - `poster.title` - 标题
            - `poster.authors` - 作者
            - `poster.affiliation` - 机构
            - `poster.abstract` - 摘要
            - `poster.introduction` - 引言 {title, content}
            - `poster.methods` - 方法 {title, content}
            - `poster.results` - 结果 {title, content}
            - `poster.conclusion` - 结论 {title, content}
            - `poster.main_figure_path` - 主图
            - `poster.references` - 参考文献列表
            """)
        
        # 事件绑定
        # API 测试按钮点击事件
        test_api_btn.click(
            fn=test_api_connection,
            inputs=[api_key, api_base_url, model_name],
            outputs=[test_result]
        )

        def update_json_visibility(save):
            return gr.update(visible=save)
        
        save_json.change(
            fn=update_json_visibility,
            inputs=[save_json],
            outputs=[json_output]
        )
        
        generate_btn.click(
            fn=process_paper,
            inputs=[
                pdf_input,
                api_key,
                api_base_url,
                model_name,
                output_format,
                poster_preset,
                poster_width,
                poster_height,
                temperature,
                save_json,
                enable_vision,
                vision_model,
                template_choice,
                max_images,
                min_image_size,
                abstract_max_words,
                output_language,
                check_overflow,
                max_iterations
            ],
            outputs=[
                poster_output,
                html_output,
                json_output,
                status_output
            ]
        )
        
        # 批量处理按钮事件绑定
        batch_generate_btn.click(
            fn=process_batch_papers,
            inputs=[
                folder_input,
                batch_api_key,
                batch_api_base_url,
                batch_model_name,
                batch_output_format,
                batch_poster_preset,
                batch_poster_width,
                batch_poster_height,
                batch_temperature,
                batch_save_json,
                batch_enable_vision,
                batch_vision_model,
                batch_template_choice,
                batch_max_images,
                batch_min_image_size,
                batch_abstract_max_words,
                batch_output_language,
                batch_check_overflow,
                batch_max_iterations,
                max_workers
            ],
            outputs=[
                batch_status_output
            ]
        )
        
        # 页脚
        gr.Markdown("""
        ---
        <div style="text-align: center; color: #666; font-size: 0.9em;">
            Paper2Poster-Web v1.0.0 | 
            <a href="https://github.com" target="_blank">GitHub</a> | 
            基于 PyMuPDF + OpenAI + Playwright 构建
        </div>
        """)
    
    return demo


def main():
    """启动 Web UI"""
    logger.info("启动 Gradio Web UI...")
    
    # 创建界面
    demo = create_ui()
    
    # 启动服务器
    demo.launch(
        server_name="0.0.0.0",  # 允许外部访问
        server_port=7860,
        share=False,  # 设为 True 可生成公网链接
        show_error=True,
        favicon_path=None
    )


if __name__ == "__main__":
    main()

