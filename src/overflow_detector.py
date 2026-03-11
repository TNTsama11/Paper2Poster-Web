"""
内容溢出检测器 (Overflow Detector)
使用 VLM 检测海报中是否有内容被截断或溢出
"""
import base64
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
from playwright.sync_api import sync_playwright

from .logger import setup_logger

logger = setup_logger("OverflowDetector")


class OverflowDetector:
    """检测海报内容溢出并提供修复建议"""
    
    def __init__(
        self,
        vision_client,
        vision_model: str = "gpt-4o-mini",
        enabled: bool = True
    ):
        """
        初始化溢出检测器
        
        Args:
            vision_client: OpenAI 兼容的视觉模型客户端
            vision_model: 视觉模型名称
            enabled: 是否启用检测
        """
        self.client = vision_client
        self.model = vision_model
        self.enabled = enabled
    
    def capture_screenshot(
        self,
        html_path: Path,
        output_path: Optional[Path] = None
    ) -> Path:
        """
        截取海报截图
        
        Args:
            html_path: HTML 文件路径
            output_path: 截图保存路径
            
        Returns:
            截图文件路径
        """
        if output_path is None:
            output_path = html_path.parent / "overflow_check.png"
        
        logger.info(f"截取海报截图: {html_path}")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # 打开 HTML
                page.goto(f"file://{html_path.absolute()}")
                
                # 等待加载
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(1000)  # 额外等待1秒确保渲染完成
                
                # 全页截图
                page.screenshot(path=str(output_path), full_page=True)
                
                browser.close()
            
            logger.info(f"截图已保存: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"截图失败: {e}")
            raise
    
    def _encode_image(self, image_path: Path) -> str:
        """将图片编码为 base64"""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    
    def _build_detection_prompt(self) -> str:
        """构建检测提示词"""
        return """请仔细检查这张学术海报，识别以下问题：

1. **文字截断** (Text Cutoff):
   - 段落文字被截断，最后一行显示不完整
   - 标题文字超出边界
   - 列表项被切断

2. **图片溢出** (Image Overflow):
   - 图片超出面板边界
   - 图片被切掉一部分
   - 图片与其他内容重叠

3. **内容重叠** (Content Overlap):
   - 文字与图片重叠
   - 面板之间内容交叉
   - 内容覆盖边框

4. **空白不均** (Uneven Spacing):
   - 某些面板过于拥挤
   - 某些面板几乎空白
   - 内容分布极不均匀

请以 JSON 格式返回结果：

{
  "has_overflow": true/false,
  "severity": "none/minor/moderate/severe",
  "issues": [
    {
      "type": "text_cutoff/image_overflow/content_overlap/spacing",
      "location": "具体位置描述",
      "severity": "minor/moderate/severe",
      "suggestion": "修复建议"
    }
  ],
  "overall_quality": 1-10分,
  "recommendations": [
    "整体改进建议1",
    "整体改进建议2"
  ]
}

只返回 JSON，不要其他内容。"""
    
    def detect_overflow(
        self,
        html_path: Path,
        screenshot_path: Optional[Path] = None
    ) -> Dict:
        """
        检测海报是否有内容溢出
        
        Args:
            html_path: HTML 文件路径
            screenshot_path: 可选的已有截图路径
            
        Returns:
            检测结果字典
        """
        if not self.enabled:
            logger.info("溢出检测已禁用")
            return {
                "has_overflow": False,
                "severity": "none",
                "issues": [],
                "overall_quality": 10,
                "recommendations": []
            }
        
        logger.info("=" * 60)
        logger.info("开始检测内容溢出")
        logger.info("=" * 60)
        
        try:
            # 1. 截图（如果没有提供）
            if screenshot_path is None:
                screenshot_path = self.capture_screenshot(html_path)
            
            # 2. 编码图片
            base64_image = self._encode_image(screenshot_path)
            
            # 3. 调用 VLM 分析
            logger.info(f"使用 {self.model} 分析海报...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": self._build_detection_prompt()
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.2,  # 较低温度以获得稳定结果
                response_format={"type": "json_object"}
            )
            
            # 4. 解析结果
            content = response.choices[0].message.content
            result = json.loads(content)
            
            # 5. 输出报告
            logger.info("=" * 60)
            logger.info("检测结果:")
            logger.info(f"  是否溢出: {'是' if result['has_overflow'] else '否'}")
            logger.info(f"  严重程度: {result['severity']}")
            logger.info(f"  整体质量: {result['overall_quality']}/10")
            
            if result['issues']:
                logger.info(f"  发现 {len(result['issues'])} 个问题:")
                for i, issue in enumerate(result['issues'], 1):
                    logger.info(f"    {i}. [{issue['type']}] {issue['location']}")
                    logger.info(f"       建议: {issue['suggestion']}")
            else:
                logger.info("  ✅ 未发现问题")
            
            logger.info("=" * 60)
            
            return result
            
        except Exception as e:
            logger.error(f"溢出检测失败: {e}", exc_info=True)
            # 返回默认值，不阻止流程
            return {
                "has_overflow": False,
                "severity": "unknown",
                "issues": [],
                "overall_quality": 7,
                "recommendations": ["检测失败，建议手动检查"]
            }
    
    def should_fix(self, detection_result: Dict, threshold: str = "moderate") -> bool:
        """
        判断是否需要修复
        
        Args:
            detection_result: 检测结果
            threshold: 触发修复的阈值 (minor/moderate/severe)
            
        Returns:
            是否需要修复
        """
        if not detection_result.get("has_overflow", False):
            return False
        
        severity = detection_result.get("severity", "none")
        
        severity_levels = {
            "none": 0,
            "minor": 1,
            "moderate": 2,
            "severe": 3
        }
        
        threshold_levels = severity_levels.get(threshold, 2)
        current_level = severity_levels.get(severity, 0)
        
        return current_level >= threshold_levels
    
    def generate_fix_suggestions(self, detection_result: Dict) -> Dict[str, any]:
        """
        根据检测结果生成修复建议
        
        Args:
            detection_result: 检测结果
            
        Returns:
            修复建议字典
        """
        suggestions = {
            "reduce_text": False,
            "reduce_images": False,
            "reduce_font_size": False,
            "increase_height": False,
            "compress_content": False
        }
        
        issues = detection_result.get("issues", [])
        
        for issue in issues:
            issue_type = issue.get("type", "")
            severity = issue.get("severity", "minor")
            
            if issue_type == "text_cutoff":
                if severity in ["moderate", "severe"]:
                    suggestions["reduce_text"] = True
                    suggestions["reduce_font_size"] = True
                else:
                    suggestions["compress_content"] = True
            
            elif issue_type == "image_overflow":
                suggestions["reduce_images"] = True
            
            elif issue_type == "content_overlap":
                suggestions["increase_height"] = True
                suggestions["reduce_text"] = True
            
            elif issue_type == "spacing" and "拥挤" in issue.get("location", ""):
                suggestions["compress_content"] = True
        
        # 记录建议
        logger.info("修复建议:")
        for key, value in suggestions.items():
            if value:
                logger.info(f"  ✓ {key}")
        
        return suggestions


def test_overflow_detection():
    """测试溢出检测功能"""
    from openai import OpenAI
    import os
    
    # 初始化
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    detector = OverflowDetector(
        vision_client=client,
        vision_model="gpt-4o-mini",
        enabled=True
    )
    
    # 测试检测
    html_path = Path("output/poster.html")
    if html_path.exists():
        result = detector.detect_overflow(html_path)
        
        if detector.should_fix(result):
            suggestions = detector.generate_fix_suggestions(result)
            print(f"\n需要修复！建议: {suggestions}")
        else:
            print("\n✅ 海报质量良好，无需修复")
    else:
        print(f"❌ 找不到文件: {html_path}")


if __name__ == "__main__":
    test_overflow_detection()

