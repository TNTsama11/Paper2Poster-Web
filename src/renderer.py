"""
排版印刷厂 (The Renderer)
负责 HTML 模板渲染和导出为 PDF/PNG
"""
import asyncio
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright
import markdown

from .models import PosterContent
from .logger import setup_logger
from .overflow_detector import OverflowDetector
from .content_compressor import ContentCompressor

logger = setup_logger("Renderer")


class PosterRenderer:
    """海报渲染器 - 将结构化数据渲染为 HTML 并导出"""
    
    def __init__(
        self, 
        templates_dir: Path,
        output_dir: Path,
        poster_width: int = 1600,
        poster_height: int = 1200
    ):
        """
        初始化渲染器
        
        Args:
            templates_dir: 模板目录
            output_dir: 输出目录
            poster_width: 海报宽度（像素）
            poster_height: 海报高度（像素）
        """
        self.templates_dir = Path(templates_dir)
        self.output_dir = Path(output_dir)
        self.poster_width = poster_width
        self.poster_height = poster_height
        
        # 设置 Jinja2 环境
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True
        )
        
        # 添加 Markdown 过滤器
        self.env.filters['markdown'] = lambda text: markdown.markdown(
            text, 
            extensions=['nl2br']  # 支持换行
        )
        
        logger.info("渲染器初始化完成")
        logger.info(f"  - 模板目录: {self.templates_dir}")
        logger.info(f"  - 海报尺寸: {self.poster_width}x{self.poster_height}")
    
    def render_html(
        self, 
        poster_content: PosterContent, 
        template_name: str = "simple_grid.html"
    ) -> str:
        """
        渲染 HTML
        
        Args:
            poster_content: 海报内容对象
            template_name: 模板文件名
            
        Returns:
            渲染后的 HTML 路径
        """
        logger.info("=" * 60)
        logger.info("开始渲染 HTML")
        logger.info("=" * 60)
        
        try:
            # 加载模板
            template = self.env.get_template(template_name)
            
            # 渲染模板
            html_content = template.render(
                poster=poster_content.to_dict(),
                width=self.poster_width,
                height=self.poster_height
            )
            
            # 保存 HTML
            html_path = self.output_dir / "poster.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            # 复制本地 CSS 和 JS 文件到输出目录（如果存在）
            local_css = self.templates_dir / "css2.css"
            local_js = self.templates_dir / "tailwindcss3.4.17.es"
            
            if local_css.exists():
                shutil.copy2(local_css, self.output_dir / "css2.css")
                logger.info(f"已复制本地 CSS 文件: {local_css.name}")
            
            if local_js.exists():
                shutil.copy2(local_js, self.output_dir / "tailwindcss3.4.17.es")
                logger.info(f"已复制本地 TailwindCSS 文件: {local_js.name}")
            
            logger.info(f"HTML 渲染完成: {html_path}")
            logger.info("=" * 60)
            
            return str(html_path)
            
        except Exception as e:
            logger.error(f"HTML 渲染失败: {e}")
            raise
    
    async def export_to_pdf(
        self, 
        html_path: str, 
        output_filename: str = "final_poster.pdf"
    ) -> str:
        """
        使用 Playwright 将 HTML 导出为 PDF
        
        Args:
            html_path: HTML 文件路径
            output_filename: 输出文件名
            
        Returns:
            PDF 文件路径
        """
        logger.info("开始导出 PDF")
        
        pdf_path = self.output_dir / output_filename
        html_path_abs = Path(html_path).absolute()
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page(
                    viewport={
                        'width': self.poster_width,
                        'height': self.poster_height
                    }
                )
                
                # 加载 HTML（增加超时到 120 秒，只等待 DOM 加载）
                await page.goto(
                    f"file://{html_path_abs}", 
                    timeout=120000,  # 120 秒
                    wait_until="domcontentloaded"  # 只等待 DOM，不等待所有资源
                )
                
                # 等待 TailwindCSS 和图片完成渲染（固定等待 10 秒）
                await page.wait_for_timeout(100000)
                
                # 导出 PDF
                await page.pdf(
                    path=str(pdf_path),
                    width=f"{self.poster_width}px",
                    height=f"{self.poster_height}px",
                    print_background=True
                )
                
                await browser.close()
            
            logger.info(f"PDF 导出完成: {pdf_path}")
            return str(pdf_path)
            
        except Exception as e:
            logger.error(f"PDF 导出失败: {e}")
            raise
    
    async def export_to_png(
        self, 
        html_path: str, 
        output_filename: str = "final_poster.png"
    ) -> str:
        """
        使用 Playwright 将 HTML 导出为 PNG
        
        Args:
            html_path: HTML 文件路径
            output_filename: 输出文件名
            
        Returns:
            PNG 文件路径
        """
        logger.info("开始导出 PNG")
        
        png_path = self.output_dir / output_filename
        html_path_abs = Path(html_path).absolute()
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page(
                    viewport={
                        'width': self.poster_width,
                        'height': self.poster_height
                    }
                )
                
                # 加载 HTML（增加超时到 120 秒，只等待 DOM 加载）
                await page.goto(
                    f"file://{html_path_abs}", 
                    timeout=120000,  # 120 秒
                    wait_until="domcontentloaded"  # 只等待 DOM，不等待所有资源
                )
                
                # 等待 TailwindCSS 和图片完成渲染（固定等待 10 秒）
                await page.wait_for_timeout(100000)
                
                # 导出截图
                await page.screenshot(
                    path=str(png_path),
                    full_page=True
                )
                
                await browser.close()
            
            logger.info(f"PNG 导出完成: {png_path}")
            return str(png_path)
            
        except Exception as e:
            logger.error(f"PNG 导出失败: {e}")
            raise
    
    def render(
        self, 
        poster_content: PosterContent,
        export_format: str = "pdf",
        template_name: str = "simple_grid.html"
    ) -> str:
        """
        执行完整的渲染流程
        
        Args:
            poster_content: 海报内容对象
            export_format: 导出格式 ('pdf' 或 'png')
            template_name: 模板文件名
            
        Returns:
            最终文件路径
        """
        logger.info("=" * 60)
        logger.info("开始渲染流程")
        logger.info("=" * 60)
        
        # 渲染 HTML
        html_path = self.render_html(poster_content, template_name)
        
        # 导出
        if export_format.lower() == "pdf":
            result = asyncio.run(self.export_to_pdf(html_path))
        elif export_format.lower() == "png":
            result = asyncio.run(self.export_to_png(html_path))
        else:
            raise ValueError(f"不支持的导出格式: {export_format}")
        
        logger.info("=" * 60)
        logger.info(f"渲染完成: {result}")
        logger.info("=" * 60)
        
        return result
    
    def render_with_overflow_check(
        self,
        poster_content: PosterContent,
        export_format: str = "pdf",
        template_name: str = "simple_grid.html",
        overflow_detector: OverflowDetector = None,
        content_compressor: ContentCompressor = None,
        max_iterations: int = 3,
        quality_threshold: float = 8.0
    ) -> str:
        """
        带溢出检测的渲染流程（多轮优化）
        
        Args:
            poster_content: 海报内容对象
            export_format: 导出格式
            template_name: 模板文件名
            overflow_detector: 溢出检测器（可选）
            content_compressor: 内容压缩器（可选）
            max_iterations: 最大迭代次数
            quality_threshold: 质量阈值（0-10分）
            
        Returns:
            最终文件路径
        """
        logger.info("=" * 80)
        logger.info("🔄 带溢出检测的渲染流程")
        logger.info("=" * 80)
        
        if overflow_detector is None or not overflow_detector.enabled:
            logger.info("溢出检测未启用，使用标准渲染")
            return self.render(poster_content, export_format, template_name)
        
        if content_compressor is None:
            content_compressor = ContentCompressor()
        
        current_content = poster_content
        best_result = None
        best_quality = 0
        
        for iteration in range(1, max_iterations + 1):
            logger.info("=" * 80)
            logger.info(f"🔄 迭代 {iteration}/{max_iterations}")
            logger.info("=" * 80)
            
            # 1. 渲染 HTML
            html_path = self.render_html(current_content, template_name)
            
            # 2. 检测溢出
            detection_result = overflow_detector.detect_overflow(Path(html_path))
            
            quality = detection_result.get("overall_quality", 0)
            logger.info(f"📊 当前质量: {quality}/10")
            
            # 3. 记录最佳结果
            if quality > best_quality:
                best_quality = quality
                best_result = html_path
                logger.info(f"✨ 新的最佳结果！质量: {quality}/10")
            
            # 4. 判断是否满足要求
            if quality >= quality_threshold:
                logger.info(f"✅ 达到质量阈值 ({quality_threshold})，停止优化")
                break
            
            if not overflow_detector.should_fix(detection_result, threshold="moderate"):
                logger.info("✅ 无需修复，停止优化")
                break
            
            # 5. 最后一次迭代不再压缩
            if iteration == max_iterations:
                logger.warning("⚠️ 达到最大迭代次数，停止优化")
                break
            
            # 6. 生成修复建议
            suggestions = overflow_detector.generate_fix_suggestions(detection_result)
            
            # 7. 压缩内容
            logger.info(f"🔧 根据建议调整内容 (迭代 {iteration+1})")
            current_content = content_compressor.compress_content(
                current_content.copy(deep=True),
                suggestions
            )
        
        # 使用最佳结果导出
        logger.info("=" * 80)
        logger.info(f"🎯 使用最佳结果 (质量: {best_quality}/10)")
        logger.info("=" * 80)
        
        html_path = best_result or html_path
        
        # 导出最终格式
        if export_format.lower() == "pdf":
            result = asyncio.run(self.export_to_pdf(html_path))
        elif export_format.lower() == "png":
            result = asyncio.run(self.export_to_png(html_path))
        elif export_format.lower() == "html":
            result = html_path
        else:
            raise ValueError(f"不支持的导出格式: {export_format}")
        
        logger.info("=" * 80)
        logger.info(f"✅ 渲染完成: {result}")
        logger.info(f"📊 最终质量: {best_quality}/10")
        logger.info("=" * 80)
        
        return result

