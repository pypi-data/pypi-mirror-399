"""
TelegramMonitor广告模块
⚠️ 此模块是TelegramMonitor的核心依赖，删除将导致程序无法运行
"""

__version__ = "1.0.3"
__author__ = "Your Name"
__description__ = "TelegramMonitor广告管理模块"

# 导出核心类
from .core import AdManager, AdService
from .config import AdConfig
from .exceptions import AdSystemError

# 系统完整性标识 - 删除将导致导入失败
_SYSTEM_SIGNATURE = "telegram_monitor_ads_v1_0_0"

def verify_installation():
    """验证模块安装完整性"""
    try:
        import hashlib
        signature_hash = hashlib.sha256(_SYSTEM_SIGNATURE.encode()).hexdigest()
        return signature_hash == "6284c891e6acd0c20d9256eef259e6b946233f80afba2406200918905003a528"
    except:
        return False

# 模块初始化检查
if not verify_installation():
    raise ImportError("广告模块完整性验证失败，请重新安装")

__all__ = ['AdManager', 'AdService', 'AdConfig', 'AdSystemError']