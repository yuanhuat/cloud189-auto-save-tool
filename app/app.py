from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os
import requests
import json

app = Flask(__name__)

def init_db():
    """初始化数据库，创建设置表"""
    conn = sqlite3.connect('settings.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_address TEXT,
            api_key TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_settings():
    """获取最新的设置信息"""
    conn = sqlite3.connect('settings.db')
    cursor = conn.cursor()
    cursor.execute('SELECT project_address, api_key FROM settings ORDER BY id DESC LIMIT 1')
    result = cursor.fetchone()
    conn.close()
    if result:
        return {'project_address': result[0], 'api_key': result[1]}
    return {'project_address': '', 'api_key': ''}

def save_settings(project_address, api_key):
    """保存设置信息到数据库"""
    conn = sqlite3.connect('settings.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO settings (project_address, api_key)
        VALUES (?, ?)
    ''', (project_address, api_key))
    conn.commit()
    conn.close()

def get_accounts(project_address, api_key):
    """调用API获取账号信息"""
    try:
        # 构建API URL
        api_url = f"{project_address.rstrip('/')}/api/accounts"
        
        # 设置请求头 - 使用x-api-key认证方式
        headers = {
            'x-api-key': api_key,
            'Content-Type': 'application/json'
        }
        
        # 发送GET请求
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('data', [])
            else:
                print(f"API返回错误: {data}")
                return []
        else:
            print(f"API请求失败，状态码: {response.status_code}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"API请求异常: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        return []
    except Exception as e:
        print(f"获取账号信息时出错: {e}")
        return []

def get_favorites(project_address, api_key, account_id):
    """调用API获取常用目录"""
    try:
        # 构建API URL
        api_url = f"{project_address.rstrip('/')}/api/favorites/{account_id}"
        
        # 设置请求头
        headers = {
            'x-api-key': api_key,
            'Content-Type': 'application/json'
        }
        
        # 发送GET请求
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('data', [])
            else:
                print(f"API返回错误: {data}")
                return []
        else:
            print(f"API请求失败，状态码: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"获取常用目录时出错: {e}")
        return []

def create_task(project_address, api_key, share_link, account_id, target_folder_id, target_folder_path, overwrite_folder=False, selected_folders=None):
    """调用API创建任务"""
    try:
        api_url = f"{project_address.rstrip('/')}/api/tasks"
        headers = {
            'x-api-key': api_key,
            'Content-Type': 'application/json'
        }
        data = {
            'shareLink': share_link,
            'accountId': int(account_id),
            'targetFolderId': target_folder_id,
            'targetFolder': target_folder_path,
            'overwriteFolder': overwrite_folder
        }
        
        # 如果提供了选中的文件夹，添加到请求中
        if selected_folders:
            data['selectedFolders'] = selected_folders
            
        print(f"发送任务创建请求: {data}")
        response = requests.post(api_url, headers=headers, json=data, timeout=10)
        print(f"API响应状态码: {response.status_code}")
        print(f"API响应内容: {response.text}")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return {'success': True, 'message': '任务创建成功', 'data': result.get('data')}
            else:
                return {'success': False, 'message': result.get('error', '任务创建失败')}
        else:
            return {'success': False, 'message': f'API请求失败，状态码: {response.status_code}'}
    except Exception as e:
        print(f"创建任务时出错: {e}")
        return {'success': False, 'message': f'创建任务时出错: {str(e)}'}

def get_directory_tree(project_address, api_key, account_id, folder_id):
    """调用API获取目录树"""
    try:
        api_url = f"{project_address.rstrip('/')}/api/folders/{account_id}?folderId={folder_id}"
        headers = {
            'x-api-key': api_key
        }
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return {'success': True, 'data': result.get('data', [])}
            else:
                return {'success': False, 'message': result.get('error', '获取目录树失败')}
        else:
            return {'success': False, 'message': f'API请求失败，状态码: {response.status_code}'}
    except Exception as e:
        print(f"获取目录树时出错: {e}")
        return {'success': False, 'message': f'获取目录树时出错: {str(e)}'}

def parse_share_link(project_address, api_key, share_link, account_id, access_code=None):
    """解析分享链接获取所有可用目录"""
    try:
        api_url = f"{project_address.rstrip('/')}/api/share/parse"
        headers = {
            'x-api-key': api_key,
            'Content-Type': 'application/json'
        }
        data = {
            'shareLink': share_link,
            'accountId': int(account_id)
        }
        if access_code:
            data['accessCode'] = access_code
            
        print(f"解析分享链接: {data}")
        response = requests.post(api_url, headers=headers, json=data, timeout=10)
        print(f"解析响应状态码: {response.status_code}")
        print(f"解析响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return {'success': True, 'data': result.get('data', [])}
            else:
                return {'success': False, 'message': result.get('error', '解析分享链接失败')}
        else:
            return {'success': False, 'message': f'API请求失败，状态码: {response.status_code}'}
    except Exception as e:
        print(f"解析分享链接时出错: {e}")
        return {'success': False, 'message': f'解析分享链接时出错: {str(e)}'}

@app.route('/api/directories/<int:account_id>')
def get_directory_tree_api(account_id):
    """获取目录树的API接口"""
    settings = get_settings()
    if not settings.get('project_address') or not settings.get('api_key'):
        return jsonify({'success': False, 'message': '请先配置项目地址和API Key'})
    
    folder_id = request.args.get('folderId', '-11')
    result = get_directory_tree(settings['project_address'], settings['api_key'], account_id, folder_id)
    return jsonify(result)

@app.route('/api/parse-share', methods=['POST'])
def parse_share():
    """解析分享链接获取所有可用目录"""
    try:
        data = request.get_json()
        share_link = data.get('share_link')
        account_id = data.get('account_id')
        access_code = data.get('access_code')
        
        if not share_link or not account_id:
            return jsonify({'success': False, 'message': '分享链接和账号ID不能为空'})
        
        settings = get_settings()
        if not settings:
            return jsonify({'success': False, 'message': '请先配置项目地址和API密钥'})
        
        result = parse_share_link(settings['project_address'], settings['api_key'], 
                                share_link, account_id, access_code)
        return jsonify(result)
    except Exception as e:
        print(f"解析分享链接时出错: {e}")
        return jsonify({'success': False, 'message': f'解析分享链接时出错: {str(e)}'})

@app.route('/', methods=['GET', 'POST'])
def index():
    """渲染首页，包含分享链接填写和配置入口"""
    if request.method == 'POST':
        share_link = request.form.get('share_link')
        account_id = request.form.get('account_id')
        save_path = request.form.get('save_path')
        overwrite_folder = request.form.get('overwrite_folder') == 'on'
        
        # 解析save_path，格式为"folderId|path"
        if '|' in save_path:
            target_folder_id, target_folder_path = save_path.split('|', 1)
        else:
            # 兼容旧格式
            target_folder_id = save_path
            target_folder_path = save_path

        # 获取选中的分享目录
        selected_folders = request.form.getlist('selected_folders')
        if not selected_folders:
            # 如果没有选择任何目录，默认选择所有目录（包括根目录）
            selected_folders = ['-1']  # -1表示根目录

        print(f"任务创建参数:")
        print(f"  share_link: {share_link}")
        print(f"  account_id: {account_id}")
        print(f"  target_folder_id: {target_folder_id}")
        print(f"  target_folder_path: {target_folder_path}")
        print(f"  overwrite_folder: {overwrite_folder}")
        print(f"  selected_folders: {selected_folders}")

        # 获取设置信息
        settings = get_settings()
        
        if not settings.get('project_address') or not settings.get('api_key'):
            return render_template('index.html', message="请先配置项目地址和API Key")
        
        if not share_link:
            return render_template('index.html', message="请输入分享链接")
        
        if not account_id:
            return render_template('index.html', message="请选择账号")
        
        if not save_path:
            return render_template('index.html', message="请选择保存目录")
        
        # 创建任务
        result = create_task(settings['project_address'], settings['api_key'],
                           share_link, account_id, target_folder_id, target_folder_path, overwrite_folder, selected_folders)
        
        # 获取账号信息用于显示
        accounts = get_accounts(settings['project_address'], settings['api_key'])
        
        return render_template('index.html', 
                             settings=settings, 
                             accounts=accounts,
                             message=result['message'],
                             task_result=result)
    
    # 获取当前设置信息
    settings = get_settings()
    
    # 如果有设置信息，尝试获取账号信息
    accounts = []
    if settings.get('project_address') and settings.get('api_key'):
        accounts = get_accounts(settings['project_address'], settings['api_key'])
    
    return render_template('index.html', settings=settings, accounts=accounts)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """渲染和处理设置页面，用于配置项目地址和API Key"""
    if request.method == 'POST':
        project_address = request.form.get('project_address')
        api_key = request.form.get('api_key')
        # 保存设置到数据库
        save_settings(project_address, api_key)
        print(f"Project Address: {project_address}, API Key: {api_key}")
        
        # 保存后立即获取账号信息
        accounts = get_accounts(project_address, api_key)
        
        # 获取当前设置信息并显示在表单中
        current_settings = get_settings()
        return render_template('settings.html', settings=current_settings, accounts=accounts, message="设置已保存")
    
    # 获取当前设置信息并显示在表单中
    current_settings = get_settings()
    
    # 如果有设置信息，尝试获取账号信息
    accounts = []
    if current_settings.get('project_address') and current_settings.get('api_key'):
        accounts = get_accounts(current_settings['project_address'], current_settings['api_key'])
    
    return render_template('settings.html', settings=current_settings, accounts=accounts)

@app.route('/api/accounts')
def get_accounts_api():
    """获取账号列表API"""
    settings = get_settings()
    if not settings.get('project_address') or not settings.get('api_key'):
        return jsonify({'success': False, 'message': '请先配置项目地址和API Key'})
    
    accounts = get_accounts(settings['project_address'], settings['api_key'])
    return jsonify({'success': True, 'data': accounts})

@app.route('/api/favorites/<int:account_id>')
def get_favorites_api(account_id):
    """获取指定账号的常用目录API"""
    settings = get_settings()
    if not settings.get('project_address') or not settings.get('api_key'):
        return jsonify({'success': False, 'message': '请先配置项目地址和API Key'})
    
    favorites = get_favorites(settings['project_address'], settings['api_key'], account_id)
    return jsonify({'success': True, 'data': favorites})

@app.route('/api/refresh-accounts')
def refresh_accounts():
    """刷新账号信息的API接口"""
    settings = get_settings()
    if not settings.get('project_address') or not settings.get('api_key'):
        return jsonify({'success': False, 'message': '请先配置项目地址和API Key'})
    
    accounts = get_accounts(settings['project_address'], settings['api_key'])
    return jsonify({'success': True, 'data': accounts})

@app.route('/test-directory')
def test_directory():
    """目录选择测试页面"""
    return send_from_directory('.', 'test_directory_ui.html')

# 在应用启动时初始化数据库
if not os.path.exists('settings.db'):
    init_db()

if __name__ == '__main__':
    app.run(debug=True)