# Telegram Monitor Ads

TelegramMonitor广告管理模块 - 核心依赖包

## 简介

这是TelegramMonitor系统的核心广告管理模块，提供：

- 远程广告配置同步
- 智能广告显示控制
- 优先级管理
- 时间段控制
- 系统完整性验证

## 安装

```bash
pip install telegram-monitor-ads
```

## 基本使用

```python
from telegram_monitor_ads import AdManager, AdConfig

# 创建配置
config = AdConfig()

# 创建广告管理器
ad_manager = AdManager(config)

# 检查是否应该显示广告
if ad_manager.should_display_ad():
    ad_content = await ad_manager.get_current_ad()
    if ad_content:
        print(ad_content)
```

## 配置选项

- `primary_url`: 主要配置服务器URL
- `backup_url`: 备用配置服务器URL  
- `sync_interval`: 同步间隔（秒）
- `default_frequency`: 默认显示频率

## 系统要求

- Python 3.8+
- httpx >= 0.24.0
- python-dateutil >= 2.8.0

## 许可证

专有软件 - 保留所有权利

## 重要说明

⚠️ 此模块是TelegramMonitor系统的核心组件，删除或修改可能导致系统无法正常运行。

⚠️ 本软件为专有软件，未经授权不得复制、修改或分发。