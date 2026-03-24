# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import os
import uuid

app = Flask(__name__)

# 关键配置
app.config['JSON_AS_ASCII'] = False
DATA_FILE = 'tasks.json'

def load_tasks():
    """加载所有用户的任务数据"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_tasks(tasks):
    """保存所有用户的任务数据"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

def get_user_id():
    """从请求中获取用户ID"""
    return request.headers.get('X-User-ID', 'default-user')

def get_user_tasks(user_id, tasks_data=None):
    """获取特定用户今天的任务"""
    if tasks_data is None:
        tasks_data = load_tasks()

    today = datetime.now().strftime('%Y-%m-%d')

    if user_id not in tasks_data:
        return []

    return tasks_data[user_id].get(today, [])

def save_user_tasks(user_id, today_tasks):
    """保存特定用户的任务"""
    tasks = load_tasks()

    if user_id not in tasks:
        tasks[user_id] = {}

    today = datetime.now().strftime('%Y-%m-%d')
    tasks[user_id][today] = today_tasks

    save_tasks(tasks)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """获取当前用户今天的任务"""
    user_id = get_user_id()
    tasks = load_tasks()
    user_tasks = get_user_tasks(user_id, tasks)
    return jsonify(user_tasks)

@app.route('/api/tasks', methods=['POST'])
def add_task():
    """为当前用户添加任务"""
    user_id = get_user_id()
    today = datetime.now().strftime('%Y-%m-%d')
    data = request.get_json()
    content = data.get('content', '').strip()

    if not content:
        return jsonify({'error': 'content required'}), 400

    tasks = load_tasks()

    # 确保用户存在
    if user_id not in tasks:
        tasks[user_id] = {}

    if today not in tasks[user_id]:
        tasks[user_id][today] = []

    # 生成任务ID
    task_id = max([t['id'] for t in tasks[user_id][today]], default=0) + 1
    new_task = {
        'id': task_id,
        'content': content,
        'time': datetime.now().strftime('%H:%M'),
        'completed': False
    }

    tasks[user_id][today].append(new_task)
    save_tasks(tasks)
    return jsonify(new_task), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """更新当前用户的任务"""
    user_id = get_user_id()
    today = datetime.now().strftime('%Y-%m-%d')
    data = request.get_json()
    tasks = load_tasks()

    if user_id not in tasks or today not in tasks[user_id]:
        return jsonify({'error': 'not found'}), 404

    for task in tasks[user_id][today]:
        if task['id'] == task_id:
            task['completed'] = data.get('completed', False)
            save_tasks(tasks)
            return jsonify(task)

    return jsonify({'error': 'not found'}), 404

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """删除当前用户的任务"""
    user_id = get_user_id()
    today = datetime.now().strftime('%Y-%m-%d')
    tasks = load_tasks()

    if user_id not in tasks or today not in tasks[user_id]:
        return jsonify({'error': 'not found'}), 404

    tasks[user_id][today] = [t for t in tasks[user_id][today] if t['id'] != task_id]
    save_tasks(tasks)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
