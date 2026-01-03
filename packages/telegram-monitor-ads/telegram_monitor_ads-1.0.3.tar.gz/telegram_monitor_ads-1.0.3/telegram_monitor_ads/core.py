"""
广告系统核心模块
"""

import asyncio
import hashlib
import json
import logging
import random
import httpx
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from .config import AdConfig
from .exceptions import AdSystemError

logger = logging.getLogger(__name__)


class AdManager:
    """广告管理器 - 系统核心组件"""
    
    def __init__(self, config: AdConfig):
        self.config = config
        self.message_count = 0
        self.last_ad_display = 0
        self._remote_ads = []
        self._header = {}
        self._buttons = []
        self._last_sync = 0
        self._sync_task = None
    
    async def _start_sync_task(self):
        """启动同步任务"""
        await asyncio.sleep(5)  # 等待系统初始化
        
        while True:
            try:
                await self._sync_remote_ads()
                await asyncio.sleep(self.config.sync_interval)
            except Exception as e:
                logger.error(f"广告同步失败: {e}")
                await asyncio.sleep(60)
    
    def start_sync(self):
        """启动同步任务（非异步版本）"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果事件循环已在运行，创建任务
                self._sync_task = asyncio.create_task(self._start_sync_task())
            else:
                # 否则直接运行
                loop.create_task(self._start_sync_task())
        except RuntimeError:
            # 没有事件循环，创建一个
            pass
    
    async def _sync_remote_ads(self):
        """同步远程广告"""
        try:
            # 尝试主URL
            config_data = await self._fetch_config(self.config.primary_url)
            
            if not config_data:
                # 尝试备用URL
                config_data = await self._fetch_config(self.config.backup_url)
            
            if config_data and self._validate_config(config_data):
                self._remote_ads = config_data.get('ads', [])
                self._header = config_data.get('header', {})
                self._buttons = config_data.get('buttons', [])
                logger.info(f"同步了 {len(self._remote_ads)} 个广告")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"同步广告配置失败: {e}")
            return False
    
    async def _fetch_config(self, url: str) -> Optional[Dict]:
        """获取远程配置"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"获取配置失败 {url}: {e}")
            return None
    
    def _validate_config(self, config: Dict) -> bool:
        """验证配置"""
        required_fields = ['version', 'ads', 'system_check']
        return all(field in config for field in required_fields)
    
    def should_display_ad(self) -> bool:
        """判断是否显示广告"""
        self.message_count += 1
        
        if not self._remote_ads:
            return False
        
        # 根据频率判断
        min_frequency = min(ad.get('frequency', 10) for ad in self._remote_ads)
        
        if self.message_count - self.last_ad_display >= min_frequency:
            self.last_ad_display = self.message_count
            return True
        
        return False
    
    async def get_current_ad(self) -> Optional[str]:
        """获取当前广告"""
        try:
            if not self._remote_ads:
                return self._get_default_ad()
            
            # 筛选活跃广告
            active_ads = [ad for ad in self._remote_ads if self._is_ad_active(ad)]
            
            if not active_ads:
                return self._get_default_ad()
            
            # 按优先级选择
            selected_ad = self._select_by_priority(active_ads)
            return self._format_ad(selected_ad)
            
        except Exception as e:
            logger.error(f"获取广告失败: {e}")
            return self._get_default_ad()
    
    def _is_ad_active(self, ad: Dict) -> bool:
        """检查广告是否活跃"""
        if not ad.get('is_active', True):
            return False
        
        now = datetime.now()
        
        # 检查开始时间
        if ad.get('start_time'):
            try:
                start_time = datetime.fromisoformat(ad['start_time'].replace('Z', '+00:00'))
                if now < start_time:
                    return False
            except:
                pass
        
        # 检查结束时间
        if ad.get('end_time'):
            try:
                end_time = datetime.fromisoformat(ad['end_time'].replace('Z', '+00:00'))
                if now > end_time:
                    return False
            except:
                pass
        
        return True
    
    def _select_by_priority(self, ads: List[Dict]) -> Dict:
        """按优先级选择广告"""
        if not ads:
            return {}
        
        total_priority = sum(ad.get('priority', 1) for ad in ads)
        if total_priority == 0:
            return random.choice(ads)
        
        rand_val = random.randint(1, total_priority)
        current_weight = 0
        
        for ad in ads:
            current_weight += ad.get('priority', 1)
            if rand_val <= current_weight:
                return ad
        
        return ads[0]
    
    def _format_ad(self, ad: Dict) -> str:
        """格式化广告 - 链接格式"""
        content = ad.get('content', '')
        url = ad.get('url', '')
        
        if url:
            # 链接格式：一行一个
            return f"🔗 [{content}]({url})"
        else:
            return content
    
    def _get_default_ad(self) -> str:
        """默认广告"""
        return """
📢 **TelegramMonitor-Python**
🔗 开源地址: https://github.com/your-repo
💬 交流群: @your_group
⭐ 觉得好用请给个Star!
"""
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        active_ads = [ad for ad in self._remote_ads if self._is_ad_active(ad)]
        
        return {
            'total_ads': len(self._remote_ads),
            'active_ads': len(active_ads),
            'message_count': self.message_count,
            'last_ad_display': self.last_ad_display,
            'last_sync': self._last_sync
        }
    
    def get_header(self) -> Dict:
        """获取标题配置"""
        return self._header
    
    def get_buttons(self) -> List[Dict]:
        """获取按钮配置"""
        return self._buttons

    def get_ads(self) -> List[Dict]:
        """获取广告链接配置"""
        return self._remote_ads


class AdService:
    """广告服务"""
    
    def __init__(self, manager: AdManager):
        self.manager = manager
    
    def should_display_ad(self) -> bool:
        """是否应该显示广告"""
        return self.manager.should_display_ad()
    
    async def get_current_ad(self) -> Optional[str]:
        """获取当前广告"""
        return await self.manager.get_current_ad()
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return self.manager.get_stats()