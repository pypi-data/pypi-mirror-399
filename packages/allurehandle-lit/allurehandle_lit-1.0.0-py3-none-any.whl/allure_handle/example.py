# -*- coding:UTF-8 -*-
"""
Allure Handle 使用示例
"""
import pytest
import allure
from allure_handle import AllureHandle


@pytest.mark.order(1)
@allure.epic("示例模块")
class TestExample:
    """使用示例"""
    
    def test_with_testdata(self):
        """示例：添加测试数据"""
        testdata = {
            "username": "test_user",
            "email": "test@example.com"
        }
        AllureHandle.add_testdata_to_report(testdata, "用户注册数据")
    
    def test_with_request_response(self):
        """示例：添加请求和响应信息"""
        # 添加请求信息
        AllureHandle.add_request_to_report(
            method='POST',
            url='https://api.example.com/users',
            headers={'Authorization': 'Bearer token'},
            json_data={'name': 'test'}
        )
        
        # 模拟响应
        response_data = {'id': 1, 'name': 'test'}
        
        # 添加响应信息
        AllureHandle.add_response_to_report(
            status_code=200,
            response_json=response_data,
            response_time=0.123
        )
    
    def test_with_case_description(self):
        """示例：添加用例描述HTML"""
        case_data = {
            'case_id': 'TC001',
            'case_module': '用户管理',
            'case_name': '创建用户',
            'case_priority': 3,  # 1-低, 2-中, 3-高
            'case_setup': '系统已登录',
            'case_step': '1. 准备数据\n2. 调用接口\n3. 验证结果',
            'case_expect_result': '用户创建成功',
            'case_result': 'passed'
        }
        AllureHandle.add_case_description_html(case_data)
    
    def test_with_steps(self):
        """示例：添加步骤和附件"""
        with allure.step("步骤1: 准备数据"):
            data = {"key": "value"}
            AllureHandle.add_testdata_to_report(data, "准备的数据")
        
        with allure.step("步骤2: 执行操作"):
            AllureHandle.add_step_with_attachment(
                title="操作结果",
                content='{"status": "success"}',
                attachment_type="JSON"
            )

