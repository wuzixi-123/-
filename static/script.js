// 设置当前日期
function setCurrentDate() {
    const now = new Date();
    const options = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' };
    const dateStr = now.toLocaleDateString('zh-CN', options);
    document.getElementById('currentDate').textContent = dateStr;
}

// 加载任务列表
async function loadTasks() {
    try {
        const response = await fetch('/api/tasks');
        const tasks = await response.json();
        renderTasks(tasks);
        updateStats();
    } catch (error) {
        console.error('加载任务失败:', error);
    }
}

// 渲染任务列表
function renderTasks(tasks) {
    const taskList = document.getElementById('taskList');
    
    if (tasks.length === 0) {
        taskList.innerHTML = `
            <div class="empty-state">
                <span class="empty-emoji">🎉</span>
                <p>还没有任务呢，先添加一个吧！</p>
            </div>
        `;
        return;
    }

    taskList.innerHTML = tasks.map(task => `
        <div class="task-item ${task.completed ? 'completed' : ''}">
            <input 
                type="checkbox" 
                class="checkbox" 
                ${task.completed ? 'checked' : ''}
                onchange="toggleTask(${task.id})"
            >
            <div class="task-content">
                <div class="task-text">${escapeHtml(task.content)}</div>
                <div class="task-time">🕐 ${task.time}</div>
            </div>
            <button class="delete-btn" onclick="deleteTask(${task.id})" title="删除">🗑️</button>
        </div>
    `).join('');
}

// 添加任务
async function addTask() {
    const input = document.getElementById('taskInput');
    const content = input.value.trim();

    if (!content) {
        alert('请输入任务内容！');
        return;
    }

    try {
        const response = await fetch('/api/tasks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ content })
        });

        if (response.ok) {
            input.value = '';
            input.focus();
            loadTasks();
        }
    } catch (error) {
        console.error('添加任务失败:', error);
        alert('添加任务失败！');
    }
}

// 切换任务完成状态
async function toggleTask(taskId) {
    try {
        const checkbox = event.target;
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ completed: checkbox.checked })
        });

        if (response.ok) {
            loadTasks();
        }
    } catch (error) {
        console.error('更新任务失败:', error);
    }
}

// 删除任务
async function deleteTask(taskId) {
    if (!confirm('确定要删除这个任务吗？')) {
        return;
    }

    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadTasks();
        }
    } catch (error) {
        console.error('删除任务失败:', error);
    }
}

// 更新统计信息
async function updateStats() {
    try {
        const response = await fetch('/api/tasks');
        const tasks = await response.json();

        const completed = tasks.filter(t => t.completed).length;
        const pending = tasks.filter(t => !t.completed).length;
        const total = tasks.length;

        document.getElementById('completedCount').textContent = completed;
        document.getElementById('pendingCount').textContent = pending;
        document.getElementById('totalCount').textContent = total;
    } catch (error) {
        console.error('更新统计失败:', error);
    }
}

// 转义HTML特殊字符
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    setCurrentDate();
    loadTasks();

    // 添加按钮点击事件
    document.getElementById('addBtn').addEventListener('click', addTask);

    // 输入框回车事件
    document.getElementById('taskInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            addTask();
        }
    });

    // 定时刷新（每30秒）
    setInterval(loadTasks, 30000);
});
