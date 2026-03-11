"""
数据模型 - 使用 Pydantic 定义严格的数据结构
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class Section(BaseModel):
    """论文章节模型"""
    title: str = Field(..., description="小节标题，如 Introduction, Methods")
    content: str = Field(
        ..., 
        description="Markdown 格式的要点内容，必须使用无序列表 Bullet Points"
    )


class Figure(BaseModel):
    """图片模型"""
    path: str = Field(..., description="图片文件名")
    caption: str = Field(..., description="图片说明")
    figure_type: str = Field(
        default="general",
        description="图片类型: equation(公式), architecture(架构图), flowchart(流程图), result(结果图), table(表格), chart(图表), general(一般图片)"
    )
    placement: str = Field(
        default="any",
        description="建议放置位置: methods(方法区), results(结果区), introduction(引言区), any(任意)"
    )
    priority: int = Field(default=5, description="重要性优先级 0-10")


class Equation(BaseModel):
    """公式模型"""
    content: str = Field(..., description="公式的LaTeX或文本内容")
    equation_type: str = Field(..., description="公式类型: inline(行内), display(行间), equation(独立公式)")
    context: str = Field(default="", description="公式的上下文环境")
    description: str = Field(default="", description="公式的含义说明")


class PosterContent(BaseModel):
    """海报内容模型 - 定义海报的完整结构"""
    
    # 标题区域
    title: str = Field(..., description="海报的大标题，需精简有力")
    authors: str = Field(..., description="作者列表")
    affiliation: str = Field(..., description="机构/学校名称")
    
    # 左栏内容
    abstract: str = Field(..., description="摘要，约 100 字")
    introduction: Section
    
    # 图片内容（支持多图）
    figures: List[Figure] = Field(
        default=[],
        description="论文中的所有重要图片，按重要性排序"
    )
    
    # 公式内容
    equations: List[Equation] = Field(
        default=[],
        description="论文中的关键公式，最多5个"
    )
    
    # 兼容旧版：主图（如果 figures 为空则使用这个）
    main_figure_path: Optional[str] = Field(
        None, 
        description="从提取的图片列表中选一张最重要的结果图文件名（兼容旧版）"
    )
    main_figure_caption: str = Field(
        default="", 
        description="对主图的一句话解释（兼容旧版）"
    )
    
    # 中栏内容
    methods: Section
    
    # 右栏内容
    results: Section
    conclusion: Section
    references: List[str] = Field(
        ..., 
        description="只列出最重要的 3-5 篇参考文献"
    )
    
    def to_dict(self):
        """转换为字典格式，方便模板渲染"""
        return {
            "title": self.title,
            "authors": self.authors,
            "affiliation": self.affiliation,
            "abstract": self.abstract,
            "introduction": {
                "title": self.introduction.title,
                "content": self.introduction.content
            },
            "figures": [
                {
                    "path": fig.path,
                    "caption": fig.caption,
                    "type": fig.figure_type,
                    "placement": fig.placement,
                    "priority": getattr(fig, 'priority', 5)
                }
                for fig in self.figures
            ],
            "equations": [
                {
                    "content": eq.content,
                    "type": eq.equation_type,
                    "description": eq.description
                }
                for eq in self.equations
            ],
            "main_figure_path": self.main_figure_path,
            "main_figure_caption": self.main_figure_caption,
            "methods": {
                "title": self.methods.title,
                "content": self.methods.content
            },
            "results": {
                "title": self.results.title,
                "content": self.results.content
            },
            "conclusion": {
                "title": self.conclusion.title,
                "content": self.conclusion.content
            },
            "references": self.references
        }

