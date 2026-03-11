#!/usr/bin/env python3
"""
Paper2Poster-Web (P2P-Web) 主程序
将学术论文 PDF 自动转换为学术海报
"""
import sys
import argparse
from pathlib import Path
from datetime import datetime
import shutil
import json

# 导入配置
import config

# 导入核心模块
from src.harvester import PDFHarvester
from src.editor import LLMEditor
from src.renderer import PosterRenderer
from src.logger import setup_logger

logger = setup_logger("Main")


def backup_file(file_path: Path, backup_dir: Path):
    """备份文件"""
    if not file_path.exists():
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
    backup_path = backup_dir / backup_name
    
    shutil.copy2(file_path, backup_path)
    logger.info(f"已备份文件: {backup_path}")


def main():
    """主流程"""
    parser = argparse.ArgumentParser(
        description="Paper2Poster-Web: 将学术论文 PDF 自动转换为学术海报"
    )
    parser.add_argument(
        "pdf_path",
        type=str,
        help="输入的 PDF 文件路径"
    )
    parser.add_argument(
        "-f", "--format",
        type=str,
        default="pdf",
        choices=["pdf", "png"],
        help="输出格式 (默认: pdf)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="输出文件名（不含扩展名，默认: final_poster）"
    )
    parser.add_argument(
        "-t", "--template",
        type=str,
        default="simple_grid.html",
        help="HTML 模板文件名 (默认: simple_grid.html)"
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="不备份已存在的输出文件"
    )
    parser.add_argument(
        "--save-json",
        action="store_true",
        help="保存 LLM 生成的 JSON 数据"
    )
    parser.add_argument(
        "--enable-vision",
        action="store_true",
        help="启用视觉模型分析图片（需要支持vision的模型）"
    )
    parser.add_argument(
        "--vision-model",
        type=str,
        default=None,
        help="指定视觉模型（如 gpt-4o-mini, Qwen/Qwen2-VL-7B-Instruct）"
    )
    parser.add_argument(
        "--max-images",
        type=int,
        default=15,
        help="最多分析的图片数量（默认15张，包含图表和公式）"
    )
    parser.add_argument(
        "--min-image-size",
        type=int,
        default=100,
        help="最小图片尺寸（默认100px，降低可提取更多公式）"
    )
    parser.add_argument(
        "--check-overflow",
        action="store_true",
        help="启用内容溢出检测和自动修复（需要vision模型）"
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=3,
        help="溢出修复的最大迭代次数（默认3次）"
    )
    parser.add_argument(
        "--quality-threshold",
        type=float,
        default=8.0,
        help="质量阈值，达到后停止优化（0-10分，默认8.0）"
    )
    parser.add_argument(
        "--width",
        type=int,
        help="海报宽度 (像素，默认根据模板自动选择)"
    )
    parser.add_argument(
        "--height",
        type=int,
        help="海报高度 (像素，默认根据模板自动选择)"
    )
    parser.add_argument(
        "--preset",
        type=str,
        choices=list(config.POSTER_PRESETS.keys()),
        help=f'海报尺寸预设 (如: a0_portrait, 36x48, extended)'
    )
    
    args = parser.parse_args()
    
    # 检查 PDF 文件
    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        logger.error(f"PDF 文件不存在: {pdf_path}")
        sys.exit(1)
    
    # 检查 API 密钥
    if not config.OPENAI_API_KEY:
        logger.error("错误: 未设置 OPENAI_API_KEY")
        logger.error("请在 .env 文件中设置您的 API 密钥")
        sys.exit(1)
    
    # ============================================
    # 确定海报尺寸（优先级：命令行 > 预设 > 模板推荐 > 默认）
    # ============================================
    poster_width = args.width
    poster_height = args.height
    
    if args.preset:
        # 使用预设尺寸
        preset = config.POSTER_PRESETS.get(args.preset)
        if preset:
            poster_width = poster_width or preset[0]
            poster_height = poster_height or preset[1]
            logger.info(f"📐 使用预设尺寸: {args.preset} ({preset[2]})")
    
    if not poster_width or not poster_height:
        # 根据模板推荐尺寸
        template_name = args.template
        recommended_preset = config.TEMPLATE_RECOMMENDED_SIZES.get(template_name, "default")
        preset = config.POSTER_PRESETS[recommended_preset]
        poster_width = poster_width or preset[0]
        poster_height = poster_height or preset[1]
        logger.info(f"📐 模板推荐尺寸: {template_name} → {recommended_preset} ({preset[2]})")
    
    logger.info(f"📐 最终海报尺寸: {poster_width}×{poster_height} 像素")
    
    # 设置输出文件名
    output_name = args.output or "final_poster"
    output_filename = f"{output_name}.{args.format}"
    
    # 备份已存在的文件
    if not args.no_backup:
        output_path = config.OUTPUT_DIR / output_filename
        backup_file(output_path, config.BACKUPS_DIR)
        
        html_path = config.OUTPUT_DIR / "poster.html"
        backup_file(html_path, config.BACKUPS_DIR)
    
    try:
        logger.info("=" * 80)
        logger.info("Paper2Poster-Web 启动")
        logger.info("=" * 80)
        logger.info(f"输入文件: {pdf_path}")
        logger.info(f"输出格式: {args.format}")
        logger.info(f"输出文件: {output_filename}")
        logger.info("=" * 80)
        
        # ============================================
        # 模块 1: 素材收割机 (The Harvester)
        # ============================================
        harvester = PDFHarvester(
            pdf_path=pdf_path,
            output_dir=config.OUTPUT_DIR,
            min_width=args.min_image_size,
            min_height=args.min_image_size
        )
        
        full_text, image_manifest, equations = harvester.harvest()
        
        # ============================================
        # 模块 2: 智能编辑部 (The Editor)
        # ============================================
        editor = LLMEditor(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL,
            model=config.OPENAI_MODEL,
            max_tokens=config.MAX_TOKENS,
            temperature=config.TEMPERATURE,
            enable_vision=args.enable_vision or config.ENABLE_VISION_ANALYSIS,
            vision_model=args.vision_model or config.VISION_MODEL,
            images_dir=config.IMAGES_DIR
        )
        
        poster_content = editor.edit(full_text, image_manifest, max_images=args.max_images, equations=equations)
        
        # 保存 JSON（如果需要）
        if args.save_json:
            json_path = config.OUTPUT_DIR / "poster_content.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(poster_content.to_dict(), f, ensure_ascii=False, indent=2)
            logger.info(f"JSON 数据已保存: {json_path}")
        
        # ============================================
        # 模块 3: 排版印刷厂 (The Renderer)
        # ============================================
        renderer = PosterRenderer(
            templates_dir=config.TEMPLATES_DIR,
            output_dir=config.OUTPUT_DIR,
            poster_width=poster_width,
            poster_height=poster_height
        )
        
        # 如果启用溢出检测
        if args.check_overflow:
            logger.info("🔄 启用溢出检测和自动修复")
            
            # 初始化溢出检测器和内容压缩器
            from openai import OpenAI
            from src.overflow_detector import OverflowDetector
            from src.content_compressor import ContentCompressor
            
            vision_client = OpenAI(
                api_key=config.OPENAI_API_KEY,
                base_url=config.OPENAI_BASE_URL
            )
            
            overflow_detector = OverflowDetector(
                vision_client=vision_client,
                vision_model=args.vision_model or config.VISION_MODEL or "gpt-4o-mini",
                enabled=True
            )
            
            content_compressor = ContentCompressor(
                llm_client=vision_client,
                model=config.OPENAI_MODEL
            )
            
            final_path = renderer.render_with_overflow_check(
                poster_content=poster_content,
                export_format=args.format,
                template_name=args.template,
                overflow_detector=overflow_detector,
                content_compressor=content_compressor,
                max_iterations=args.max_iterations,
                quality_threshold=args.quality_threshold
            )
        else:
            # 标准渲染
            final_path = renderer.render(
                poster_content=poster_content,
                export_format=args.format,
                template_name=args.template
            )
        
        # ============================================
        # 完成
        # ============================================
        logger.info("=" * 80)
        logger.info("✅ Paper2Poster-Web 完成!")
        logger.info(f"📄 最终海报: {final_path}")
        logger.info("=" * 80)
        
    except KeyboardInterrupt:
        logger.warning("\n用户中断程序")
        sys.exit(1)
    except Exception as e:
        logger.error(f"程序执行失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

