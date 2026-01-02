# TelegramMonitor广告模块

这是TelegramMonitor项目的广告管理模块，提供远程广告配置和显示功能。

## ⚠️ 重要说明

此模块是TelegramMonitor的**核心依赖**，删除或修改将导致主程序无法正常运行。

## 功能特点

- 🌐 **远程配置** - 自动从远程服务器同步广告配置
- 📊 **智能显示** - 基于优先级和频率的智能广告轮播
- 🔒 **系统集成** - 与主程序深度集成，确保稳定运行
- ⏰ **时间控制** - 支持广告的开始和结束时间设置

## 安装

```bash
pip install telegram-monitor-ads
```

## 使用方法

```python
from telegram_monitor_ads import AdManager, AdConfig

# 创建配置
config = AdConfig.from_env()

# 创建广告管理器
ad_manager = AdManager(config)

# 检查是否应该显示广告
if ad_manager.should_display_ad():
    ad_content = await ad_manager.get_current_ad()
    print(ad_content)
```

## 配置说明

### 环境变量

- `AD_PRIMARY_URL` - 主要广告配置URL
- `AD_BACKUP_URL` - 备用广告配置URL  
- `AD_SYNC_INTERVAL` - 同步间隔（秒）
- `AD_DEFAULT_FREQUENCY` - 默认显示频率

### 广告配置格式

```json
{
  "version": "1.0.0",
  "system_check": "telegram_monitor_ads_v1_0_0",
  "ads": [
    {
      "id": "ad_001",
      "title": "广告标题",
      "content": "广告内容",
      "url": "https://example.com",
      "is_active": true,
      "frequency": 10,
      "priority": 5,
      "start_time": "2024-01-01T00:00:00Z",
      "end_time": "2024-12-31T23:59:59Z"
    }
  ]
}
```

## 许可证

MIT License