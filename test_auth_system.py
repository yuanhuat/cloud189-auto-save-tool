#!/usr/bin/env python3
"""
用户认证系统测试脚本
"""

import requests
import json

def test_auth_system():
    """测试用户认证系统"""
    base_url = "http://localhost:5000"
    
    print("🔐 测试用户认证系统")
    print("=" * 50)
    
    # 测试1: 访问首页
    print("1. 📄 测试访问首页...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("   ✅ 首页访问成功")
        else:
            print(f"   ❌ 首页访问失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 首页访问异常: {e}")
    
    # 测试2: 访问登录页面
    print("\n2. 🔐 测试登录页面...")
    try:
        response = requests.get(f"{base_url}/login")
        if response.status_code == 200:
            print("   ✅ 登录页面访问成功")
        else:
            print(f"   ❌ 登录页面访问失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 登录页面访问异常: {e}")
    
    # 测试3: 访问注册页面
    print("\n3. 📝 测试注册页面...")
    try:
        response = requests.get(f"{base_url}/register")
        if response.status_code == 200:
            print("   ✅ 注册页面访问成功")
        else:
            print(f"   ❌ 注册页面访问失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 注册页面访问异常: {e}")
    
    # 测试4: 测试用户注册
    print("\n4. 👤 测试用户注册...")
    try:
        register_data = {
            'username': 'testuser',
            'password': 'test123456',
            'confirm_password': 'test123456'
        }
        response = requests.post(f"{base_url}/register", data=register_data)
        if response.status_code == 200:
            if "注册成功" in response.text:
                print("   ✅ 用户注册成功")
            elif "用户名已存在" in response.text:
                print("   ⚠️ 用户名已存在")
            else:
                print("   ❓ 注册结果未知")
        else:
            print(f"   ❌ 注册请求失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 注册请求异常: {e}")
    
    # 测试5: 测试用户登录
    print("\n5. 🔑 测试用户登录...")
    try:
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        response = requests.post(f"{base_url}/login", data=login_data)
        if response.status_code == 200:
            if "登录成功" in response.text:
                print("   ✅ 管理员登录成功")
            elif "用户名或密码错误" in response.text:
                print("   ❌ 管理员登录失败")
            else:
                print("   ❓ 登录结果未知")
        else:
            print(f"   ❌ 登录请求失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 登录请求异常: {e}")
    
    # 测试6: 测试设置页面访问（需要管理员权限）
    print("\n6. ⚙️ 测试设置页面访问...")
    try:
        response = requests.get(f"{base_url}/settings")
        if response.status_code == 200:
            print("   ✅ 设置页面访问成功")
        elif response.status_code == 302:  # 重定向到登录页面
            print("   ⚠️ 设置页面需要登录，已重定向到登录页面")
        else:
            print(f"   ❌ 设置页面访问失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 设置页面访问异常: {e}")
    
    # 测试7: 测试用户管理页面访问（需要管理员权限）
    print("\n7. 👥 测试用户管理页面访问...")
    try:
        response = requests.get(f"{base_url}/users")
        if response.status_code == 200:
            print("   ✅ 用户管理页面访问成功")
        elif response.status_code == 302:  # 重定向到登录页面
            print("   ⚠️ 用户管理页面需要登录，已重定向到登录页面")
        else:
            print(f"   ❌ 用户管理页面访问失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 用户管理页面访问异常: {e}")

def test_database_connection():
    """测试数据库连接"""
    print("\n🔍 测试数据库连接...")
    try:
        import sqlite3
        conn = sqlite3.connect('settings.db')
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        print("   📋 数据库表:")
        for table in table_names:
            print(f"      ✅ {table}")
        
        # 检查用户表
        if 'users' in table_names:
            cursor.execute('SELECT COUNT(*) FROM users')
            user_count = cursor.fetchone()[0]
            print(f"   👥 用户数量: {user_count}")
            
            cursor.execute('SELECT username, is_admin FROM users')
            users = cursor.fetchall()
            for user in users:
                user_type = "管理员" if user[1] else "普通用户"
                print(f"      - {user[0]} ({user_type})")
        
        # 检查设置表
        if 'settings' in table_names:
            cursor.execute('SELECT COUNT(*) FROM settings')
            settings_count = cursor.fetchone()[0]
            print(f"   ⚙️ 设置记录数: {settings_count}")
        
        conn.close()
        print("   ✅ 数据库连接正常")
        
    except Exception as e:
        print(f"   ❌ 数据库连接失败: {e}")

if __name__ == '__main__':
    print("🧪 用户认证系统测试")
    print("=" * 50)
    
    # 测试数据库连接
    test_database_connection()
    
    # 测试认证系统
    test_auth_system()
    
    print("\n🎉 测试完成！")
    print("\n💡 使用说明:")
    print("• 默认管理员账户: admin/admin123")
    print("• 访问 http://localhost:5000 开始使用")
    print("• 注册新用户或使用管理员账户登录") 