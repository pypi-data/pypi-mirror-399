# Allure Handle - 轻量级 Allure 报告工具

> **轻量级、零依赖的 Allure 报告增强工具包**

一个专为 pytest + Allure 测试框架设计的工具包，提供便捷的 Allure 报告增强功能，让测试报告更加丰富和易读。

---

## ✨ 特性

- 🎯 **轻量级**：最小化依赖，只依赖 `allure-pytest`
- 🚀 **简单易用**：提供简洁的 API，快速集成到现有测试用例
- 📊 **报告增强**：支持测试数据、用例描述、步骤附件等丰富功能
- 🔧 **自动检测**：自动检测 Allure CLI 工具，无需手动配置
- 📦 **独立包**：可作为独立 pip 包安装和使用

---

## 📦 安装

### 方式1: 从 PyPI 安装（推荐）

```bash
pip install allurehandle-lit
```

### 方式2: 从 GitHub 安装

```bash
# 直接安装（推荐）
pip install git+https://github.com/Aquarius-0455/Allurehandle-Lit.git

# 或者指定分支/标签
pip install git+https://github.com/Aquarius-0455/Allurehandle-Lit.git@main
```

### 方式3: 从源码安装

```bash
# 克隆仓库
git clone https://github.com/Aquarius-0455/Allurehandle-Lit.git
cd Allurehandle-Lit

# 安装
pip install -e .
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install allurehandle-lit pytest allure-pytest
```

### 2. 在测试用例中使用

```python
import pytest
import allure
from allure_handle import AllureHandle

@pytest.mark.order(1)
@allure.epic("用户管理")
class TestUser:
    
    def test_create_user(self):
        """创建用户"""
        # 添加测试数据到报告
        testdata = {
            "username": "test_user",
            "email": "test@example.com"
        }
        AllureHandle.add_testdata_to_report(testdata, "创建用户测试数据")
        
        # 添加用例描述（HTML格式）
        case_data = {
            'case_id': 'TC_USER_001',
            'case_module': '用户管理',
            'case_name': '创建用户',
            'case_priority': 3,  # 1-低, 2-中, 3-高
            'case_setup': '系统已登录',
            'case_step': '1. 准备用户数据\n2. 调用创建用户接口\n3. 验证返回结果',
            'case_expect_result': '用户创建成功，返回用户信息',
            'case_result': 'passed'
        }
        AllureHandle.add_case_description_html(case_data)
        
        # 添加步骤附件
        with allure.step("调用创建用户接口"):
            # ... 你的测试代码 ...
            AllureHandle.add_step_with_attachment(
                title="创建结果",
                content="用户创建成功",
                attachment_type="TEXT"
            )
```

### 3. 运行测试并生成报告

```bash
# 运行测试
pytest --alluredir=reports/allure_results

# 生成并打开 Allure 报告
allure generate reports/allure_results -o reports/allure_reports --clean
allure open reports/allure_reports
```

---

## 📖 API 文档

### `AllureHandle.add_testdata_to_report(testdata, title="测试数据")`

将测试数据添加到 Allure 报告中。

**参数：**
- `testdata` (dict): 测试数据字典
- `title` (str): 数据标题，默认为 "测试数据"

**示例：**
```python
testdata = {"username": "test", "password": "123456"}
AllureHandle.add_testdata_to_report(testdata, "登录测试数据")
```

---

### `AllureHandle.add_case_description_html(case_data)`

添加格式化的用例描述到 Allure 报告中。

**参数：**
- `case_data` (dict): 用例数据字典，包含以下字段：
  - `case_id` (str): 用例ID
  - `case_module` (str): 用例模块
  - `case_name` (str): 用例名称
  - `case_priority` (int): 优先级（1-低, 2-中, 3-高）
  - `case_setup` (str): 前置条件
  - `case_step` (str): 测试步骤
  - `case_expect_result` (str): 预期结果
  - `case_result` (str): 测试结果（passed/failed/skipped）

**示例：**
```python
case_data = {
    'case_id': 'TC_001',
    'case_module': '用户管理',
    'case_name': '创建用户',
    'case_priority': 3,
    'case_setup': '系统已登录',
    'case_step': '1. 准备数据\n2. 调用接口',
    'case_expect_result': '创建成功',
    'case_result': 'passed'
}
AllureHandle.add_case_description_html(case_data)
```

---

### `AllureHandle.add_step_with_attachment(title, content, attachment_type="TEXT")`

添加步骤附件到 Allure 报告中。

**参数：**
- `title` (str): 附件标题
- `content` (str): 附件内容
- `attachment_type` (str): 附件类型，可选值：
  - `"TEXT"`: 文本
  - `"JSON"`: JSON 格式
  - `"HTML"`: HTML 格式
  - `"XML"`: XML 格式

**示例：**
```python
AllureHandle.add_step_with_attachment(
    title="响应结果",
    content='{"code": 200, "message": "success"}',
    attachment_type="JSON"
)
```

---

### `AllureHandle.generate_report(results_dir, report_dir, clean=True)`

生成 Allure 报告。

**参数：**
- `results_dir` (str): Allure 结果目录，默认为 `"reports/allure_results"`
- `report_dir` (str): 报告输出目录，默认为 `"reports/allure_reports"`
- `clean` (bool): 是否清理旧报告，默认为 `True`

**示例：**
```python
AllureHandle.generate_report(
    results_dir="reports/allure_results",
    report_dir="reports/allure_reports",
    clean=True
)
```

---

## 📁 项目结构

```
Allurehandle-Lit/
├── allure_handle/          # 核心包
│   ├── __init__.py
│   ├── allure_handle.py   # 主模块
│   ├── example.py          # 使用示例
│   └── README.md           # 包说明文档
├── demo_allure.py          # 完整演示文件（推荐）
├── README_DEMO.md          # Demo 使用说明
├── setup.py                # 安装配置
├── pyproject.toml          # 项目配置
├── MANIFEST.in             # 打包清单
├── requirements.txt         # 依赖列表
├── README.md               # 项目说明（本文件）
└── PACKAGE_INSTALL.md      # 打包安装指南
```

---

## 🔧 配置

### Allure CLI 工具检测

`AllureHandle` 会自动检测系统中是否安装了 Allure CLI 工具：

1. 首先检查环境变量 `ALLURE_HOME`
2. 然后检查系统 PATH
3. 如果未找到，会提示安装方法

**手动设置 Allure 路径：**
```python
import os
os.environ['ALLURE_HOME'] = '/path/to/allure'
```

---

## 📝 完整示例

查看 `allure_handle/example.py` 获取完整的使用示例。

---

## 🎯 运行 Demo 演示

项目包含一个完整的演示文件 `demo_allure.py`，可以直接运行查看效果。

### 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/Aquarius-0455/Allurehandle-Lit.git
cd Allurehandle-Lit

# 2. 安装依赖
pip install allurehandle-lit pytest allure-pytest

# 3. 运行 Demo（会自动生成报告）
python demo_allure.py
```

### Demo 功能

`demo_allure.py` 演示了以下功能：

- ✅ **测试数据展示** - 在报告中以表格形式展示测试数据
- ✅ **用例描述** - 格式化的 HTML 用例描述，包含用例ID、优先级等信息
- ✅ **步骤附件** - 支持 JSON、TEXT、HTML 等格式的附件
- ✅ **测试分类** - 使用 Epic、Feature、Story、Severity 进行分类
- ✅ **自动生成报告** - 运行后自动生成并打开 Allure 报告

### 手动生成报告

如果自动生成失败，可以手动生成：

```bash
# 运行测试生成结果
pytest demo_allure.py --alluredir=reports/allure_results -v

# 生成报告（需要先安装 Allure CLI）
allure generate reports/allure_results -o reports/allure_reports --clean

# 打开报告
allure open reports/allure_reports
```

### 安装 Allure CLI

如果还没有安装 Allure CLI，可以：

**Windows:**
```bash
# 使用 Scoop
scoop install allure

# 或使用 Chocolatey
choco install allure-commandline
```

**Mac:**
```bash
brew install allure
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-add-repository ppa:qameta/allure
sudo apt-get update
sudo apt-get install allure
```

更多安装方法请查看 [Allure 官方文档](https://docs.qameta.io/allure/)。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License

---

## 🔗 相关链接

- [Allure 官方文档](https://docs.qameta.io/allure/)
- [pytest 官方文档](https://docs.pytest.org/)
- [allure-pytest 文档](https://github.com/allure-framework/allure-python)

---

**作者：** Lit  
**最后更新：** 2024-12-31
