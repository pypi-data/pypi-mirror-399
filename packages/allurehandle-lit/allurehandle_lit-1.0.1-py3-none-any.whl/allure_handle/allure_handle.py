# -*- coding:UTF-8 -*-
"""
Allure 报告处理工具类
轻量级 Allure 报告工具，最小依赖
"""
import json
import os
import allure
from typing import Dict, Optional


class AllureHandle:
    """Allure 报告处理工具类"""
    
    @staticmethod
    def add_request_to_report(method: str, url: str, headers: Dict = None, 
                             params: Dict = None, data: Dict = None, 
                             json_data: Dict = None):
        """
        添加请求信息到 Allure 报告
        
        Args:
            method: HTTP 方法
            url: 请求URL
            headers: 请求头
            params: URL参数
            data: 表单数据
            json_data: JSON数据
        """
        with allure.step(f"请求信息: {method} {url}"):
            request_info = {
                "Method": method,
                "URL": url
            }
            
            if headers:
                request_info["Headers"] = headers
            if params:
                request_info["Params"] = params
            if data:
                request_info["Data"] = data
            if json_data:
                request_info["JSON"] = json_data
            
            allure.attach(
                json.dumps(request_info, indent=2, ensure_ascii=False),
                name="请求信息",
                attachment_type=allure.attachment_type.JSON
            )
    
    @staticmethod
    def add_response_to_report(status_code: int, response_json: Dict = None, 
                               response_text: str = None, response_time: float = None):
        """
        添加响应信息到 Allure 报告
        
        Args:
            status_code: 状态码
            response_json: JSON响应
            response_text: 文本响应
            response_time: 响应时间（秒）
        """
        with allure.step(f"响应信息: {status_code}"):
            response_info = {
                "Status Code": status_code,
            }
            
            if response_time:
                response_info["Response Time"] = f"{response_time:.3f}s"
            
            if response_json:
                response_info["Response Body"] = response_json
                allure.attach(
                    json.dumps(response_json, indent=2, ensure_ascii=False),
                    name="响应内容 (JSON)",
                    attachment_type=allure.attachment_type.JSON
                )
            elif response_text:
                response_info["Response Body"] = response_text[:500]  # 限制长度
                allure.attach(
                    response_text,
                    name="响应内容 (Text)",
                    attachment_type=allure.attachment_type.TEXT
                )
            
            allure.attach(
                json.dumps(response_info, indent=2, ensure_ascii=False),
                name="响应信息",
                attachment_type=allure.attachment_type.JSON
            )
    
    @staticmethod
    def add_testdata_to_report(testdata: Dict, name: str = "测试数据"):
        """
        添加测试数据到 Allure 报告
        
        Args:
            testdata: 测试数据字典
            name: 附件名称
        """
        allure.attach(
            json.dumps(testdata, indent=2, ensure_ascii=False),
            name=name,
            attachment_type=allure.attachment_type.JSON
        )
    
    @staticmethod
    def add_case_result_to_report(call, report):
        """
        添加用例结果信息到 Allure 报告
        
        Args:
            call: pytest call 对象
            report: pytest report 对象
        """
        with allure.step("用例执行信息"):
            result_info = {
                "用例ID": report.nodeid,
                "测试结果": report.outcome,
                "用例耗时": f"{report.duration:.3f}s"
            }
            
            if report.longrepr:
                result_info["错误详情"] = str(report.longrepr)
            
            if call.excinfo:
                result_info["异常信息"] = str(call.excinfo)
            
            allure.attach(
                json.dumps(result_info, indent=2, ensure_ascii=False),
                name="用例执行信息",
                attachment_type=allure.attachment_type.JSON
            )
    
    @staticmethod
    def add_case_description_html(case_data: Dict):
        """
        添加用例描述HTML到 Allure 报告
        
        Args:
            case_data: 用例数据字典，包含以下字段：
                - case_id: 用例ID
                - case_module: 模块
                - case_name: 用例名称
                - case_priority: 优先级 (1-低, 2-中, 3-高)
                - case_setup: 前置条件
                - case_step: 测试步骤
                - case_expect_result: 预期结果
                - case_result: 测试结果
        """
        # 处理优先级显示
        priority_map = {1: '低', 2: '中', 3: '高'}
        case_data['case_priority'] = priority_map.get(
            case_data.get('case_priority'), 
            case_data.get('case_priority', '未知')
        )
        
        desc_html = '''<!doctype html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <title>用例详情</title>
    <style>
        table {{
            font-size: 12px;
            color: #333;
            width: 100%;
            border-width: 1px;
            border-color: #000;
            border-collapse: collapse;
        }}
        th {{
            font-size: 12px;
            border-width: 1px;
            padding: 8px;
            border-style: solid;
            border-color: #000;
            text-align: left;
            background-color: #b1cfea;
        }}
        td {{
            font-size: 12px;
            border-width: 1px;
            padding: 8px;
            border-style: solid;
            border-color: #000;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
    </style>
</head>
<body>
    <table>
        <tr>
            <th>ID</th>
            <th>模块</th>
            <th>用例名称</th>
            <th>优先级</th>
            <th>前置条件</th>
            <th>测试步骤</th>
            <th>预期结果</th>
            <th>测试结果</th>
        </tr>
        <tr>
            <td>{case_id}</td>
            <td>{case_module}</td>
            <td>{case_name}</td>
            <td>{case_priority}</td>
            <td>{case_setup}</td>
            <td>{case_step}</td>
            <td>{case_expect_result}</td>
            <td>{case_result}</td>
        </tr>
    </table>
</body>
</html>'''
        
        allure.dynamic.description_html(desc_html.format(**case_data))
    
    @staticmethod
    def add_step_with_attachment(title: str, content: str, attachment_type: str = "TEXT"):
        """
        添加步骤并附加内容到 Allure 报告
        
        Args:
            title: 步骤标题
            content: 内容
            attachment_type: 附件类型 (TEXT, JSON, HTML等)
        """
        with allure.step(title):
            attach_type_map = {
                "TEXT": allure.attachment_type.TEXT,
                "JSON": allure.attachment_type.JSON,
                "HTML": allure.attachment_type.HTML,
            }
            attach_type = attach_type_map.get(attachment_type.upper(), allure.attachment_type.TEXT)
            
            allure.attach(content, name=title, attachment_type=attach_type)
    
    @staticmethod
    def add_file_to_report(file_path: str, name: str = None):
        """
        添加文件到 Allure 报告
        
        Args:
            file_path: 文件路径
            name: 附件名称（可选）
        """
        if not os.path.exists(file_path):
            return
        
        file_name = name or os.path.basename(file_path)
        
        # 根据文件扩展名确定附件类型
        ext = os.path.splitext(file_path)[1].lower()
        attach_type_map = {
            '.png': allure.attachment_type.PNG,
            '.jpg': allure.attachment_type.JPG,
            '.jpeg': allure.attachment_type.JPG,
            '.json': allure.attachment_type.JSON,
            '.html': allure.attachment_type.HTML,
            '.xml': allure.attachment_type.XML,
            '.txt': allure.attachment_type.TEXT,
            '.log': allure.attachment_type.TEXT,
        }
        attach_type = attach_type_map.get(ext, allure.attachment_type.TEXT)
        
        allure.attach.file(file_path, name=file_name, attachment_type=attach_type)
    
    @staticmethod
    def add_log_to_report(log_content: str, name: str = "日志信息"):
        """
        添加日志内容到 Allure 报告
        
        Args:
            log_content: 日志内容
            name: 附件名称
        """
        allure.attach(
            log_content,
            name=name,
            attachment_type=allure.attachment_type.TEXT
        )


# 创建全局实例，方便使用
allure_handle = AllureHandle()

