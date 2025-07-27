#!/usr/bin/env python3
"""
数据库修复脚本
"""

import sqlite3
import hashlib
import os

def fix_database():
    """修复数据库，确保所有表都存在"""
    print("🔧 开始修复数据库...")
    
    # 检查数据库文件是否存在
    db_path = 'settings.db'
    if os.path.exists(db_path):
        print(f"✅ 数据库文件存在: {db_path}")
    else:
        print(f"⚠️ 数据库文件不存在，将创建新文件: {db_path}")
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 创建设置表
        print("📋 创建 settings 表...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_address TEXT,
                api_key TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ settings 表创建成功")
        
        # 创建用户表
        print("👥 创建 users 表...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ users 表创建成功")
        
        # 检查是否需要创建默认管理员账户
        print("🔍 检查管理员账户...")
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = TRUE')
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            print("👤 创建默认管理员账户...")
            default_password = hashlib.sha256('admin123'.encode()).hexdigest()
            cursor.execute('''
                INSERT INTO users (username, password_hash, is_admin)
                VALUES (?, ?, ?)
            ''', ('admin', default_password, True))
            print("✅ 默认管理员账户创建成功")
            print("   用户名: admin")
            print("   密码: admin123")
        else:
            print(f"✅ 已存在 {admin_count} 个管理员账户")
        
        # 显示表结构
        print("\n📊 数据库表结构:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        for table in tables:
            print(f"   - {table[0]}")
        
        # 显示用户列表
        print("\n👥 用户列表:")
        cursor.execute('SELECT id, username, is_admin, created_at FROM users')
        users = cursor.fetchall()
        if users:
            for user in users:
                user_type = "管理员" if user[2] else "普通用户"
                print(f"   - ID: {user[0]}, 用户名: {user[1]}, 类型: {user_type}, 创建时间: {user[3]}")
        else:
            print("   - 暂无用户")
        
        # 显示设置信息
        print("\n⚙️ 设置信息:")
        cursor.execute('SELECT project_address, api_key FROM settings ORDER BY id DESC LIMIT 1')
        settings = cursor.fetchone()
        if settings:
            print(f"   - 项目地址: {settings[0]}")
            print(f"   - API密钥: {'*' * len(settings[1]) if settings[1] else '未设置'}")
        else:
            print("   - 暂无设置信息")
        
        # 提交更改
        conn.commit()
        print("\n🎉 数据库修复完成！")
        
    except Exception as e:
        print(f"❌ 数据库修复失败: {e}")
        conn.rollback()
    finally:
        conn.close()

def check_database():
    """检查数据库状态"""
    print("🔍 检查数据库状态...")
    
    try:
        conn = sqlite3.connect('settings.db')
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        print("📋 现有表:")
        for table in table_names:
            print(f"   ✅ {table}")
        
        # 检查必需的表
        required_tables = ['settings', 'users']
        missing_tables = [table for table in required_tables if table not in table_names]
        
        if missing_tables:
            print(f"❌ 缺失的表: {missing_tables}")
            return False
        else:
            print("✅ 所有必需的表都存在")
            return True
            
    except Exception as e:
        print(f"❌ 检查数据库失败: {e}")
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    print("🔧 数据库修复工具")
    print("=" * 50)
    
    # 检查数据库状态
    if not check_database():
        print("\n🔧 开始修复数据库...")
        fix_database()
    else:
        print("\n✅ 数据库状态正常，无需修复")
    
    print("\n💡 提示:")
    print("• 如果仍有问题，请删除 settings.db 文件重新启动应用")
    print("• 默认管理员账户: admin/admin123")
    print("• 建议首次登录后修改默认密码") 