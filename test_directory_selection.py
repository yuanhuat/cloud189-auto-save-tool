#!/usr/bin/env python3
"""
测试目录选择功能
"""

import requests
import json

def test_directory_selection():
    """测试目录选择功能"""
    base_url = "http://localhost:5000"
    
    print("🔍 测试目录选择功能")
    print("=" * 50)
    
    # 1. 测试获取目录树API
    print("\n1. 测试获取目录树API...")
    try:
        response = requests.get(f"{base_url}/api/directories/1?folderId=-11")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            if data.get('success'):
                print("✅ 目录树API正常")
                directories = data.get('data', [])
                print(f"找到 {len(directories)} 个目录")
                for dir_item in directories:
                    print(f"  - {dir_item.get('name', 'Unknown')} (ID: {dir_item.get('id', 'Unknown')})")
            else:
                print(f"❌ 目录树API返回错误: {data.get('message')}")
        else:
            print(f"❌ 目录树API请求失败: {response.text}")
    except Exception as e:
        print(f"❌ 目录树API测试失败: {e}")
    
    # 2. 测试常用目录API
    print("\n2. 测试常用目录API...")
    try:
        response = requests.get(f"{base_url}/api/favorites/1")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            if data.get('success'):
                print("✅ 常用目录API正常")
                favorites = data.get('data', [])
                print(f"找到 {len(favorites)} 个常用目录")
                for fav in favorites:
                    print(f"  - {fav.get('name', 'Unknown')} (路径: {fav.get('path', 'Unknown')})")
            else:
                print(f"❌ 常用目录API返回错误: {data.get('message')}")
        else:
            print(f"❌ 常用目录API请求失败: {response.text}")
    except Exception as e:
        print(f"❌ 常用目录API测试失败: {e}")
    
    # 3. 测试分享链接解析API
    print("\n3. 测试分享链接解析API...")
    try:
        test_data = {
            'share_link': 'https://cloud.189.cn/test',
            'account_id': '1',
            'access_code': ''
        }
        response = requests.post(f"{base_url}/api/parse-share", 
                               json=test_data,
                               headers={'Content-Type': 'application/json'})
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            if data.get('success'):
                print("✅ 分享链接解析API正常")
                folders = data.get('data', [])
                print(f"找到 {len(folders)} 个分享目录")
                for folder in folders:
                    print(f"  - {folder.get('name', 'Unknown')} (ID: {folder.get('id', 'Unknown')})")
            else:
                print(f"❌ 分享链接解析API返回错误: {data.get('message')}")
        else:
            print(f"❌ 分享链接解析API请求失败: {response.text}")
    except Exception as e:
        print(f"❌ 分享链接解析API测试失败: {e}")
    
    print("\n📋 测试总结:")
    print("如果看到错误信息，可能的原因:")
    print("1. 目标API服务器未运行")
    print("2. 配置信息不正确")
    print("3. 网络连接问题")
    print("4. API接口格式不匹配")

if __name__ == '__main__':
    test_directory_selection() 