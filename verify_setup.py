#!/usr/bin/env python3
"""
验证 Paper2Poster-Web 项目设置
"""
import sys
from pathlib import Path

def check_file(path, name):
    """检查文件是否存在"""
    if Path(path).exists():
        print(f"✓ {name}")
        return True
    else:
        print(f"✗ {name} - 缺失")
        return False

def check_directory(path, name):
    """检查目录是否存在"""
    if Path(path).is_dir():
        print(f"✓ {name}/")
        return True
    else:
        print(f"✗ {name}/ - 缺失")
        return False

def check_import(module_name, display_name):
    """检查 Python 模块是否可导入"""
    try:
        __import__(module_name)
        print(f"✓ {display_name}")
        return True
    except ImportError as e:
        print(f"✗ {display_name} - 未安装: {e}")
        return False

def main():
    print("=" * 60)
    print("Paper2Poster-Web 项目验证")
    print("=" * 60)
    
    all_ok = True
    
    # 检查核心文件
    print("\n📁 核心文件:")
    all_ok &= check_file("config.py", "config.py")
    all_ok &= check_file("main.py", "main.py")
    all_ok &= check_file("requirements.txt", "requirements.txt")
    all_ok &= check_file("README.md", "README.md")
    
    # 检查目录结构
    print("\n📂 目录结构:")
    all_ok &= check_directory("src", "src")
    all_ok &= check_directory("templates", "templates")
    all_ok &= check_directory("input", "input")
    all_ok &= check_directory("output", "output")
    all_ok &= check_directory("output/images", "output/images")
    all_ok &= check_directory("backups", "backups")
    
    # 检查源代码模块
    print("\n🐍 源代码模块:")
    all_ok &= check_file("src/__init__.py", "src/__init__.py")
    all_ok &= check_file("src/harvester.py", "src/harvester.py")
    all_ok &= check_file("src/editor.py", "src/editor.py")
    all_ok &= check_file("src/renderer.py", "src/renderer.py")
    all_ok &= check_file("src/models.py", "src/models.py")
    all_ok &= check_file("src/logger.py", "src/logger.py")
    
    # 检查模板
    print("\n🎨 模板文件:")
    all_ok &= check_file("templates/simple_grid.html", "simple_grid.html")
    
    # 检查 Python 依赖
    print("\n📦 Python 依赖:")
    all_ok &= check_import("fitz", "PyMuPDF")
    all_ok &= check_import("openai", "openai")
    all_ok &= check_import("pydantic", "pydantic")
    all_ok &= check_import("jinja2", "jinja2")
    all_ok &= check_import("playwright", "playwright")
    all_ok &= check_import("dotenv", "python-dotenv")
    all_ok &= check_import("colorlog", "colorlog")
    all_ok &= check_import("PIL", "Pillow")
    all_ok &= check_import("markdown", "markdown")
    
    # 检查环境变量
    print("\n🔑 环境配置:")
    env_file_exists = check_file(".env", ".env")
    if not env_file_exists:
        print("   ⚠️  提示: 请复制 .env.example 为 .env 并配置 API 密钥")
        all_ok = False
    
    # 测试导入核心模块
    print("\n🔍 模块导入测试:")
    try:
        from src.harvester import PDFHarvester
        from src.editor import LLMEditor
        from src.renderer import PosterRenderer
        from src.models import PosterContent, Section
        print("✓ 所有核心模块可正常导入")
    except Exception as e:
        print(f"✗ 模块导入失败: {e}")
        all_ok = False
    
    # 总结
    print("\n" + "=" * 60)
    if all_ok:
        print("✅ 项目设置验证通过！")
        print("\n下一步:")
        print("1. 确保 .env 文件已配置 API 密钥")
        print("2. 将 PDF 文件放入 input/ 目录")
        print("3. 运行: python main.py input/your_paper.pdf")
    else:
        print("❌ 项目设置存在问题，请检查上述错误")
        sys.exit(1)
    print("=" * 60)

if __name__ == "__main__":
    main()

