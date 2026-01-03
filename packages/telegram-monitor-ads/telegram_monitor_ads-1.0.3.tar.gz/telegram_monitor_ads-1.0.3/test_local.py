#!/usr/bin/env python3
"""
本地测试脚本
"""

import asyncio
import sys
from pathlib import Path

# 添加本地包路径
sys.path.insert(0, str(Path(__file__).parent))

async def test_package():
    """测试包功能"""
    print("🧪 测试 telegram-monitor-ads 包...")
    
    try:
        # 1. 测试导入
        print("\n1️⃣ 测试导入...")
        from telegram_monitor_ads import AdManager, AdConfig, AdService
        from telegram_monitor_ads import verify_installation
        print("✅ 导入成功")
        
        # 2. 测试验证
        print("\n2️⃣ 测试验证...")
        if verify_installation():
            print("✅ 验证通过")
        else:
            print("❌ 验证失败")
            return False
        
        # 3. 测试配置
        print("\n3️⃣ 测试配置...")
        config = AdConfig()
        print(f"   主URL: {config.primary_url}")
        print(f"   备用URL: {config.backup_url}")
        print(f"   同步间隔: {config.sync_interval}秒")
        print("✅ 配置创建成功")
        
        # 4. 测试广告管理器
        print("\n4️⃣ 测试广告管理器...")
        manager = AdManager(config)
        print("✅ 广告管理器创建成功")
        
        # 5. 测试广告服务
        print("\n5️⃣ 测试广告服务...")
        service = AdService(manager)
        print("✅ 广告服务创建成功")
        
        # 6. 测试功能
        print("\n6️⃣ 测试基本功能...")
        
        # 模拟消息计数
        for i in range(15):
            should_show = service.should_display_ad()
            if should_show:
                print(f"   第{i+1}条消息: 🎯 显示广告")
                break
        else:
            print("   📝 未触发广告显示（正常）")
        
        # 7. 测试获取广告
        print("\n7️⃣ 测试获取广告...")
        ad_content = await service.get_current_ad()
        if ad_content:
            print("   ✅ 获取到广告内容:")
            print(f"   {ad_content[:100]}...")
        else:
            print("   📝 未获取到广告内容（可能正常）")
        
        # 8. 测试统计
        print("\n8️⃣ 测试统计...")
        stats = service.get_stats()
        print(f"   统计信息: {stats}")
        
        print("\n🎉 所有测试通过!")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_package())
    sys.exit(0 if success else 1)