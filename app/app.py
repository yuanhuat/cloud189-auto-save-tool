from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
import sqlite3
import os
import requests
import json
import hashlib
import secrets
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # 生成随机密钥用于session

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect('settings.db')
    cursor = conn.cursor()
    
    # 创建设置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_address TEXT,
            api_key TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建账号-目录映射表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS account_directories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            account_name TEXT NOT NULL,
            target_folder_id TEXT NOT NULL,
            target_folder_path TEXT NOT NULL,
            folder_name TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建自动删除任务配置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS auto_delete_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT NOT NULL,
            days INTEGER NOT NULL DEFAULT 30,
            delete_cloud BOOLEAN DEFAULT FALSE,
            enabled BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 检查是否需要创建默认管理员账户
    cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = TRUE')
    admin_count = cursor.fetchone()[0]
    
    if admin_count == 0:
        # 创建默认管理员账户 (admin/admin123)
        default_password = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute('''
            INSERT INTO users (username, password_hash, is_admin)
            VALUES (?, ?, ?)
        ''', ('admin', default_password, True))
        print("✅ 已创建默认管理员账户: admin/admin123")
    
    # 插入默认自动删除配置
    default_configs = [
        ('pending', 30, False),    # 等待中任务30天后删除，不删除云盘文件
        ('processing', 60, False), # 追剧中任务60天后删除，不删除云盘文件
        ('completed', 90, True),   # 已完成任务90天后删除，删除云盘文件
        ('failed', 7, False)       # 失败任务7天后删除，不删除云盘文件
    ]
    
    for status, days, delete_cloud in default_configs:
        cursor.execute('SELECT * FROM auto_delete_config WHERE status = ?', (status,))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO auto_delete_config (status, days, delete_cloud, enabled) 
                VALUES (?, ?, ?, ?)
            ''', (status, days, delete_cloud, True))
    
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

def verify_user(username, password):
    """验证用户登录"""
    conn = sqlite3.connect('settings.db')
    cursor = conn.cursor()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute('SELECT id, username, is_admin FROM users WHERE username = ? AND password_hash = ?', 
                   (username, password_hash))
    user = cursor.fetchone()
    conn.close()
    return user

def create_user(username, password, is_admin=False):
    """创建新用户"""
    try:
        conn = sqlite3.connect('settings.db')
        cursor = conn.cursor()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute('INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)',
                       (username, password_hash, is_admin))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False  # 用户名已存在

def get_all_users():
    """获取所有用户列表（仅管理员）"""
    conn = sqlite3.connect('settings.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, is_admin, created_at FROM users ORDER BY created_at DESC')
    users = cursor.fetchall()
    conn.close()
    return users

def delete_user(user_id):
    """删除用户（仅管理员）"""
    try:
        conn = sqlite3.connect('settings.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def save_account_directory(account_id, account_name, target_folder_id, target_folder_path, folder_name):
    """保存账号-目录映射"""
    try:
        conn = sqlite3.connect('settings.db')
        cursor = conn.cursor()
        
        # 检查是否已存在该账号的映射
        cursor.execute('SELECT id FROM account_directories WHERE account_id = ?', (account_id,))
        existing = cursor.fetchone()
        
        if existing:
            # 更新现有映射
            cursor.execute('''
                UPDATE account_directories 
                SET target_folder_id = ?, target_folder_path = ?, folder_name = ?, 
                    updated_at = CURRENT_TIMESTAMP
                WHERE account_id = ?
            ''', (target_folder_id, target_folder_path, folder_name, account_id))
        else:
            # 创建新映射
            cursor.execute('''
                INSERT INTO account_directories (account_id, account_name, target_folder_id, target_folder_path, folder_name)
                VALUES (?, ?, ?, ?, ?)
            ''', (account_id, account_name, target_folder_id, target_folder_path, folder_name))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"保存账号-目录映射失败: {e}")
        return False

def get_account_directories():
    """获取所有账号-目录映射"""
    try:
        conn = sqlite3.connect('settings.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, account_id, account_name, target_folder_id, target_folder_path, 
                   folder_name, is_active, created_at, updated_at
            FROM account_directories 
            WHERE is_active = TRUE
            ORDER BY account_id
        ''')
        mappings = cursor.fetchall()
        conn.close()
        return mappings
    except Exception as e:
        print(f"获取账号-目录映射失败: {e}")
        return []

def get_account_directory(account_id):
    """获取指定账号的目录映射"""
    try:
        conn = sqlite3.connect('settings.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT target_folder_id, target_folder_path, folder_name
            FROM account_directories 
            WHERE account_id = ? AND is_active = TRUE
        ''', (account_id,))
        mapping = cursor.fetchone()
        conn.close()
        return mapping
    except Exception as e:
        print(f"获取账号目录映射失败: {e}")
        return None

def delete_account_directory(mapping_id):
    """删除账号-目录映射"""
    try:
        conn = sqlite3.connect('settings.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM account_directories WHERE id = ?', (mapping_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"删除账号-目录映射失败: {e}")
        return False

def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """管理员权限验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if not session.get('is_admin'):
            flash('需要管理员权限', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

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

def create_task(project_address, api_key, share_link, account_id, target_folder_id, target_folder_path, overwrite_folder=False, selected_folders=None, enable_cron=False, cron_expression=None):
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
        
        # 添加定时任务参数
        if enable_cron and cron_expression:
            data['enableCron'] = enable_cron
            data['cronExpression'] = cron_expression
            
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
        share_link = request.form.get('share_link', '').strip()
        batch_links = request.form.get('batch_links', '').strip()
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

        # 获取定时任务参数
        enable_cron = request.form.get('enable_cron') == 'on'
        cron_expression = request.form.get('cron_expression', '').strip()

        # 获取设置信息
        settings = get_settings()
        
        if not settings.get('project_address') or not settings.get('api_key'):
            return render_template('index.html', message="请先配置项目地址和API Key")
        
        if not account_id:
            return render_template('index.html', message="请选择账号")
        
        if not save_path:
            return render_template('index.html', message="请选择保存目录")
        
        # 验证定时任务参数
        if enable_cron and not cron_expression:
            return render_template('index.html', message="启用定时任务时必须填写Cron表达式")
        
        # 处理批量链接
        if batch_links:
            # 批量处理模式
            links = [line.strip() for line in batch_links.split('\n') if line.strip()]
            if not links:
                return render_template('index.html', message="请输入有效的批量分享链接")
            
            print(f"批量任务创建参数:")
            print(f"  链接数量: {len(links)}")
            print(f"  account_id: {account_id}")
            print(f"  target_folder_id: {target_folder_id}")
            print(f"  target_folder_path: {target_folder_path}")
            print(f"  overwrite_folder: {overwrite_folder}")
            print(f"  selected_folders: {selected_folders}")
            print(f"  enable_cron: {enable_cron}")
            print(f"  cron_expression: {cron_expression}")
            
            # 批量创建任务
            results = []
            for i, line in enumerate(links):
                # 解析链接和访问码
                parts = line.split()
                link = parts[0]
                link_access_code = parts[1] if len(parts) > 1 else ''
                
                print(f"  处理链接 {i+1}: {link}")
                result = create_task(settings['project_address'], settings['api_key'],
                                   link, account_id, target_folder_id, target_folder_path, 
                                   overwrite_folder, selected_folders, enable_cron, cron_expression)
                results.append(result)
            
            # 统计结果
            success_count = sum(1 for r in results if r.get('success'))
            fail_count = len(results) - success_count
            
            if success_count > 0:
                message = f"批量创建任务完成！成功: {success_count} 个，失败: {fail_count} 个"
                return render_template('index.html', message=message, task_result={'success': True})
            else:
                message = f"批量创建任务失败！所有 {len(results)} 个任务都创建失败"
                return render_template('index.html', message=message, task_result={'success': False})
        else:
            # 单个链接模式
            if not share_link:
                return render_template('index.html', message="请输入分享链接")
            
            print(f"单个任务创建参数:")
            print(f"  share_link: {share_link}")
            print(f"  account_id: {account_id}")
            print(f"  target_folder_id: {target_folder_id}")
            print(f"  target_folder_path: {target_folder_path}")
            print(f"  overwrite_folder: {overwrite_folder}")
            print(f"  selected_folders: {selected_folders}")
            print(f"  enable_cron: {enable_cron}")
            print(f"  cron_expression: {cron_expression}")
            
            # 创建单个任务
            result = create_task(settings['project_address'], settings['api_key'],
                               share_link, account_id, target_folder_id, target_folder_path, 
                               overwrite_folder, selected_folders, enable_cron, cron_expression)
        
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
    
    return render_template('index.html', settings=settings, accounts=accounts, 
                         user=session.get('username'), is_admin=session.get('is_admin'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('请输入用户名和密码', 'error')
            return render_template('login.html')
        
        user = verify_user(username, password)
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['is_admin'] = user[2]
            flash('登录成功！', 'success')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """注册页面"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not password:
            flash('请输入用户名和密码', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('两次输入的密码不一致', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('密码长度至少6位', 'error')
            return render_template('register.html')
        
        if create_user(username, password):
            flash('注册成功！请登录', 'success')
            return redirect(url_for('login'))
        else:
            flash('用户名已存在', 'error')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """退出登录"""
    session.clear()
    flash('已退出登录', 'info')
    return redirect(url_for('index'))

@app.route('/users')
@admin_required
def users():
    """用户管理页面（仅管理员）"""
    users_list = get_all_users()
    return render_template('users.html', users=users_list)

@app.route('/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user_route(user_id):
    """删除用户（仅管理员）"""
    if delete_user(user_id):
        flash('用户删除成功', 'success')
    else:
        flash('用户删除失败', 'error')
    return redirect(url_for('users'))

@app.route('/account-directories')
@admin_required
def account_directories():
    """账号-目录映射管理页面（仅管理员）"""
    mappings = get_account_directories()
    settings = get_settings()
    accounts = []
    if settings.get('project_address') and settings.get('api_key'):
        accounts = get_accounts(settings['project_address'], settings['api_key'])
    return render_template('account_directories.html', mappings=mappings, accounts=accounts, settings=settings)

@app.route('/account-directories/save', methods=['POST'])
@admin_required
def save_account_directory_route():
    """保存账号-目录映射（仅管理员）"""
    account_id = request.form.get('account_id')
    account_name = request.form.get('account_name')
    target_folder_id = request.form.get('target_folder_id')
    target_folder_path = request.form.get('target_folder_path')
    folder_name = request.form.get('folder_name')
    
    if not all([account_id, account_name, target_folder_id, target_folder_path, folder_name]):
        flash('请填写所有必填字段', 'error')
        return redirect(url_for('account_directories'))
    
    if save_account_directory(account_id, account_name, target_folder_id, target_folder_path, folder_name):
        flash('账号-目录映射保存成功', 'success')
    else:
        flash('账号-目录映射保存失败', 'error')
    
    return redirect(url_for('account_directories'))

@app.route('/account-directories/delete/<int:mapping_id>', methods=['POST'])
@admin_required
def delete_account_directory_route(mapping_id):
    """删除账号-目录映射（仅管理员）"""
    if delete_account_directory(mapping_id):
        flash('账号-目录映射删除成功', 'success')
    else:
        flash('账号-目录映射删除失败', 'error')
    return redirect(url_for('account_directories'))

@app.route('/api/account-directory/<int:account_id>')
def get_account_directory_api(account_id):
    """获取指定账号的目录映射API"""
    mapping = get_account_directory(account_id)
    if mapping:
        return jsonify({
            'success': True,
            'data': {
                'target_folder_id': mapping[0],
                'target_folder_path': mapping[1],
                'folder_name': mapping[2]
            }
        })
    else:
        return jsonify({
            'success': False,
            'message': '未找到该账号的目录映射'
        })

@app.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    """渲染和处理设置页面，用于配置项目地址和API Key（需要管理员权限）"""
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
    return render_template('test_directory.html')

# 在应用启动时初始化数据库
if not os.path.exists('settings.db'):
    init_db()

# 任务管理相关路由
@app.route('/tasks')
@admin_required
def tasks():
    """任务管理页面"""
    return render_template('tasks.html')

@app.route('/api/tasks')
@admin_required
def get_tasks():
    """获取任务列表"""
    try:
        settings = get_settings()
        project_address = settings.get('project_address')
        api_key = settings.get('api_key')
        
        if not project_address or not api_key:
            return jsonify({'success': False, 'error': '请先配置项目地址和API密钥'})
        
        # 获取查询参数
        status = request.args.get('status', 'all')
        search = request.args.get('search', '')
        
        # 构建API URL
        api_url = f"{project_address.rstrip('/')}/api/tasks"
        params = {}
        if status != 'all':
            params['status'] = status
        if search:
            params['search'] = search
        
        # 调用 cloud189-auto-save 的 API
        headers = {'x-api-key': api_key}
        response = requests.get(api_url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return jsonify(data)
        else:
            return jsonify({'success': False, 'error': f'API请求失败: {response.status_code}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@admin_required
def delete_task(task_id):
    """删除单个任务"""
    try:
        settings = get_settings()
        project_address = settings.get('project_address')
        api_key = settings.get('api_key')
        
        if not project_address or not api_key:
            return jsonify({'success': False, 'error': '请先配置项目地址和API密钥'})
        
        # 获取删除选项
        delete_cloud = request.json.get('deleteCloud', False) if request.json else False
        
        # 调用 cloud189-auto-save 的 API
        headers = {'x-api-key': api_key, 'Content-Type': 'application/json'}
        response = requests.delete(
            f"{project_address.rstrip('/')}/api/tasks/{task_id}", 
            headers=headers,
            json={'deleteCloud': delete_cloud}
        )
        
        if response.status_code == 200:
            data = response.json()
            return jsonify(data)
        else:
            return jsonify({'success': False, 'error': f'删除失败: {response.status_code}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/tasks/batch', methods=['DELETE'])
@admin_required
def delete_tasks_batch():
    """批量删除任务"""
    try:
        settings = get_settings()
        project_address = settings.get('project_address')
        api_key = settings.get('api_key')
        
        if not project_address or not api_key:
            return jsonify({'success': False, 'error': '请先配置项目地址和API密钥'})
        
        # 获取删除参数
        task_ids = request.json.get('taskIds', [])
        delete_cloud = request.json.get('deleteCloud', False)
        
        if not task_ids:
            return jsonify({'success': False, 'error': '请选择要删除的任务'})
        
        # 调用 cloud189-auto-save 的 API
        headers = {'x-api-key': api_key, 'Content-Type': 'application/json'}
        response = requests.delete(
            f"{project_address.rstrip('/')}/api/tasks/batch", 
            headers=headers,
            json={'taskIds': task_ids, 'deleteCloud': delete_cloud}
        )
        
        if response.status_code == 200:
            data = response.json()
            return jsonify(data)
        else:
            return jsonify({'success': False, 'error': f'批量删除失败: {response.status_code}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# 自动删除配置管理函数
def get_auto_delete_configs():
    """获取自动删除配置"""
    conn = sqlite3.connect('settings.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM auto_delete_config ORDER BY status')
    configs = cursor.fetchall()
    conn.close()
    
    return [
        {
            'id': row[0],
            'status': row[1],
            'days': row[2],
            'delete_cloud': bool(row[3]),
            'enabled': bool(row[4]),
            'created_at': row[5],
            'updated_at': row[6]
        }
        for row in configs
    ]

def update_auto_delete_config(config_id, days, delete_cloud, enabled):
    """更新自动删除配置"""
    conn = sqlite3.connect('settings.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE auto_delete_config 
        SET days = ?, delete_cloud = ?, enabled = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (days, delete_cloud, enabled, config_id))
    conn.commit()
    conn.close()

def get_tasks_for_auto_delete():
    """获取需要自动删除的任务"""
    try:
        settings = get_settings()
        project_address = settings.get('project_address')
        api_key = settings.get('api_key')
        
        if not project_address or not api_key:
            return []
        
        # 获取所有任务
        headers = {'x-api-key': api_key}
        response = requests.get(f"{project_address}/api/tasks", headers=headers, timeout=10)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        if not data.get('success'):
            return []
        
        tasks = data.get('data', [])
        configs = get_auto_delete_configs()
        
        tasks_to_delete = []
        now = datetime.now()
        
        for task in tasks:
            task_status = task.get('status')
            last_check_time = task.get('lastCheckTime')
            
            if not last_check_time:
                continue
                
            # 找到对应的配置
            config = next((c for c in configs if c['status'] == task_status and c['enabled']), None)
            if not config:
                continue
            
            # 计算天数差
            try:
                last_check = datetime.fromisoformat(last_check_time.replace('Z', '+00:00'))
                days_diff = (now - last_check).days
                
                if days_diff >= config['days']:
                    tasks_to_delete.append({
                        'task': task,
                        'config': config,
                        'days_diff': days_diff
                    })
            except Exception as e:
                print(f"解析时间失败: {e}")
                continue
        
        return tasks_to_delete
        
    except Exception as e:
        print(f"获取自动删除任务失败: {e}")
        return []

def execute_auto_delete():
    """执行自动删除任务"""
    try:
        tasks_to_delete = get_tasks_for_auto_delete()
        
        if not tasks_to_delete:
            return {"success": True, "message": "没有需要自动删除的任务", "deleted_count": 0}
        
        settings = get_settings()
        project_address = settings.get('project_address')
        api_key = settings.get('api_key')
        
        if not project_address or not api_key:
            return {"success": False, "message": "配置信息不完整"}
        
        headers = {'x-api-key': api_key}
        deleted_count = 0
        
        for item in tasks_to_delete:
            task = item['task']
            config = item['config']
            
            try:
                # 调用删除API
                delete_url = f"{project_address}/api/tasks/{task['id']}"
                delete_data = {'deleteCloud': config['delete_cloud']}
                
                response = requests.delete(delete_url, headers=headers, json=delete_data, timeout=10)
                
                if response.status_code == 200:
                    deleted_count += 1
                    print(f"自动删除任务成功: {task.get('resourceName', 'Unknown')} (ID: {task['id']})")
                else:
                    print(f"自动删除任务失败: {task.get('resourceName', 'Unknown')} (ID: {task['id']})")
                    
            except Exception as e:
                print(f"删除任务异常: {task.get('resourceName', 'Unknown')} (ID: {task['id']}): {e}")
        
        return {
            "success": True, 
            "message": f"自动删除完成，共删除 {deleted_count} 个任务",
            "deleted_count": deleted_count,
            "total_found": len(tasks_to_delete)
        }
        
    except Exception as e:
        return {"success": False, "message": f"执行自动删除失败: {e}"}

# 自动删除配置路由
@app.route('/auto-delete')
@admin_required
def auto_delete_config():
    """自动删除配置页面"""
    configs = get_auto_delete_configs()
    return render_template('auto_delete_config.html', configs=configs)

@app.route('/api/auto-delete/configs')
@admin_required
def get_auto_delete_configs_api():
    """获取自动删除配置API"""
    try:
        configs = get_auto_delete_configs()
        return jsonify({'success': True, 'data': configs})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/auto-delete/configs/<int:config_id>', methods=['PUT'])
@admin_required
def update_auto_delete_config_api(config_id):
    """更新自动删除配置API"""
    try:
        data = request.get_json()
        days = data.get('days', 30)
        delete_cloud = data.get('delete_cloud', False)
        enabled = data.get('enabled', True)
        
        update_auto_delete_config(config_id, days, delete_cloud, enabled)
        return jsonify({'success': True, 'message': '配置更新成功'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/auto-delete/execute', methods=['POST'])
@admin_required
def execute_auto_delete_api():
    """执行自动删除API"""
    try:
        result = execute_auto_delete()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/auto-delete/preview')
@admin_required
def preview_auto_delete():
    """预览自动删除任务API"""
    try:
        tasks_to_delete = get_tasks_for_auto_delete()
        return jsonify({
            'success': True, 
            'data': tasks_to_delete,
            'count': len(tasks_to_delete)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/auto-delete/schedule', methods=['POST'])
@admin_required
def schedule_auto_delete():
    """定时执行自动删除API"""
    try:
        # 这里可以集成定时任务系统，比如APScheduler
        # 目前先直接执行一次
        result = execute_auto_delete()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# 添加一个简单的定时任务（每小时执行一次）
import threading
import time

def auto_delete_scheduler():
    """自动删除定时任务"""
    while True:
        try:
            # 每小时执行一次
            time.sleep(3600)  # 3600秒 = 1小时
            print("🕐 执行定时自动删除任务...")
            result = execute_auto_delete()
            if result['success'] and result['deleted_count'] > 0:
                print(f"✅ 定时删除完成: {result['message']}")
            else:
                print(f"ℹ️ 定时删除: {result['message']}")
        except Exception as e:
            print(f"❌ 定时删除任务异常: {e}")

# 启动定时任务线程
def start_auto_delete_scheduler():
    """启动自动删除定时任务"""
    scheduler_thread = threading.Thread(target=auto_delete_scheduler, daemon=True)
    scheduler_thread.start()
    print("🚀 自动删除定时任务已启动")

# 模板辅助函数
@app.template_filter('get_status_icon')
def get_status_icon(status):
    """获取状态图标"""
    icon_map = {
        'pending': '⏳',
        'processing': '📺',
        'completed': '✅',
        'failed': '❌'
    }
    return icon_map.get(status, '❓')

@app.template_filter('get_status_text')
def get_status_text(status):
    """获取状态文本"""
    text_map = {
        'pending': '等待中',
        'processing': '追剧中',
        'completed': '已完成',
        'failed': '失败'
    }
    return text_map.get(status, status)

# 自动删除配置路由

if __name__ == '__main__':
    # 初始化数据库
    init_db()
    
    # 启动自动删除定时任务
    start_auto_delete_scheduler()
    
    # 启动Flask应用
    app.run(debug=True, host='0.0.0.0', port=5000)