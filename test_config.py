#!/usr/bin/env python3
"""
测试配置读取和API调用
"""

import sqlite3
import requests
import json

def test_database_config():
    """测试数据库配置读取"""
    print("=== 测试数据库配置读取 ===")
    
    try:
        conn = sqlite3.connect('app/settings.db')
        cursor = conn.cursor()
        cursor.execute('SELECT project_address, api_key FROM settings ORDER BY id DESC LIMIT 1')
        result = cursor.fetchone()
        conn.close()
        
        if result:
            project_address, api_key = result
            print(f"✓ 从数据库读取到配置:")
            print(f"  项目地址: {project_address}")
            print(f"  API密钥: {api_key}")
            return project_address, api_key
        else:
            print("✗ 数据库中没有配置信息")
            return None, None
    except Exception as e:
        print(f"✗ 读取数据库配置失败: {e}")
        return None, None

def test_api_connection(project_address, api_key):
    """测试API连接"""
    print(f"\n=== 测试API连接 ===")
    print(f"目标地址: {project_address}")
    print(f"API密钥: {api_key}")
    
    try:
        # 测试账号API
        api_url = f"{project_address.rstrip('/')}/api/accounts"
        headers = {
            'x-api-key': api_key,
            'Content-Type': 'application/json'
        }
        
        print(f"请求URL: {api_url}")
        print(f"请求头: {headers}")
        
        response = requests.get(api_url, headers=headers, timeout=10)
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                accounts = data.get('data', [])
                print(f"✓ API连接成功，获取到 {len(accounts)} 个账号")
                for account in accounts:
                    print(f"  - {account['username']} (ID: {account['id']})")
                return True
            else:
                print(f"✗ API返回错误: {data.get('error')}")
                return False
        else:
            print(f"✗ API请求失败，状态码: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"✗ 连接失败: {e}")
        return False
    except Exception as e:
        print(f"✗ API调用失败: {e}")
        return False

def test_share_parse(project_address, api_key):
    """测试分享链接解析"""
    print(f"\n=== 测试分享链接解析 ===")
    
    try:
        api_url = f"{project_address.rstrip('/')}/api/share/parse"
        headers = {
            'x-api-key': api_key,
            'Content-Type': 'application/json'
        }
        
        data = {
            'shareLink': 'test_share_1',
            'accountId': 1,
            'accessCode': None
        }
        
        print(f"请求URL: {api_url}")
        print(f"请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(api_url, headers=headers, json=data, timeout=10)
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                folders = result.get('data', [])
                print(f"✓ 分享链接解析成功，获取到 {len(folders)} 个目录")
                for folder in folders:
                    print(f"  - {folder['name']} (ID: {folder['id']})")
                return True
            else:
                print(f"✗ 分享链接解析失败: {result.get('error')}")
                return False
        else:
            print(f"✗ 分享链接解析请求失败，状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ 分享链接解析失败: {e}")
        return False

if __name__ == '__main__':
    print("开始测试配置和API功能...")
    
    # 1. 测试数据库配置读取
    project_address, api_key = test_database_config()
    
    if not project_address or not api_key:
        print("\n❌ 无法获取配置信息，测试终止")
        exit(1)
    
    # 2. 测试API连接
    api_success = test_api_connection(project_address, api_key)
    
    # 3. 测试分享链接解析
    parse_success = test_share_parse(project_address, api_key)
    
    # 总结
    print(f"\n=== 测试总结 ===")
    print(f"配置读取: {'✓' if project_address and api_key else '✗'}")
    print(f"API连接: {'✓' if api_success else '✗'}")
    print(f"分享解析: {'✓' if parse_success else '✗'}")
    
    if api_success and parse_success:
        print("\n🎉 所有测试通过！配置和API功能正常")
    else:
        print("\n❌ 部分测试失败，请检查配置和API服务器状态") 