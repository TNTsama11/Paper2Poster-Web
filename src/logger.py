"""
日志模块 - 提供彩色日志输出
"""
import logging
import colorlog


def setup_logger(name: str = "Paper2Poster", level=logging.INFO):
    """设置彩色日志"""
    handler = colorlog.StreamHandler()
    handler.setFormatter(
        colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
    )
    
    logger = colorlog.getLogger(name)
    logger.addHandler(handler)
    logger.setLevel(level)
    
    return logger

