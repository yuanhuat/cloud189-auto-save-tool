#!/usr/bin/env python3
"""
测试Web界面基本功能
"""

import requests
import time

def test_web_interface():
    """测试Web界面基本功能"""
    base_url = "http://localhost:5000"
    
    print("开始测试Web界面基本功能...")
    
    # 1. 测试主页访问
    print("\n1. 测试主页访问...")
    try:
        response = requests.get(base_url)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("✓ 主页访问成功")
            # 检查页面内容是否包含关键元素
            content = response.text
            if "云盘自动保存" in content:
                print("✓ 页面标题正确")
            if "分享链接" in content:
                print("✓ 分享链接输入框存在")
            if "选择账号" in content:
                print("✓ 账号选择框存在")
            if "保存目录" in content:
                print("✓ 保存目录选择框存在")
            if "浏览目录" in content:
                print("✓ 浏览目录按钮存在")
            if "创建任务" in content:
                print("✓ 创建任务按钮存在")
        else:
            print(f"✗ 主页访问失败: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 主页访问失败: {e}")
        return False
    
    # 2. 测试设置页面
    print("\n2. 测试设置页面...")
    try:
        response = requests.get(f"{base_url}/settings")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("✓ 设置页面访问成功")
            content = response.text
            if "项目地址" in content and "API Key" in content:
                print("✓ 设置表单存在")
        else:
            print(f"✗ 设置页面访问失败: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 设置页面访问失败: {e}")
        return False
    
    print("\n✓ 基本界面测试通过！")
    print("\n🎉 现在你可以：")
    print("1. 访问 http://localhost:5000 查看主界面")
    print("2. 点击'设置'配置项目地址和API密钥")
    print("3. 输入分享链接并点击'解析链接'")
    print("4. 选择账号和保存目录")
    print("5. 点击'浏览目录'测试目录选择功能")
    print("6. 创建任务")
    
    return True

if __name__ == '__main__':
    # 等待Flask应用启动
    print("等待Flask应用启动...")
    time.sleep(3)
    
    success = test_web_interface()
    if not success:
        print("\n❌ 测试失败，请检查应用状态") 