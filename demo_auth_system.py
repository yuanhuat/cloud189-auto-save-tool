#!/usr/bin/env python3
"""
用户认证系统演示
"""

import webbrowser
import time

def demo_auth_system():
    """演示用户认证系统特性"""
    print("🔐 用户认证系统演示")
    print("=" * 50)
    
    print("🎯 系统特性:")
    print("1. 🔐 用户认证")
    print("   - 用户注册和登录")
    print("   - 密码加密存储")
    print("   - Session管理")
    
    print("\n2. 👑 权限管理")
    print("   - 管理员权限")
    print("   - 普通用户权限")
    print("   - 页面访问控制")
    
    print("\n3. 🛡️ 安全特性")
    print("   - SHA256密码加密")
    print("   - 登录状态验证")
    print("   - 权限装饰器")
    
    print("\n4. 👥 用户管理")
    print("   - 用户列表查看")
    print("   - 用户删除功能")
    print("   - 管理员统计")
    
    print("\n🔧 默认账户:")
    print("• 管理员账户: admin/admin123")
    print("• 首次启动自动创建")
    print("• 建议首次登录后修改密码")
    
    print("\n📋 功能说明:")
    print("• 普通用户: 只能使用基本功能")
    print("• 管理员: 可以访问设置和用户管理")
    print("• 设置页面: 需要管理员权限")
    print("• 用户管理: 仅管理员可访问")
    
    print("\n💡 使用流程:")
    print("1. 访问首页查看当前状态")
    print("2. 点击'注册'创建新账户")
    print("3. 使用'登录'进入系统")
    print("4. 管理员可访问设置和用户管理")
    
    # 打开浏览器演示
    print("\n🌐 正在打开浏览器演示...")
    time.sleep(2)
    
    try:
        webbrowser.open('http://localhost:5000')
        print("✅ 浏览器已打开，请体验用户认证系统")
    except Exception as e:
        print(f"❌ 无法打开浏览器: {e}")
        print("请手动访问: http://localhost:5000")

def show_auth_features():
    """显示认证功能特性"""
    print("\n🚀 认证功能亮点:")
    print("=" * 30)
    
    print("✅ 安全性:")
    print("  - SHA256密码加密")
    print("  - Session安全管理")
    print("  - 权限验证装饰器")
    print("  - 防SQL注入")
    
    print("\n✅ 用户体验:")
    print("  - 现代化登录界面")
    print("  - 实时表单验证")
    print("  - 友好的错误提示")
    print("  - 响应式设计")
    
    print("\n✅ 管理功能:")
    print("  - 用户列表管理")
    print("  - 权限级别控制")
    print("  - 用户统计信息")
    print("  - 安全删除确认")

def show_usage_guide():
    """显示使用指南"""
    print("\n📖 使用指南:")
    print("=" * 20)
    
    print("🔐 登录系统:")
    print("1. 访问 http://localhost:5000")
    print("2. 点击右上角'登录'按钮")
    print("3. 输入用户名和密码")
    print("4. 点击'登录'按钮")
    
    print("\n📝 注册账户:")
    print("1. 点击右上角'注册'按钮")
    print("2. 填写用户名和密码")
    print("3. 确认密码")
    print("4. 点击'注册'按钮")
    
    print("\n⚙️ 管理员功能:")
    print("1. 使用管理员账户登录")
    print("2. 点击用户名下拉菜单")
    print("3. 选择'系统设置'或'用户管理'")
    print("4. 进行相应操作")
    
    print("\n🚪 退出登录:")
    print("1. 点击用户名下拉菜单")
    print("2. 选择'退出登录'")
    print("3. 系统将清除登录状态")

if __name__ == '__main__':
    demo_auth_system()
    show_auth_features()
    show_usage_guide() 