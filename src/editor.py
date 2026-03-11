"""
智能编辑部 (The Editor)
负责调用 LLM 进行内容理解和结构化输出
"""
import json
from typing import List, Optional
from pathlib import Path
from openai import OpenAI

from .models import PosterContent, Figure
from .vision_analyzer import VisionAnalyzer
from .logger import setup_logger

logger = setup_logger("Editor")


class LLMEditor:
    """LLM 编辑器 - 将论文文本转换为结构化海报内容"""
    
    def __init__(
        self, 
        api_key: str, 
        base_url: str = "https://api.openai.com/v1",
        model: str = "gpt-4-turbo-preview",
        max_tokens: int = 4096,
        temperature: float = 0.3,
        enable_vision: bool = False,
        vision_model: Optional[str] = None,
        images_dir: Optional[Path] = None
    ):
        """
        初始化 LLM 编辑器
        
        Args:
            api_key: OpenAI API 密钥
            base_url: API 基础 URL（支持自定义兼容 OpenAI API 的服务）
            model: 模型名称
            max_tokens: 最大生成 token 数
            temperature: 温度参数（0-1，越低越稳定）
            enable_vision: 是否启用视觉模型分析图片
            vision_model: 视觉模型名称（如果不指定则自动推荐）
            images_dir: 图片目录
        """
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.enable_vision = enable_vision
        self.images_dir = images_dir
        
        # 初始化视觉分析器
        if enable_vision:
            if vision_model is None:
                vision_model = VisionAnalyzer.get_recommended_vision_model(base_url)
            
            self.vision_analyzer = VisionAnalyzer(
                api_key=api_key,
                base_url=base_url,
                model=vision_model,
                enabled=True
            )
        else:
            self.vision_analyzer = None
        
        logger.info(f"LLM 编辑器初始化完成")
        logger.info(f"  - 模型: {model}")
        logger.info(f"  - API: {base_url}")
        logger.info(f"  - 视觉分析: {'启用' if enable_vision else '禁用'}")
    
    def _build_system_prompt(self, abstract_max_words: int = 130, output_language: str = "auto") -> str:
        """构建系统提示词"""
        # 根据语言选择构建语言要求
        if output_language == "chinese":
            language_instruction = """2. **重要**：所有内容必须用中文输出，包括标题、摘要、各部分内容等。即使论文是英文的，也要翻译为中文。
   **例外**：
   - **作者姓名**（authors 字段）必须保持原文，不要翻译或音译
   - **参考文献**（references 字段）必须保持原文，不要翻译"""
        elif output_language == "english":
            language_instruction = """2. **Important**: All content must be output in English, including title, abstract, and all sections. If the paper is in Chinese, translate it to English.
   **Exceptions**:
   - **Author names** (authors field) must be kept in original form, do not translate
   - **References** (references field) must be kept in original form, do not translate"""
        else:  # auto
            language_instruction = """2. 所有内容必须用论文的源语言输出（中文论文用中文，英文论文用英文）
   **例外**：
   - **作者姓名**（authors 字段）必须保持原文
   - **参考文献**（references 字段）必须保持原文"""
        
        return f"""你是一个专业的学术海报设计师。你的任务是将论文内容转化为信息丰富、结构清晰的海报内容。

要求：
1. 请忽略无关的致谢或附录部分
{language_instruction}
3. 对于 section 的 content 字段，必须使用 Markdown 的无序列表格式（- 开头）
4. **内容量要求**：
   - Introduction: 至少 5-7 个要点，每个30-50字
   - Methods: 至少 6-8 个要点，详细说明方法细节
   - Results: 至少 5-7 个要点，包含具体数据和发现
   - Conclusion: 至少 4-5 个要点，总结贡献和展望
5. **Abstract 生成规则**：
   - 字数限制：严格控制在 **{abstract_max_words}字以内**（中文字符）
   - 内容要求：核心创新点 + 主要方法 + 关键结果
   - 如果原文摘要过长，务必重新组织语言，删减次要信息，保持语义完整
6. 从提供的图片列表中选择最能代表"方法"或"核心结果"的一张图作为主图
7. 如果没有合适的图片，将 main_figure_path 设为 null
8. **authors 字段规则**：
   - 必须是字符串格式，多个作者用逗号分隔
   - **必须保持原文**，不要翻译或音译作者姓名
   - 示例: "John Smith, Li Wei, Maria Garcia"（无论输出语言是什么，作者名都保持原样）
9. **references 字段规则**：
   - **必须保持原文**，不要翻译参考文献
   - 保留原始引用格式和语言
10. **重要**：内容要充实，避免过度简化，保留关键技术细节和数据

**重要**: 必须输出完整的 JSON，包含所有必需字段。请严格按照下面的 JSON Schema 格式输出：

{{
  "title": "海报标题（准确）",
  "authors": "Author1, Author2, Author3（保持原文，不翻译）",
  "affiliation": "机构/学校名称",
  "abstract": "约100字的摘要...",
  "introduction": {{
    "title": "Introduction",
    "content": "- 要点1\\n- 要点2\\n- 要点3"
  }},
  "main_figure_path": "img_01.png",
  "main_figure_caption": "图片的一句话说明",
  "methods": {{
    "title": "Methods",
    "content": "- 方法要点1\\n- 方法要点2"
  }},
  "results": {{
    "title": "Results",
    "content": "- 结果要点1\\n- 结果要点2"
  }},
  "conclusion": {{
    "title": "Conclusion",
    "content": "- 结论要点1\\n- 结论要点2"
  }},
  "references": ["Reference 1 in original language", "Reference 2 in original language", "Reference 3 in original language"]
}}

请严格按照此格式输出，不要遗漏任何字段。"""
    
    def _build_user_prompt(self, full_text: str, image_manifest: List[str]) -> str:
        """
        构建用户提示词
        
        Args:
            full_text: 论文全文
            image_manifest: 可用图片列表
        """
        # 如果文本太长，进行截断（保留前后部分）
        max_text_length = 30000  # 约 7500 tokens
        if len(full_text) > max_text_length:
            logger.warning(f"论文文本过长 ({len(full_text)} 字符)，进行截断")
            half_length = max_text_length // 2
            full_text = full_text[:half_length] + "\n\n...[中间部分省略]...\n\n" + full_text[-half_length:]
        
        prompt = f"""请阅读以下学术论文内容，并将其转换为海报所需的结构化内容。

# 论文内容：
{full_text}

# 可用图片列表：
{', '.join(image_manifest) if image_manifest else '无可用图片'}

请从可用图片列表中选择最合适的一张作为 main_figure_path。如果列表为空或没有合适的图片，请将 main_figure_path 设为 null。

**重要提醒**：
1. authors 必须是字符串，多个作者用逗号连接（如："作者A, 作者B, 作者C"）
2. 必须包含所有必需字段：title, authors, affiliation, abstract, introduction, methods, results, conclusion, references, main_figure_caption
3. 每个 section (introduction/methods/results/conclusion) 都必须有 title 和 content 两个字段

请输出完整的 JSON 对象。"""
        
        return prompt
    
    def _fix_json_data(self, data: dict, image_manifest: List[str]) -> dict:
        """
        修复 LLM 返回的 JSON 数据中的常见问题
        
        Args:
            data: LLM 返回的原始数据
            image_manifest: 图片列表
            
        Returns:
            修复后的数据
        """
        # 修复 authors 字段（如果是列表，转为字符串）
        if "authors" in data and isinstance(data["authors"], list):
            data["authors"] = ", ".join(data["authors"])
        
        # 确保必需字段存在
        if "affiliation" not in data:
            data["affiliation"] = "Unknown Institution"
        
        if "abstract" not in data:
            data["abstract"] = "Abstract not available."
        
        # 修复 section 字段
        section_defaults = {
            "introduction": {"title": "Introduction", "content": "- Content not available"},
            "methods": {"title": "Methods", "content": "- Content not available"},
            "results": {"title": "Results", "content": "- Content not available"},
            "conclusion": {"title": "Conclusion", "content": "- Content not available"}
        }
        
        for section_name, default_value in section_defaults.items():
            if section_name not in data:
                data[section_name] = default_value
            elif not isinstance(data[section_name], dict):
                data[section_name] = default_value
            else:
                # 确保有 title 和 content
                if "title" not in data[section_name]:
                    data[section_name]["title"] = default_value["title"]
                if "content" not in data[section_name]:
                    data[section_name]["content"] = default_value["content"]
                # 修复 content 字段：如果是列表，转为字符串
                elif isinstance(data[section_name]["content"], list):
                    # 将列表项用换行符连接，保持markdown格式
                    content_list = data[section_name]["content"]
                    data[section_name]["content"] = "\n".join(content_list)
        
        # 修复 figures 字段（新版多图支持）
        if "figures" not in data or not isinstance(data["figures"], list):
            data["figures"] = []
        
        # 修复 main_figure_caption（兼容旧版）
        if "main_figure_caption" not in data:
            if data.get("main_figure_path"):
                data["main_figure_caption"] = "Figure from the paper"
            elif data.get("figures"):
                data["main_figure_caption"] = data["figures"][0].get("caption", "")
            else:
                data["main_figure_caption"] = ""
        
        # 修复 references
        if "references" not in data:
            data["references"] = ["References not available"]
        elif not isinstance(data["references"], list):
            data["references"] = ["References not available"]
        
        # 验证 main_figure_path
        if "main_figure_path" in data and data["main_figure_path"]:
            if data["main_figure_path"] not in image_manifest:
                logger.warning(f"LLM 选择的图片 {data['main_figure_path']} 不在图片列表中")
                # 如果有图片，选择第一张；否则设为 None
                data["main_figure_path"] = image_manifest[0] if image_manifest else None
        
        return data
    
    def generate_poster_content(
        self, 
        full_text: str, 
        image_manifest: List[str],
        abstract_max_words: int = 130,
        output_language: str = "auto"
    ) -> PosterContent:
        """
        调用 LLM 生成结构化的海报内容
        
        Args:
            full_text: 论文全文文本
            image_manifest: 提取的图片文件名列表
            abstract_max_words: Abstract 最大字数限制
            output_language: 输出语言 ("auto", "chinese", "english")
            
        Returns:
            结构化的海报内容对象
        """
        logger.info("=" * 60)
        logger.info("开始 LLM 内容生成")
        logger.info("=" * 60)
        
        system_prompt = self._build_system_prompt(abstract_max_words, output_language)
        user_prompt = self._build_user_prompt(full_text, image_manifest)
        
        logger.info(f"发送请求到 LLM (模型: {self.model})")
        
        try:
            # 使用 Pydantic 模型的 JSON Schema
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            # 解析响应
            content = response.choices[0].message.content
            logger.info("收到 LLM 响应")
            
            # 解析 JSON
            content_dict = json.loads(content)
            
            # 修复常见的格式问题
            content_dict = self._fix_json_data(content_dict, image_manifest)
            
            # 保存原始 JSON 用于调试
            logger.debug(f"修复后的 JSON: {json.dumps(content_dict, ensure_ascii=False, indent=2)}")
            
            # 使用 Pydantic 验证和解析
            poster_content = PosterContent(**content_dict)
            
            logger.info("=" * 60)
            logger.info("内容生成完成")
            logger.info(f"  - 标题: {poster_content.title}")
            logger.info(f"  - 作者: {poster_content.authors}")
            logger.info(f"  - 主图: {poster_content.main_figure_path or '无'}")
            logger.info("=" * 60)
            
            return poster_content
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {e}")
            logger.error(f"LLM 原始输出: {content[:500]}...")
            raise ValueError(f"LLM 返回的不是有效的 JSON 格式。请检查 API 配置或尝试其他模型。")
        except ValueError as e:
            # Pydantic 验证错误
            logger.error(f"数据验证失败: {e}")
            logger.error(f"问题数据: {json.dumps(content_dict, ensure_ascii=False, indent=2)}")
            raise ValueError(f"LLM 返回的数据格式不完整。建议：\n1. 使用更强大的模型（如 GPT-4）\n2. 检查论文 PDF 质量\n3. 尝试更短的论文")
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            raise ValueError(f"LLM 调用失败: {str(e)}\n请检查：\n1. API 密钥是否正确\n2. 网络连接\n3. API 账户余额")
    
    def edit(self, full_text: str, image_manifest: List[str], max_images: int = 15, equations: List[dict] = None, abstract_max_words: int = 130, output_language: str = "auto") -> PosterContent:
        """
        执行完整的编辑流程
        
        Args:
            full_text: 论文全文文本
            image_manifest: 提取的图片文件名列表
            max_images: 最多分析的图片数量
            equations: 提取的公式列表
            abstract_max_words: Abstract 最大字数限制
            output_language: 输出语言 ("auto", "chinese", "english")
            
        Returns:
            结构化的海报内容对象
        """
        # 如果启用视觉分析，先分析图片
        analyzed_figures = []
        if self.enable_vision and self.vision_analyzer and self.images_dir:
            analyzed_figures = self.vision_analyzer.analyze_images(
                self.images_dir,
                image_manifest,
                max_images=max_images  # 使用传入的参数
            )
        
        # 生成海报内容
        language_desc = {"auto": "自动检测", "chinese": "中文", "english": "英文"}.get(output_language, "自动检测")
        logger.info(f"🤖 正在调用 LLM 生成海报内容 (Abstract限制: {abstract_max_words}字, 输出语言: {language_desc})...")
        poster_content = self.generate_poster_content(full_text, image_manifest, abstract_max_words, output_language)
        
        # 如果有视觉分析结果，替换 figures
        if analyzed_figures:
            poster_content.figures = analyzed_figures
            logger.info(f"已集成 {len(analyzed_figures)} 张视觉分析的图片")
        
        # 如果有公式，集成公式
        if equations:
            from .models import Equation
            poster_equations = []
            # 选择最重要的5个公式
            for eq_dict in equations[:5]:
                equation = Equation(
                    content=eq_dict['content'],
                    equation_type=eq_dict['type'],
                    context=eq_dict.get('context', ''),
                    description=f"关键公式 ({eq_dict['type']})"
                )
                poster_equations.append(equation)
            poster_content.equations = poster_equations
            logger.info(f"已集成 {len(poster_equations)} 个公式")
        
        return poster_content

