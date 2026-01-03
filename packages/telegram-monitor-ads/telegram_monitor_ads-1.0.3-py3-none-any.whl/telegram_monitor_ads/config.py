"""
广告配置模块
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class AdConfig:
    """广告配置类"""
    
    # 远程配置URL - 硬编码，不可修改
    primary_url: str = "https://raw.githubusercontent.com/luoyanglang/ads/main/ads.json"
    backup_url: str = ""  # 备用URL已禁用
    
    # 同步设置
    sync_interval: int = 300  # 5分钟
    
    # 显示设置
    default_frequency: int = 10
    max_ads_per_session: int = 3
    
    # 系统设置
    enable_cache: bool = True
    cache_duration: int = 3600  # 1小时
    
    @classmethod
    def from_env(cls) -> 'AdConfig':
        """从环境变量创建配置 - URL不可覆盖"""
        import os
        
        # 强制使用硬编码的URL，忽略环境变量
        return cls(
            sync_interval=int(os.getenv('AD_SYNC_INTERVAL', cls.sync_interval)),
            default_frequency=int(os.getenv('AD_DEFAULT_FREQUENCY', cls.default_frequency))
        )