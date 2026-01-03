# -*- coding:UTF-8 -*-
"""
Allure Handle - 轻量级 Allure 报告工具
"""
from setuptools import setup, find_packages
import os

# 读取 README 文件
def read_readme():
    # 优先读取 allure_handle 目录下的 README
    readme_paths = [
        os.path.join(os.path.dirname(__file__), 'allure_handle', 'README.md'),
        os.path.join(os.path.dirname(__file__), 'README.md'),
    ]
    for readme_path in readme_paths:
        if os.path.exists(readme_path):
            with open(readme_path, 'r', encoding='utf-8') as f:
                return f.read()
    return "轻量级 Allure 报告处理工具，用于 pytest 测试框架"

setup(
    name='allurehandle-lit',
    version='1.0.0',
    description='轻量级 Allure 报告处理工具，用于 pytest 测试框架',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='Lit',
    author_email='',
    url='https://github.com/Aquarius-0455/Allurehandle-Lit',
    packages=['allure_handle'],
    include_package_data=False,  # 不需要包含额外文件
    python_requires='>=3.7',
    install_requires=[
        'allure-pytest>=2.13.0',  # 只需要 allure-pytest
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    keywords='allure pytest testing report',
)
