# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    today = datetime.now().strftime('%Y-%m-%d')
    tasks = load_tasks()
    return jsonify(tasks.get(today, []))

@app.route('/api/tasks', methods=['POST'])
def add_task():
    today = datetime.now().strftime('%Y-%m-%d')
    data = request.get_json()
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({'error': 'content required'}), 400
    
    tasks = load_tasks()
    if today not in tasks:
        tasks[today] = []
    
    task_id = max([t['id'] for t in tasks[today]], default=0) + 1
    new_task = {
        'id': task_id,
        'content': content,
        'time': datetime.now().strftime('%H:%M'),
        'completed': False
    }
    
    tasks[today].append(new_task)
    save_tasks(tasks)
    return jsonify(new_task), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    today = datetime.now().strftime('%Y-%m-%d')
    data = request.get_json()
    tasks = load_tasks()
    
    if today in tasks:
        for task in tasks[today]:
            if task['id'] == task_id:
                task['completed'] = data.get('completed', False)
                save_tasks(tasks)
                return jsonify(task)
    
    return jsonify({'error': 'not found'}), 404

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    today = datetime.now().strftime('%Y-%m-%d')
    tasks = load_tasks()
    
    if today in tasks:
        tasks[today] = [t for t in tasks[today] if t['id'] != task_id]
        save_tasks(tasks)
        return jsonify({'success': True})
    
    return jsonify({'error': 'not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
