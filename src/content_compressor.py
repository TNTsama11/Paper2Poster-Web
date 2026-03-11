"""
内容压缩器 (Content Compressor)
智能压缩海报内容以解决溢出问题
"""
from typing import Dict, List
from .models import PosterContent, Section, Figure
from .logger import setup_logger

logger = setup_logger("ContentCompressor")


class ContentCompressor:
    """智能压缩海报内容"""
    
    def __init__(self, llm_client=None, model: str = "gpt-4o-mini"):
        """
        初始化压缩器
        
        Args:
            llm_client: LLM 客户端（可选，用于智能压缩）
            model: LLM 模型名称
        """
        self.client = llm_client
        self.model = model
    
    def compress_content(
        self,
        poster_content: PosterContent,
        suggestions: Dict[str, bool]
    ) -> PosterContent:
        """
        根据建议压缩内容
        
        Args:
            poster_content: 原始海报内容
            suggestions: 修复建议字典
            
        Returns:
            压缩后的海报内容
        """
        logger.info("=" * 60)
        logger.info("开始压缩内容")
        logger.info("=" * 60)
        
        compressed = poster_content.copy(deep=True)
        
        # 1. 压缩文本
        if suggestions.get("reduce_text") or suggestions.get("compress_content"):
            logger.info("📝 压缩文本内容...")
            compressed = self._compress_text(compressed)
        
        # 2. 减少图片
        if suggestions.get("reduce_images"):
            logger.info("🖼️  减少图片数量...")
            compressed = self._reduce_images(compressed)
        
        # 3. 调整字体（通过CSS变量，这里记录建议）
        if suggestions.get("reduce_font_size"):
            logger.info("🔤 建议: 减小字体 (需在模板中调整)")
        
        # 4. 增加高度（需要重新渲染）
        if suggestions.get("increase_height"):
            logger.info("📏 建议: 增加海报高度 (需重新渲染)")
        
        logger.info("=" * 60)
        logger.info("压缩完成")
        logger.info("=" * 60)
        
        return compressed
    
    def _compress_text(self, poster_content: PosterContent) -> PosterContent:
        """
        压缩文本内容
        
        策略:
        1. 限制每个 section 的要点数量 (最多5个)
        2. 压缩冗长的要点
        3. 移除次要信息
        """
        max_bullets = 5  # 每个section最多5个要点
        max_bullet_length = 60  # 每个要点最多60字符
        
        # 压缩 abstract
        if len(poster_content.abstract) > 150:
            poster_content.abstract = poster_content.abstract[:147] + "..."
            logger.info(f"  Abstract: 压缩到 150 字符")
        
        # 压缩各个 section
        for section_name in ["introduction", "methods", "results", "conclusion"]:
            section = getattr(poster_content, section_name, None)
            if section and hasattr(section, 'content'):
                original_content = section.content
                compressed_content = self._compress_section_content(
                    original_content,
                    max_bullets,
                    max_bullet_length
                )
                section.content = compressed_content
                
                # 统计
                orig_bullets = len([l for l in original_content.split('\n') if l.strip()])
                comp_bullets = len([l for l in compressed_content.split('\n') if l.strip()])
                logger.info(f"  {section_name}: {orig_bullets} → {comp_bullets} 要点")
        
        # 压缩 references (最多保留5个)
        if len(poster_content.references) > 5:
            original_count = len(poster_content.references)
            poster_content.references = poster_content.references[:5]
            logger.info(f"  References: {original_count} → 5 条")
        
        return poster_content
    
    def _compress_section_content(
        self,
        content: str,
        max_bullets: int,
        max_bullet_length: int
    ) -> str:
        """
        压缩单个 section 的内容
        
        Args:
            content: 原始内容
            max_bullets: 最多要点数
            max_bullet_length: 每个要点最大长度
            
        Returns:
            压缩后的内容
        """
        # 分割成要点
        lines = content.split('\n')
        bullets = [line for line in lines if line.strip() and line.strip().startswith('-')]
        
        # 如果要点不多，只压缩长度
        if len(bullets) <= max_bullets:
            compressed_bullets = []
            for bullet in bullets:
                if len(bullet) > max_bullet_length:
                    # 截断过长的要点
                    compressed = bullet[:max_bullet_length - 3] + "..."
                    compressed_bullets.append(compressed)
                else:
                    compressed_bullets.append(bullet)
            return '\n'.join(compressed_bullets)
        
        # 如果要点太多，选择最重要的
        # 简单策略：保留前 max_bullets 个
        selected_bullets = bullets[:max_bullets]
        
        # 压缩长度
        compressed_bullets = []
        for bullet in selected_bullets:
            if len(bullet) > max_bullet_length:
                compressed = bullet[:max_bullet_length - 3] + "..."
                compressed_bullets.append(compressed)
            else:
                compressed_bullets.append(bullet)
        
        return '\n'.join(compressed_bullets)
    
    def _reduce_images(self, poster_content: PosterContent) -> PosterContent:
        """
        减少图片数量
        
        策略:
        1. 按 priority 排序
        2. 保留前 N 张 (N = 当前数量 * 0.7)
        3. 至少保留 3 张
        """
        current_count = len(poster_content.figures)
        
        if current_count <= 3:
            logger.info(f"  图片数量已经很少 ({current_count}张)，不减少")
            return poster_content
        
        # 目标数量：当前的 70%，至少3张
        target_count = max(3, int(current_count * 0.7))
        
        # 按优先级排序
        sorted_figures = sorted(
            poster_content.figures,
            key=lambda f: getattr(f, 'priority', 5),
            reverse=True
        )
        
        # 保留前 N 张
        poster_content.figures = sorted_figures[:target_count]
        
        logger.info(f"  图片: {current_count} → {target_count} 张")
        
        return poster_content
    
    def compress_with_llm(
        self,
        poster_content: PosterContent,
        target_reduction: float = 0.3
    ) -> PosterContent:
        """
        使用 LLM 智能压缩内容
        
        Args:
            poster_content: 原始内容
            target_reduction: 目标压缩率 (0.3 = 压缩30%)
            
        Returns:
            压缩后的内容
        """
        if self.client is None:
            logger.warning("未提供 LLM 客户端，使用简单压缩")
            return poster_content
        
        logger.info(f"使用 LLM 智能压缩 (目标: 减少 {target_reduction*100}%)")
        
        # TODO: 实现 LLM 驱动的智能压缩
        # 这需要调用 LLM 来重写内容，保留核心信息
        
        logger.warning("LLM 智能压缩尚未实现，使用简单压缩")
        return poster_content
    
    def estimate_content_size(self, poster_content: PosterContent) -> Dict[str, int]:
        """
        估算内容大小
        
        Returns:
            各部分的字符/项目数统计
        """
        stats = {
            "abstract_chars": len(poster_content.abstract),
            "introduction_bullets": self._count_bullets(poster_content.introduction.content),
            "methods_bullets": self._count_bullets(poster_content.methods.content),
            "results_bullets": self._count_bullets(poster_content.results.content),
            "conclusion_bullets": self._count_bullets(poster_content.conclusion.content),
            "figures_count": len(poster_content.figures),
            "references_count": len(poster_content.references),
            "total_bullets": 0
        }
        
        stats["total_bullets"] = (
            stats["introduction_bullets"] +
            stats["methods_bullets"] +
            stats["results_bullets"] +
            stats["conclusion_bullets"]
        )
        
        return stats
    
    def _count_bullets(self, content: str) -> int:
        """统计要点数量"""
        lines = content.split('\n')
        return len([line for line in lines if line.strip() and line.strip().startswith('-')])


def test_compression():
    """测试压缩功能"""
    from .models import PosterContent, Section, Figure
    
    # 创建测试数据
    test_content = PosterContent(
        title="Test Poster",
        authors="Author1, Author2",
        affiliation="University",
        abstract="A" * 200,  # 过长的摘要
        introduction=Section(
            title="Introduction",
            content="\n".join([f"- Point {i}: " + "x" * 50 for i in range(10)])  # 10个要点
        ),
        methods=Section(
            title="Methods",
            content="\n".join([f"- Method {i}: " + "y" * 50 for i in range(8)])
        ),
        results=Section(
            title="Results",
            content="\n".join([f"- Result {i}: " + "z" * 50 for i in range(12)])
        ),
        conclusion=Section(
            title="Conclusion",
            content="\n".join([f"- Conclusion {i}" for i in range(6)])
        ),
        references=[f"Reference {i}" for i in range(10)],
        figures=[
            Figure(path=f"img_{i}.png", caption=f"Figure {i}", 
                   figure_type="result", placement="results", priority=i)
            for i in range(15)
        ]
    )
    
    # 压缩
    compressor = ContentCompressor()
    
    print("压缩前:")
    stats_before = compressor.estimate_content_size(test_content)
    for key, value in stats_before.items():
        print(f"  {key}: {value}")
    
    suggestions = {
        "reduce_text": True,
        "reduce_images": True,
        "compress_content": True
    }
    
    compressed = compressor.compress_content(test_content, suggestions)
    
    print("\n压缩后:")
    stats_after = compressor.estimate_content_size(compressed)
    for key, value in stats_after.items():
        reduction = ((stats_before[key] - value) / stats_before[key] * 100) if stats_before[key] > 0 else 0
        print(f"  {key}: {value} (减少 {reduction:.1f}%)")


if __name__ == "__main__":
    test_compression()

