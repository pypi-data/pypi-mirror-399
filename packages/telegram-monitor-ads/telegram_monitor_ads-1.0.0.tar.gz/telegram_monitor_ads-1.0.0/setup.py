"""
广告模块安装脚本
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="telegram-monitor-ads",
    version="1.0.0",
    author="洛阳狼",
    author_email="hanwanlonga@gmail.com",
    description="TelegramMonitor广告管理模块",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/luoyanglang/telegram-monitor-ads",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "httpx>=0.24.0",
        "python-dateutil>=2.8.0",
    ],
    keywords="telegram, monitor, ads, advertisement",
    project_urls={
        "Bug Reports": "https://github.com/luoyanglang/telegram-monitor-ads/issues",
        "Source": "https://github.com/luoyanglang/telegram-monitor-ads",
    },
)