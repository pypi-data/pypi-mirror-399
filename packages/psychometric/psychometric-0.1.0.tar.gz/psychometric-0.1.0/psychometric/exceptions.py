"""
自定义异常类
"""


class PsychometricError(Exception):
    """心理测量分析基础异常"""

    pass


class DataValidationError(PsychometricError):
    """数据验证错误"""

    pass


class InsufficientDataError(PsychometricError):
    """数据量不足错误"""

    pass
