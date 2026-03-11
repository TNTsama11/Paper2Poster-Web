"""
素材收割机 (The Harvester)
负责从 PDF 中提取文本、图片和公式
"""
import fitz  # PyMuPDF
from pathlib import Path
from typing import Tuple, List, Dict
from PIL import Image
import io
import re

from .logger import setup_logger

logger = setup_logger("Harvester")


class PDFHarvester:
    """PDF 解析和资源提取器"""
    
    def __init__(self, pdf_path: str, output_dir: Path, min_width: int = 100, min_height: int = 100):
        """
        初始化 PDF 收割机
        
        Args:
            pdf_path: PDF 文件路径
            output_dir: 输出目录
            min_width: 最小图片宽度（降低以包含公式）
            min_height: 最小图片高度（降低以包含公式）
        """
        self.pdf_path = Path(pdf_path)
        self.output_dir = Path(output_dir)
        self.min_width = min_width
        self.min_height = min_height
        self.images_dir = self.output_dir / "images"
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF 文件不存在: {self.pdf_path}")
    
    def extract_text(self) -> str:
        """
        提取 PDF 中的所有文本
        
        Returns:
            清洗后的全文文本
        """
        logger.info(f"开始提取 PDF 文本: {self.pdf_path}")
        
        try:
            doc = fitz.open(self.pdf_path)
            full_text = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                # 简单清洗：去除过短的行（可能是页眉页脚）
                lines = text.split('\n')
                cleaned_lines = [
                    line.strip() 
                    for line in lines 
                    if len(line.strip()) > 3  # 忽略太短的行
                ]
                
                full_text.extend(cleaned_lines)
            
            doc.close()
            
            result = '\n'.join(full_text)
            logger.info(f"文本提取完成，共 {len(result)} 字符")
            
            return result
            
        except Exception as e:
            logger.error(f"文本提取失败: {e}")
            raise
    
    def extract_images(self) -> List[str]:
        """
        提取 PDF 中的所有图片
        
        Returns:
            提取的图片文件名列表
        """
        logger.info(f"开始提取 PDF 图片: {self.pdf_path}")
        
        try:
            doc = fitz.open(self.pdf_path)
            image_list = []
            image_counter = 1
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_info_list = page.get_images()
                
                for img_index, img_info in enumerate(image_info_list):
                    xref = img_info[0]
                    
                    try:
                        # 提取图片
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]
                        
                        # 使用 PIL 检查图片尺寸
                        image = Image.open(io.BytesIO(image_bytes))
                        width, height = image.size
                        
                        # 过滤过小的图片（通常是图标、logo等）
                        # 放宽限制以包含公式图片
                        if width < self.min_width or height < self.min_height:
                            logger.debug(f"跳过小图片 ({width}x{height})")
                            continue
                        
                        # 过滤过大的图片（可能是全页扫描）
                        if width > 3000 or height > 3000:
                            logger.debug(f"跳过过大图片 ({width}x{height})")
                            continue
                        
                        # 保存图片
                        image_filename = f"img_{image_counter:02d}.{image_ext}"
                        image_path = self.images_dir / image_filename
                        
                        with open(image_path, "wb") as img_file:
                            img_file.write(image_bytes)
                        
                        image_list.append(image_filename)
                        logger.info(f"提取图片: {image_filename} ({width}x{height})")
                        
                        image_counter += 1
                        
                    except Exception as e:
                        logger.warning(f"提取图片失败 (xref={xref}): {e}")
                        continue
            
            doc.close()
            
            logger.info(f"图片提取完成，共 {len(image_list)} 张")
            return image_list
            
        except Exception as e:
            logger.error(f"图片提取失败: {e}")
            raise
    
    def extract_equations(self, text: str) -> List[Dict[str, str]]:
        """
        从文本中提取公式
        
        Args:
            text: 论文全文
            
        Returns:
            公式列表，每个公式包含 {type, content, context}
        """
        logger.info("开始提取文本公式...")
        
        equations = []
        
        # 模式1: 行内公式 $...$
        inline_pattern = r'\$([^\$]+)\$'
        inline_matches = re.finditer(inline_pattern, text)
        for match in inline_matches:
            formula = match.group(1).strip()
            if len(formula) > 3:  # 过滤太短的（可能是金额）
                equations.append({
                    'type': 'inline',
                    'content': formula,
                    'context': text[max(0, match.start()-50):match.end()+50]
                })
        
        # 模式2: 行间公式 $$...$$
        display_pattern = r'\$\$([^\$]+)\$\$'
        display_matches = re.finditer(display_pattern, text)
        for match in display_matches:
            formula = match.group(1).strip()
            equations.append({
                'type': 'display',
                'content': formula,
                'context': text[max(0, match.start()-50):match.end()+50]
            })
        
        # 模式3: LaTeX equation 环境
        equation_pattern = r'\\begin\{equation\}(.*?)\\end\{equation\}'
        equation_matches = re.finditer(equation_pattern, text, re.DOTALL)
        for match in equation_matches:
            formula = match.group(1).strip()
            equations.append({
                'type': 'equation',
                'content': formula,
                'context': text[max(0, match.start()-50):match.end()+50]
            })
        
        # 模式4: 常见数学符号密集的行（启发式识别）
        math_symbols = r'[∑∏∫∂∇≈≠≤≥±×÷√∞∈∉⊂⊃∪∩α-ωΑ-Ω]'
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if len(re.findall(math_symbols, line)) >= 3:  # 至少3个数学符号
                equations.append({
                    'type': 'symbolic',
                    'content': line.strip(),
                    'context': '\n'.join(lines[max(0,i-2):i+3])
                })
        
        # 去重
        seen = set()
        unique_equations = []
        for eq in equations:
            content_key = eq['content'][:100]  # 使用前100字符作为key
            if content_key not in seen and len(eq['content']) > 5:
                seen.add(content_key)
                unique_equations.append(eq)
        
        logger.info(f"提取到 {len(unique_equations)} 个公式")
        return unique_equations[:20]  # 最多返回20个最重要的公式
    
    def harvest(self) -> Tuple[str, List[str], List[Dict[str, str]]]:
        """
        执行完整的收割流程
        
        Returns:
            (全文文本, 图片文件名列表, 公式列表)
        """
        logger.info("=" * 60)
        logger.info("开始素材收割")
        logger.info("=" * 60)
        
        text = self.extract_text()
        images = self.extract_images()
        equations = self.extract_equations(text)
        
        logger.info("=" * 60)
        logger.info(f"素材收割完成: {len(text)} 字符文本, {len(images)} 张图片, {len(equations)} 个公式")
        logger.info("=" * 60)
        
        return text, images, equations

