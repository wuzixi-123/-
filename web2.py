# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import json
import os
import uuid

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_here' 
app.config['JSON_AS_ASCII'] = False

DATA_FILE = 'tasks.json'
MSG_FILE = 'messages.json' # 新增：专门存聊天记录的文件

# === 数据读写工具函数 ===
def load_data(filename):
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f: return json.load(f)
        except: return {}
    return {}

def save_data(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user_id():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
        session.permanent = True
    return session['user_id']

# === 原有的任务管理路由 ===
@app.route('/')
def index():
    get_user_id()
    return render_template('index.html')

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

# === 新增：普通用户的留言接口 ===
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

# === 新增：管理员专属后门 ===
@app.route('/admin')
def admin_page():
    # 这里为了简单，目前没有加密码，后续可以加上
    msgs = load_data(MSG_FILE)
    return render_template('admin.html', all_messages=msgs)

@app.route('/admin/reply', methods=['POST'])
def admin_reply():
    data = request.get_json()
    target_user = data.get('user_id')
    content = data.get('content', '').strip()
    
    msgs = load_data(MSG_FILE)
    if target_user in msgs and content:
        new_msg = {'role': 'admin', 'content': content, 'time': datetime.now().strftime('%m-%d %H:%M')}
        msgs[target_user].append(new_msg)
        save_data(MSG_FILE, msgs)
        return jsonify(new_msg)
    return jsonify({'error': 'fail'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)