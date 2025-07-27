#!/usr/bin/env python3
"""
测试定时任务功能
"""

import requests
import json

def test_cron_task():
    """测试定时任务功能"""
    base_url = "http://localhost:5000"
    
    print("⏰ 测试定时任务功能")
    print("=" * 50)
    
    # 测试数据
    test_data = {
        "accountId": 1,
        "shareLink": "https://cloud.189.cn/test_share",
        "targetFolderId": "test_folder_id",
        "targetFolder": "/test/path",
        "selectedFolders": ["-1"],
        "enableCron": True,
        "cronExpression": "0 */30 * * * *",  # 每30分钟执行
        "overwriteFolder": False
    }
    
    print("📋 测试定时任务创建...")
    print(f"请求数据: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        # 使用表单数据提交到根路径
        form_data = {
            'share_link': test_data['shareLink'],
            'account_id': str(test_data['accountId']),
            'save_path': f"{test_data['targetFolderId']}|{test_data['targetFolder']}",
            'overwrite_folder': 'on' if test_data['overwriteFolder'] else '',
            'enable_cron': 'on' if test_data['enableCron'] else '',
            'cron_expression': test_data['cronExpression']
        }
        
        # 添加选中的文件夹
        for folder in test_data['selectedFolders']:
            form_data[f'selected_folders'] = folder
        
        response = requests.post(f"{base_url}/", data=form_data)
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            # 检查响应内容
            content = response.text
            if "任务创建成功" in content:
                print("✅ 定时任务创建成功")
            elif "任务创建失败" in content:
                print("❌ 定时任务创建失败")
            elif "请先配置项目地址和API Key" in content:
                print("⚠️ 需要先配置项目地址和API密钥")
            elif "请输入分享链接" in content:
                print("⚠️ 分享链接不能为空")
            elif "请选择账号" in content:
                print("⚠️ 需要选择账号")
            elif "请选择保存目录" in content:
                print("⚠️ 需要选择保存目录")
            else:
                print("📄 响应内容预览:")
                print(content[:500] + "..." if len(content) > 500 else content)
        else:
            print(f"❌ 请求失败: {response.text}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    print("\n📝 Cron表达式示例:")
    print("• 每30分钟执行: 0 */30 * * * *")
    print("• 每天凌晨2点执行: 0 0 2 * * *")
    print("• 每2小时执行: 0 0 */2 * * *")
    print("• 每天9-18点整点执行: 0 0 9-18 * * *")
    print("• 每周一凌晨2点30分: 0 30 2 * * 1")
    print("• 每分钟执行: */1 * * * * *")
    print("• 每小时执行: 0 0 * * * *")

if __name__ == '__main__':
    test_cron_task() 