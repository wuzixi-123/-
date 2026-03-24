# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import json
import os
import uuid  # 引入 uuid 用于生成唯一的用户ID

app = Flask(__name__)

# 必须设置一个安全密钥，Flask 才能使用 session 功能
app.secret_key = 'your_super_secret_key_here' 

# 关键配置
app.config['JSON_AS_ASCII'] = False
DATA_FILE = 'tasks.json'

def load_tasks():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_tasks(tasks):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

# 核心功能：获取或分配用户ID
def get_user_id():
    # 如果这个浏览器是第一次来，给它分配一个独一无二的 UUID
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
        session.permanent = True  # 让身份码持久保存，关掉浏览器也不会立马失效
    return session['user_id']

@app.route('/')
def index():
    get_user_id() # 用户一打开主页，就确保他有身份码
    return render_template('index.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    user_id = get_user_id()
    today = datetime.now().strftime('%Y-%m-%d')
    all_tasks = load_tasks()
    
    # 以前是直接获取当天的，现在是获取：所有任务 -> 这个用户的 -> 当天的
    user_tasks = all_tasks.get(user_id, {})
    return jsonify(user_tasks.get(today, []))

@app.route('/api/tasks', methods=['POST'])
def add_task():
    user_id = get_user_id()
    today = datetime.now().strftime('%Y-%m-%d')
    data = request.get_json()
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({'error': 'content required'}), 400
    
    all_tasks = load_tasks()
    
    # 初始化这个用户的专属数据结构
    if user_id not in all_tasks:
        all_tasks[user_id] = {}
    if today not in all_tasks[user_id]:
        all_tasks[user_id][today] = []
    
    user_today_tasks = all_tasks[user_id][today]
    task_id = max([t['id'] for t in user_today_tasks], default=0) + 1
    
    new_task = {
        'id': task_id,
        'content': content,
        'time': datetime.now().strftime('%H:%M'),
        'completed': False
    }
    
    user_today_tasks.append(new_task)
    save_tasks(all_tasks)
    return jsonify(new_task), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    user_id = get_user_id()
    today = datetime.now().strftime('%Y-%m-%d')
    data = request.get_json()
    all_tasks = load_tasks()
    
    if user_id in all_tasks and today in all_tasks[user_id]:
        for task in all_tasks[user_id][today]:
            if task['id'] == task_id:
                task['completed'] = data.get('completed', False)
                save_tasks(all_tasks)
                return jsonify(task)
    
    return jsonify({'error': 'not found'}), 404

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    user_id = get_user_id()
    today = datetime.now().strftime('%Y-%m-%d')
    all_tasks = load_tasks()
    
    if user_id in all_tasks and today in all_tasks[user_id]:
        all_tasks[user_id][today] = [t for t in all_tasks[user_id][today] if t['id'] != task_id]
        save_tasks(all_tasks)
        return jsonify({'success': True})
    
    return jsonify({'error': 'not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)