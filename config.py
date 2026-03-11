"""
配置文件 - 管理项目配置和环境变量
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 项目根目录
ROOT_DIR = Path(__file__).parent
INPUT_DIR = ROOT_DIR / "input"
OUTPUT_DIR = ROOT_DIR / "output"
IMAGES_DIR = OUTPUT_DIR / "images"
TEMPLATES_DIR = ROOT_DIR / "templates"
BACKUPS_DIR = ROOT_DIR / "backups"

# 确保目录存在
INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)
BACKUPS_DIR.mkdir(exist_ok=True)

# OpenAI API 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

# 图片提取配置
MIN_IMAGE_WIDTH = int(os.getenv("MIN_IMAGE_WIDTH", "100"))  # 降低以包含公式
MIN_IMAGE_HEIGHT = int(os.getenv("MIN_IMAGE_HEIGHT", "100"))
MAX_IMAGES_ANALYZE = int(os.getenv("MAX_IMAGES_ANALYZE", "15"))  # 最多分析的图片数

# ============================================
# 海报尺寸配置 (像素)
# ============================================

# 默认尺寸（适合大多数场景）
POSTER_WIDTH = 1600
POSTER_HEIGHT = 1800  # 增加高度，防止内容溢出

# 学术海报常用尺寸预设 (名称: (宽, 高, 描述))
POSTER_PRESETS = {
    "default": (1600, 1800, "默认尺寸 (适合大多数场景)"),
    "a0_portrait": (3370, 4768, "A0 纵向 (841×1189mm, 标准学术海报)"),
    "a0_landscape": (4768, 3370, "A0 横向 (1189×841mm)"),
    "a1_portrait": (2384, 3370, "A1 纵向 (594×841mm)"),
    "a1_landscape": (3370, 2384, "A1 横向 (841×594mm)"),
    "36x48": (3600, 4800, "36\"×48\" 纵向 (914×1219mm, 北美常用)"),
    "48x36": (4800, 3600, "48\"×36\" 横向 (1219×914mm)"),
    "screen_4k": (3840, 2160, "4K 屏幕 (16:9, 适合展示)"),
    "screen_hd": (1920, 1080, "1080p 屏幕 (16:9, 轻量级)"),
    "compact": (1400, 1600, "紧凑型 (适合简短论文)"),
    "extended": (1600, 2400, "加长型 (适合内容丰富的论文)"),
}

# 模板推荐尺寸（模板名: 预设名）
TEMPLATE_RECOMMENDED_SIZES = {
    "academic_panels.html": "extended",  # 多面板，内容丰富，需要更大高度
    "academic_panels_landscape.html": "screen_hd",  # 横版16:9，1080p更紧凑，内容密度更高
    "multi_figure_grid.html": "default",  # 多图展示，默认尺寸即可
    "simple_grid.html": "compact",        # 简单布局，紧凑型即可
}

# LLM 配置
MAX_TOKENS = 4096
TEMPERATURE = 0.3  # 较低的温度以获得更稳定的输出

# 视觉分析配置
ENABLE_VISION_ANALYSIS = os.getenv("ENABLE_VISION_ANALYSIS", "false").lower() == "true"
VISION_MODEL = os.getenv("VISION_MODEL", None)  # None 表示自动推荐

