// 用户管理
class UserManager {
    constructor() {
        this.userIdKey = 'taskapp_user_id';
        this.userNameKey = 'taskapp_user_name';
    }

    // 获取或创建用户ID
    getUserId() {
        let userId = localStorage.getItem(this.userIdKey);
        if (!userId) {
            userId = 'user_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem(this.userIdKey, userId);
        }
        return userId;
    }

    // 获取用户名（显示用））
    getUserName() {
        return localStorage.getItem(this.userNameKey) || '我';
    }

    // 设置用户名
    setUserName(name) {
        localStorage.setItem(this.userNameKey, name);
        updateUserDisplay();
    }

    // 切换用户（用于测试多用户）
    switchUser(name) {
        if (name) {
            this.setUserName(name);
        } else {
            localStorage.removeItem(this.userNameKey);
            localStorage.removeItem(this.userIdKey);
            window.location.reload();
        }
    }

    // 清除用户数据
    logout() {
        localStorage.removeItem(this.userIdKey);
        localStorage.removeItem(this.userNameKey);
        window.location.reload();
    }
}

const userManager = new UserManager();

// 设置当前日期
function setCurrentDate() {
    const now = new Date();
    const options = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' };
    const dateStr = now.toLocaleDateString('zh-CN', options);
    document.getElementById('currentDate').textContent = dateStr;
}

// 更新用户显示
function updateUserDisplay() {
    const userName = userManager.getUserName();
    const userDisplay = document.getElementById('userDisplay');
    if (userDisplay) {
        userDisplay.textContent = `用户: ${userName}`;
    }
}

// 加载任务列表
async function loadTasks() {
    try {
        const response = await fetch('/api/tasks', {
            headers: {
                'X-User-ID': userManager.getUserId()
            }
        });
        const tasks = await response.json();
        renderTasks(tasks);
        updateStats();
    } catch (error) {
        console.error('Error loading tasks:', error);
    }
}

// 渲染任务列表
function renderTasks(tasks) {
    const taskList = document.getElementById('taskList');
    
    if (tasks.length === 0) {
        taskList.innerHTML = '<div class="empty-state"><span class="empty-emoji">🎉</span><p>还没有任务，先添加一个吧！</p></div>';
        return;
    }

    taskList.innerHTML = tasks.map(task => `
        <div class="task-item ${task.completed ? 'completed' : ''}">
            <input type="checkbox" class="checkbox" ${task.completed ? 'checked' : ''} onchange="toggleTask(${task.id})">
            <div class="task-content">
                <div class="task-text">${escapeHtml(task.content)}</div>
                <div class="task-time">🕐 ${task.time}</div>
            </div>
            <button class="delete-btn" onclick="deleteTask(${task.id})">🗑️</button>
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
                'Content-Type': 'application/json',
                'X-User-ID': userManager.getUserId()
            },
            body: JSON.stringify({ content })
        });

        if (response.ok) {
            input.value = '';
            input.focus();
            loadTasks();
        } else {
            alert('添加任务失败！');
        }
    } catch (error) {
        console.error('Error adding task:', error);
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
                'Content-Type': 'application/json',
                'X-User-ID': userManager.getUserId()
            },
            body: JSON.stringify({ completed: checkbox.checked })
        });

        if (response.ok) {
            loadTasks();
        }
    } catch (error) {
        console.error('Error updating task:', error);
    }
}

// 删除任务
async function deleteTask(taskId) {
    if (!confirm('确定要删除这个任务吗？')) {
        return;
    }

    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'DELETE',
            headers: {
                'X-User-ID': userManager.getUserId()
            }
        });

        if (response.ok) {
            loadTasks();
        }
    } catch (error) {
        console.error('Error deleting task:', error);
    }
}

// 更新统计信息
async function updateStats() {
    try {
        const response = await fetch('/api/tasks', {
            headers: {
                'X-User-ID': userManager.getUserId()
            }
        });
        const tasks = await response.json();

        const completed = tasks.filter(t => t.completed).length;
        const pending = tasks.filter(t => !t.completed).length;
        const total = tasks.length;

        document.getElementById('completedCount').textContent = completed;
        document.getElementById('pendingCount').textContent = pending;
        document.getElementById('totalCount').textContent = total;
    } catch (error) {
        console.error('Error updating stats:', error);
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
    updateUserDisplay();
    loadTasks();

    // 添加按钮点击事件
    document.getElementById('addBtn').addEventListener('click', addTask);

    // 输入框回车事件
    document.getElementById('taskInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') addTask();
    });

    // 用户切换按钮
    const switchUserBtn = document.getElementById('switchUserBtn');
    if (switchUserBtn) {
        switchUserBtn.addEventListener('click', () => {
            const newName = prompt('请输入你的名字:', userManager.getUserName());
            if (newName && newName.trim()) {
                userManager.setUserName(newName.trim());
                loadTasks();
            }
        });
    }
});
    // === 留言板功能 ===
    async function loadChatMessages() {
        try {
            const response = await fetch('/api/messages');
            const msgs = await response.json();
            const chatBox = document.getElementById('chatMessages');
        
            chatBox.innerHTML = msgs.map(msg => `
            <div class="msg-bubble ${msg.role === 'user' ? 'msg-user' : 'msg-admin'}">
                <div style="font-size: 0.7em; opacity: 0.7; margin-bottom: 2px;">${msg.time}</div>
                ${escapeHtml(msg.content)}
            </div>
        `).join('');
            // 自动滚动到最底部
            chatBox.scrollTop = chatBox.scrollHeight;
        } catch (error) {
            console.error('加载留言失败:', error);
        }
    }

    async function sendChatMessage() {
        const input = document.getElementById('chatInput');
        const content = input.value.trim();
        if (!content) return;

        try {
            const response = await fetch('/api/messages', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content })
            });

            if (response.ok) {
                input.value = '';
                loadChatMessages(); // 重新加载消息
            }
        } catch (error) {
            console.error('发送留言失败:', error);
        }
    }

    // 绑定回车发送留言
    document.addEventListener('DOMContentLoaded', () => {
        const chatInput = document.getElementById('chatInput');
        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') sendChatMessage();
            });
        }
        // 每 10 秒去后台查一下有没有站长的最新回复
        setInterval(loadChatMessages, 10000);
        loadChatMessages();
    });