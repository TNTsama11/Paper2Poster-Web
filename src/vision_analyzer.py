"""
视觉分析器 (Vision Analyzer)
使用视觉模型分析图片内容，智能分类和描述
"""
import base64
from pathlib import Path
from typing import List, Dict, Optional
from openai import OpenAI
import json

from .logger import setup_logger
from .models import Figure

logger = setup_logger("VisionAnalyzer")


class VisionAnalyzer:
    """视觉模型分析器 - 分析图片内容和类型"""
    
    # 支持的视觉模型列表
    VISION_MODELS = {
        # OpenAI
        "gpt-4-vision-preview": "OpenAI GPT-4 Vision",
        "gpt-4-turbo": "OpenAI GPT-4 Turbo (with vision)",
        "gpt-4o": "OpenAI GPT-4o",
        "gpt-4o-mini": "OpenAI GPT-4o Mini",
        
        # SiliconFlow
        "Pro/Qwen/Qwen2-VL-72B-Instruct": "Qwen2-VL-72B (SiliconFlow)",
        "Qwen/Qwen2-VL-7B-Instruct": "Qwen2-VL-7B (SiliconFlow)",
        "OpenGVLab/InternVL2-26B": "InternVL2-26B (SiliconFlow)",
        "OpenGVLab/InternVL2-8B": "InternVL2-8B (SiliconFlow)",
        "stepfun-ai/GOT-OCR2_0": "GOT-OCR (SiliconFlow)",
        
        # 其他
        "claude-3-opus": "Claude 3 Opus",
        "claude-3-sonnet": "Claude 3 Sonnet",
    }
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        model: str = "gpt-4o-mini",
        enabled: bool = True
    ):
        """
        初始化视觉分析器
        
        Args:
            api_key: API 密钥
            base_url: API 基础 URL
            model: 视觉模型名称
            enabled: 是否启用视觉分析（False 则使用简单分析）
        """
        self.enabled = enabled
        self.model = model
        
        if enabled:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
            logger.info(f"视觉分析器初始化完成")
            logger.info(f"  - 模型: {model}")
            logger.info(f"  - API: {base_url}")
        else:
            logger.info("视觉分析器已禁用，将使用简单分析")
    
    def _encode_image(self, image_path: Path) -> str:
        """将图片编码为 base64"""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    def _build_analysis_prompt(self) -> str:
        """构建图片分析提示词"""
        return """请分析这张学术论文中的图片，并提供以下信息：

**重要**: 首先判断这张图片是否与论文研究内容相关：
- ❌ 如果是期刊封面、logo、版权声明、页眉页脚等无关内容，设置 is_relevant=false
- ✅ 如果是实验结果、架构图、流程图、表格等研究相关内容，设置 is_relevant=true

1. **相关性** (is_relevant): true 或 false

2. **图片类型** (figure_type): 
   - equation: 数学公式、方程式 ⭐
   - architecture: 系统架构图、模型结构图
   - flowchart: 流程图、算法流程
   - result: 实验结果图、对比图、性能图
   - table: 表格
   - chart: 图表、柱状图、折线图
   - cover: 期刊封面、logo（无关内容）
   - general: 其他类型图片

3. **简短描述** (caption): 用一句话描述图片内容（15-30字）

4. **建议放置位置** (placement):
   - introduction: 适合放在引言部分（如问题说明图）
   - methods: 适合放在方法部分（如架构图、流程图）
   - results: 适合放在结果部分（如实验结果、对比图）
   - any: 任意位置都可以

5. **重要性** (priority): 0-10 的整数
   - 8-10: 核心结果图、关键架构图、核心公式
   - 5-7: 重要但非核心的图片、辅助公式
   - 2-4: 辅助说明图片
   - 0-1: 无关或不重要的图片（如封面）
   
**特别提示**: 如果是数学公式/方程式，请设置 figure_type="equation"，并根据其重要性评分

请以 JSON 格式返回结果：
{
  "is_relevant": true,
  "figure_type": "result",
  "caption": "不同方法的性能对比结果",
  "placement": "results",
  "priority": 9
}

只返回 JSON，不要其他内容。"""
    
    def analyze_image(
        self,
        image_path: Path,
        image_filename: str
    ) -> Figure:
        """
        分析单张图片
        
        Args:
            image_path: 图片文件路径
            image_filename: 图片文件名
            
        Returns:
            Figure 对象
        """
        if not self.enabled:
            # 简单分析：基于文件名推测
            return self._simple_analysis(image_filename)
        
        try:
            logger.info(f"分析图片: {image_filename}")
            
            # 编码图片
            base64_image = self._encode_image(image_path)
            
            # 调用视觉模型
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": self._build_analysis_prompt()
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            # 解析响应
            content = response.choices[0].message.content
            analysis = json.loads(content)
            
            # 检查相关性 - 过滤无关图片
            is_relevant = analysis.get("is_relevant", True)
            if not is_relevant:
                logger.warning(f"图片 {image_filename} 被识别为无关内容，已过滤")
                return None  # 返回 None 表示应该过滤此图片
            
            # 创建 Figure 对象
            figure = Figure(
                path=image_filename,
                caption=analysis.get("caption", f"Figure: {image_filename}"),
                figure_type=analysis.get("figure_type", "general"),
                placement=analysis.get("placement", "any"),
                priority=analysis.get("priority", 5)
            )
            
            logger.info(f"  → 类型: {figure.figure_type}, 位置: {figure.placement}")
            
            return figure
            
        except Exception as e:
            logger.warning(f"图片分析失败 ({image_filename}): {e}")
            # 降级到简单分析
            return self._simple_analysis(image_filename)
    
    def _simple_analysis(self, image_filename: str) -> Figure:
        """
        简单分析：基于文件名和顺序推测
        
        Args:
            image_filename: 图片文件名
            
        Returns:
            Figure 对象
        """
        # 提取图片编号
        import re
        match = re.search(r'(\d+)', image_filename)
        number = int(match.group(1)) if match else 0
        
        # 基于文件名简单推测
        filename_lower = image_filename.lower()
        
        # 尝试从文件名推测类型
        if 'eq' in filename_lower or 'formula' in filename_lower:
            figure_type = "equation"
            placement = "methods"
            caption = f"Mathematical equation"
            priority = 7
        elif number <= 2:
            figure_type = "architecture"
            placement = "methods"
            caption = f"Method illustration"
            priority = 7
        elif number <= 5:
            figure_type = "result"
            placement = "results"
            caption = f"Experimental results"
            priority = 8
        else:
            figure_type = "general"
            placement = "any"
            caption = f"Figure {number}"
            priority = 5
        
        return Figure(
            path=image_filename,
            caption=caption,
            figure_type=figure_type,
            placement=placement,
            priority=priority
        )
    
    def analyze_images(
        self,
        images_dir: Path,
        image_filenames: List[str],
        max_images: int = 15  # 增加默认值
    ) -> List[Figure]:
        """
        批量分析图片
        
        Args:
            images_dir: 图片目录
            image_filenames: 图片文件名列表
            max_images: 最多分析的图片数量
            
        Returns:
            Figure 对象列表，按重要性排序
        """
        logger.info("=" * 60)
        logger.info(f"开始分析 {len(image_filenames)} 张图片（最多保留 {max_images} 张）")
        logger.info("=" * 60)
        
        figures = []
        
        # 限制分析数量
        filenames_to_analyze = image_filenames[:max_images]
        
        for filename in filenames_to_analyze:
            image_path = images_dir / filename
            if image_path.exists():
                figure = self.analyze_image(image_path, filename)
                if figure is not None:  # 过滤掉无关图片
                    figures.append(figure)
        
        # 按 priority 属性排序（数字越大越重要）
        # 如果没有 priority，则使用 figure_type 的优先级
        type_priority = {
            "result": 8,
            "equation": 7,      # 公式也很重要
            "architecture": 7,
            "flowchart": 6,
            "chart": 5,
            "table": 4,
            "general": 3,
            "cover": 0
        }
        
        figures.sort(
            key=lambda f: (
                getattr(f, 'priority', type_priority.get(f.figure_type, 3)),
                type_priority.get(f.figure_type, 3)
            ),
            reverse=True  # 从高到低排序
        )
        
        logger.info("=" * 60)
        logger.info(f"图片分析完成，保留 {len(figures)} 张图片")
        for i, fig in enumerate(figures, 1):
            logger.info(f"  {i}. {fig.path} - {fig.figure_type} ({fig.placement})")
        logger.info("=" * 60)
        
        return figures
    
    @staticmethod
    def is_vision_model_available(model: str) -> bool:
        """检查是否是支持的视觉模型"""
        return model in VisionAnalyzer.VISION_MODELS
    
    @staticmethod
    def get_recommended_vision_model(base_url: str) -> str:
        """根据 API URL 推荐视觉模型"""
        base_url_lower = base_url.lower()
        
        if "siliconflow" in base_url_lower:
            return "Qwen/Qwen2-VL-7B-Instruct"
        elif "openai" in base_url_lower:
            return "gpt-4o-mini"
        elif "anthropic" in base_url_lower or "claude" in base_url_lower:
            return "claude-3-sonnet"
        else:
            # 默认使用经济型模型
            return "gpt-4o-mini"

