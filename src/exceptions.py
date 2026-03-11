"""
自定义异常类 - 提供清晰的错误信息和解决建议
"""


class Paper2PosterError(Exception):
    """Paper2Poster 基础异常类"""

    def __init__(self, message: str, suggestion: str = None):
        """
        Args:
            message: 错误信息
            suggestion: 解决建议
        """
        self.message = message
        self.suggestion = suggestion
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """格式化完整的错误信息"""
        if self.suggestion:
            return f"{self.message}\n\n💡 建议：{self.suggestion}"
        return self.message

    def to_user_friendly(self) -> str:
        """转换为用户友好的错误信息（用于 WebUI）"""
        return self._format_message()


class PDFExtractionError(Paper2PosterError):
    """PDF 提取错误"""

    def __init__(self, message: str, detail: str = None):
        suggestion = "请检查：\n1. PDF 文件是否损坏\n2. PDF 是否为扫描件（需要 OCR）\n3. 尝试用其他 PDF 阅读器打开确认文件正常"
        if detail:
            message = f"{message}（详情：{detail}）"
        super().__init__(message, suggestion)


class LLMError(Paper2PosterError):
    """LLM 调用错误基类"""

    def __init__(self, message: str, suggestion: str = None):
        super().__init__(message, suggestion)


class LLMConnectionError(LLMError):
    """LLM 连接错误"""

    def __init__(self, detail: str = None):
        message = "无法连接到 LLM API 服务"
        if detail:
            message = f"{message}（{detail}）"
        suggestion = "请检查：\n1. 网络连接是否正常\n2. API Base URL 是否正确\n3. 是否需要代理/VPN"
        super().__init__(message, suggestion)


class LLMAuthError(LLMError):
    """LLM 认证错误"""

    def __init__(self):
        message = "API 密钥认证失败"
        suggestion = "请检查：\n1. API 密钥是否正确（检查开头和结尾字符）\n2. API 密钥是否已过期或被禁用\n3. 账户余额是否充足"
        super().__init__(message, suggestion)


class LLMRateLimitError(LLMError):
    """LLM 速率限制错误"""

    def __init__(self, retry_after: int = None):
        message = "API 请求频率超限"
        if retry_after:
            message = f"{message}，请在 {retry_after} 秒后重试"
        suggestion = "建议：\n1. 等待几秒后重试\n2. 如频繁遇到此问题，可考虑升级 API 套餐"
        super().__init__(message, suggestion)


class LLMResponseError(LLMError):
    """LLM 响应格式错误"""

    def __init__(self, detail: str = None):
        message = "LLM 返回的数据格式不正确"
        if detail:
            message = f"{message}（{detail}）"
        suggestion = "建议：\n1. 使用更强大的模型（如 GPT-4）\n2. 检查论文 PDF 质量和文本可读性\n3. 尝试处理更短的论文"
        super().__init__(message, suggestion)


class RenderingError(Paper2PosterError):
    """渲染错误"""

    def __init__(self, message: str, detail: str = None):
        if detail:
            message = f"{message}（{detail}）"
        suggestion = "请检查：\n1. Playwright 浏览器是否正确安装（运行：playwright install chromium）\n2. 系统内存是否充足\n3. 输出目录是否有写入权限"
        super().__init__(message, suggestion)


class TemplateError(Paper2PosterError):
    """模板错误"""

    def __init__(self, template_name: str, detail: str = None):
        message = f"模板 '{template_name}' 处理失败"
        if detail:
            message = f"{message}（{detail}）"
        suggestion = "请检查：\n1. 模板文件是否存在于 templates 目录\n2. 模板语法是否正确（Jinja2 格式）\n3. 尝试使用默认模板 simple_grid.html"
        super().__init__(message, suggestion)


class ConfigurationError(Paper2PosterError):
    """配置错误"""

    def __init__(self, config_name: str, detail: str = None):
        message = f"配置项 '{config_name}' 无效"
        if detail:
            message = f"{message}（{detail}）"
        suggestion = "请检查 .env 文件中的配置是否正确"
        super().__init__(message, suggestion)


# 错误映射：将原始异常转换为友好异常
def convert_llm_error(error: Exception) -> LLMError:
    """
    将 OpenAI API 错误转换为友好的 LLM 错误

    Args:
        error: 原始异常

    Returns:
        对应的 LLMError 子类
    """
    error_str = str(error).lower()

    # 认证错误
    if any(kw in error_str for kw in ['unauthorized', 'invalid api key', 'authentication', '401']):
        return LLMAuthError()

    # 速率限制
    if any(kw in error_str for kw in ['rate limit', '429', 'too many requests']):
        return LLMRateLimitError()

    # 连接错误
    if any(kw in error_str for kw in ['connection', 'timeout', 'network', 'connect']):
        return LLMConnectionError(str(error))

    # 其他 LLM 错误
    return LLMResponseError(str(error))
