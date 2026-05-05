# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, session, redirect
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql # 修正1：导入正确的数据库驱动包
import json
import os
import uuid
import re

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_here'
app.config['JSON_AS_ASCII'] = False

# === # === MySQL Aiven 云端配置 ===
MYSQL_CONFIG = {
    'host': 'mysql-b6c8fa-nguyenvantoan32916-49c2.h.aivencloud.com',
    'port': 21283,
    'user': 'avnadmin',
    'password': 'AVNS_od6VLyn8ryI5kGh78ZW',
    'database': 'defaultdb',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
    # 核心：由于 Aiven 强制加密，这里必须手动开启 SSL 模式
    'ssl': {'ssl_mode': 'REQUIRED'} 
}

def get_db_conn():
    # 修正1：使用 pymysql 建立 TCP 连接
    return pymysql.connect(**MYSQL_CONFIG)

DATA_FILE = 'tasks.json'
MSG_FILE = 'messages.json'

# === 数据读写工具函数 ===
def load_data(filename):
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f: 
                return json.load(f)
        except: 
            return {}
    return {}

def save_data(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user_id():
    # 修正3：底层的会话状态映射
    # 优先检查是否已经经过真实 MySQL 鉴权
    if 'username' in session:
        return session['username']
    
    # 如果没有登录，分配一个基于内存的匿名 UUID 指针
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
        session.permanent = True
    return session['user_id']

# === 用户认证相关函数（MySQL 版） ===
def get_user_by_username(username):
    conn = get_db_conn()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE username=%s', (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def get_user_by_email(email):
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email=%s', (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def create_user(username, email, password):
    conn = get_db_conn()
    cursor = conn.cursor()
    password_hash = generate_password_hash(password)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('INSERT INTO users (username, email, password_hash, created_at) VALUES (%s, %s, %s, %s)',
                   (username, email, password_hash, now))
    conn.commit()
    cursor.close()
    conn.close()

def is_valid_email(email):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_username(username):
    """验证用户名格式（3-20个字符，字母/数字/下划线）"""
    if not (3 <= len(username) <= 20):
        return False
    return re.match(r'^[a-zA-Z0-9_]+$', username) is not None

# === 页面路由 ===
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login_page():
    if session.get('username'):
        return redirect('/dashboard')
    return render_template('login.html')

@app.route('/register')
def register_page():
    if session.get('username'):
        return redirect('/dashboard')
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('username'):
        return redirect('/login')
    return render_template('dashboard.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    user_id = get_user_id()
    today = datetime.now().strftime('%Y-%m-%d')
    all_tasks = load_data(DATA_FILE)
    user_tasks = all_tasks.get(user_id, {})
    return jsonify(user_tasks.get(today, []))

@app.route('/api/tasks', methods=['POST'])
def add_task():
    user_id = get_user_id()
    today = datetime.now().strftime('%Y-%m-%d')
    data = request.get_json()
    content = data.get('content', '').strip()
    if not content: return jsonify({'error': 'content required'}), 400
    
    all_tasks = load_data(DATA_FILE)
    if user_id not in all_tasks: all_tasks[user_id] = {}
    if today not in all_tasks[user_id]: all_tasks[user_id][today] = []
    
    task_id = max([t['id'] for t in all_tasks[user_id][today]], default=0) + 1
    new_task = {'id': task_id, 'content': content, 'time': datetime.now().strftime('%H:%M'), 'completed': False}
    all_tasks[user_id][today].append(new_task)
    save_data(DATA_FILE, all_tasks)
    return jsonify(new_task), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT', 'DELETE'])
def update_or_delete_task(task_id):
    user_id = get_user_id()
    today = datetime.now().strftime('%Y-%m-%d')
    all_tasks = load_data(DATA_FILE)
    
    if user_id in all_tasks and today in all_tasks[user_id]:
        if request.method == 'PUT':
            for task in all_tasks[user_id][today]:
                if task['id'] == task_id:
                    task['completed'] = request.get_json().get('completed', False)
                    save_data(DATA_FILE, all_tasks)
                    return jsonify(task)
        elif request.method == 'DELETE':
            all_tasks[user_id][today] = [t for t in all_tasks[user_id][today] if t['id'] != task_id]
            save_data(DATA_FILE, all_tasks)
            return jsonify({'success': True})
    return jsonify({'error': 'not found'}), 404

# === 留言板接口 ===
@app.route('/api/messages', methods=['GET'])
def get_messages():
    user_id = get_user_id()
    msgs = load_data(MSG_FILE)
    return jsonify(msgs.get(user_id, []))

@app.route('/api/messages', methods=['POST'])
def send_message():
    user_id = get_user_id()
    content = request.get_json().get('content', '').strip()
    if not content: return jsonify({'error': 'empty'}), 400

    msgs = load_data(MSG_FILE)
    if user_id not in msgs: msgs[user_id] = []
    
    new_msg = {'role': 'user', 'content': content, 'time': datetime.now().strftime('%m-%d %H:%M')}
    msgs[user_id].append(new_msg)
    save_data(MSG_FILE, msgs)
    return jsonify(new_msg)

# === 认证 API 路由（MySQL 版） ===
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify({'message': '用户名、邮箱和密码不能为空'}), 400
    if not is_valid_username(username):
        return jsonify({'message': '用户名必须为3-20个字符，只能包含字母、数字和下划线'}), 400
    if not is_valid_email(email):
        return jsonify({'message': '邮箱格式不正确'}), 400
    if len(password) < 6:
        return jsonify({'message': '密码至少需要6个字符'}), 400

    if get_user_by_username(username):
        return jsonify({'message': '用户名已被占用'}), 400
    if get_user_by_email(email):
        return jsonify({'message': '该邮箱已被注册'}), 400

    create_user(username, email, password)
    # 注册完毕自动给当前会话挂载真实用户名
    session['username'] = username
    session.permanent = True
    return jsonify({'message': '注册成功', 'username': username}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    if not username or not password:
        return jsonify({'message': '用户名和密码不能为空'}), 400
    
    user = get_user_by_username(username)
  # 直接用 == 比较数据库里取出的字符串，和前端传来的字符串是否完全一致
    if not user or user['password_hash'] != password:
        return jsonify({'message': '用户名或密码错误'}), 401
    
    session.clear() # 登录前清空原有的匿名会话数据，防止脏数据污染
    session['username'] = username
    session.permanent = True
    return jsonify({'message': '登录成功', 'username': username}), 200

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear() # 摧毁当前的身份令牌
    return jsonify({'message': '登出成功'}), 200

@app.route('/api/user', methods=['GET'])
def get_current_user():
    username = session.get('username')
    if username:
        return jsonify({'username': username}), 200
    return jsonify({'username': None}), 200
# === zixiHub 视频页路由 ===
@app.route('/zixihub')
def zixihub():
    return render_template('zixihub.html')

# === 下面是你代码本来就有的结尾 ===


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)