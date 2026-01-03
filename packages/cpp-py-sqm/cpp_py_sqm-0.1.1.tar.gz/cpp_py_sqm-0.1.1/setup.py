from setuptools import setup, find_packages
import os

# 读取 README.md 作为长描述（解决中文乱码+文件不存在兼容）
def get_long_description():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "A C++-style simulation library for Python"

# 核心配置
setup(
    # 库的基本信息（必填）
    name="cpp_py_sqm",          # PyPI 上的唯一库名（先确认未被占用）
    version="0.1.1",        # 语义化版本号，每次发布需递增
    author="sqm",
    author_email="shiqianmo@126.com",
    description="A C++-style simulation library for Python（模拟C++风格的Python工具库）",
    long_description=get_long_description(),
    long_description_content_type="text/markdown", 
    
    # 打包配置（必填）
    packages=find_packages(),  # 自动识别 cpp/ 目录作为包
    include_package_data=True, # 包含包内非代码文件（如 README）
    python_requires=">=3.6",   # 支持的 Python 版本
    
    # 分类标签（帮助 PyPI 索引）
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    
    # 依赖（你的库无额外依赖，留空）
    install_requires=[],
)