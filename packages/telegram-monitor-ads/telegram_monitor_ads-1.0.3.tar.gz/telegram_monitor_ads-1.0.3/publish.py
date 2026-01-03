#!/usr/bin/env python3
"""
发布脚本 - 构建并发布到PyPI
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, check=True):
    """运行命令"""
    print(f"执行: {cmd}")
    result = subprocess.run(cmd, shell=True, check=check)
    return result.returncode == 0

def clean_build():
    """清理构建文件"""
    print("🧹 清理构建文件...")
    
    dirs_to_clean = ['build', 'dist', '*.egg-info']
    for pattern in dirs_to_clean:
        if '*' in pattern:
            import glob
            for path in glob.glob(pattern):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                    print(f"删除目录: {path}")
        else:
            if os.path.exists(pattern):
                shutil.rmtree(pattern)
                print(f"删除目录: {pattern}")

def build_package():
    """构建包"""
    print("📦 构建包...")
    
    if not run_command("python -m build"):
        print("❌ 构建失败")
        return False
    
    print("✅ 构建成功")
    return True

def upload_to_pypi():
    """上传到PyPI"""
    print("🚀 上传到PyPI...")
    
    if not run_command("python -m twine upload dist/*"):
        print("❌ 上传失败")
        return False
    
    print("✅ 上传成功")
    return True

def test_install():
    """测试安装"""
    print("🧪 测试安装...")
    
    # 等待PyPI更新
    import time
    print("等待PyPI更新...")
    time.sleep(10)
    
    if not run_command("pip install --upgrade telegram-monitor-ads"):
        print("❌ 安装测试失败")
        return False
    
    # 测试导入
    if not run_command("python -c 'import telegram_monitor_ads; print(f\"版本: {telegram_monitor_ads.__version__}\")'"):
        print("❌ 导入测试失败")
        return False
    
    print("✅ 测试成功")
    return True

def main():
    """主函数"""
    print("🚀 开始发布 telegram-monitor-ads 包...")
    
    # 检查必要工具
    required_tools = ['build', 'twine']
    for tool in required_tools:
        if not run_command(f"python -m {tool} --help", check=False):
            print(f"❌ 缺少工具: {tool}")
            print(f"请安装: pip install {tool}")
            return False
    
    try:
        # 1. 清理
        clean_build()
        
        # 2. 构建
        if not build_package():
            return False
        
        # 3. 上传
        if not upload_to_pypi():
            return False
        
        # 4. 测试
        if not test_install():
            return False
        
        print("🎉 发布完成!")
        return True
        
    except KeyboardInterrupt:
        print("\n❌ 用户取消")
        return False
    except Exception as e:
        print(f"❌ 发布失败: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)