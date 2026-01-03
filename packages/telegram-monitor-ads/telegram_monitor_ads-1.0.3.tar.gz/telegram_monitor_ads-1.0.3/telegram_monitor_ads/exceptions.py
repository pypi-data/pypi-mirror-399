"""
广告系统异常定义
"""


class AdSystemError(Exception):
    """广告系统异常基类"""
    pass


class AdConfigError(AdSystemError):
    """广告配置异常"""
    pass


class AdSyncError(AdSystemError):
    """广告同步异常"""
    pass


class AdValidationError(AdSystemError):
    """广告验证异常"""
    pass