# 📝 今天做了什么 - 日程记录Web应用

一个简洁大方、卡通风格的日程记录应用，用于记录和管理每天的任务。

## 功能特性

✨ **核心功能**
- 📝 快速添加任务
- ✅ 标记任务完成状态
- 🗑️ 删除任务
- 📊 实时统计进度
- 💾 本地数据持久化

🎨 **设计特色**
- 卡通风格的UI设计
- 简洁大方的界面布局
- 响应式设计，支持移动设备
- 流畅的交互动画

## 技术栈

- **前端**: HTML5 + CSS3 + JavaScript
- **后端**: Python + Flask
- **数据存储**: JSON本地文件

## 项目结构

```
web2/
├── web2.py                 # Flask后端应用
├── requirements.txt        # Python依赖包
├── templates/
│   └── index.html         # 主页面
├── static/
│   ├── style.css          # 样式表
│   ├── script.js          # JavaScript交互
│   └── ...
└── tasks.json             # 任务数据（自动生成）
```

## 安装与运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行应用

```bash
python web2.py
```

### 3. 打开浏览器

访问 `http://localhost:5000`

## API接口

### 获取今天的任务
```
GET /api/tasks
返回: [
  {
    "id": 1,
    "content": "任务内容",
    "time": "14:30",
    "completed": false
  }
]
```

### 添加新任务
```
POST /api/tasks
请求体: {"content": "任务内容"}
返回: 新创建的任务对象
```

### 更新任务状态
```
PUT /api/tasks/<task_id>
请求体: {"completed": true/false}
返回: 更新后的任务对象
```

### 删除任务
```
DELETE /api/tasks/<task_id>
返回: {"success": true}
```

## 数据存储

任务数据以JSON格式存储在 `tasks.json` 文件中，按日期组织：

```json
{
  "2024-03-24": [
    {
      "id": 1,
      "content": "完成项目文档",
      "time": "14:30",
      "completed": true
    }
  ]
}
```

## 使用建议

- 利用回车键快速添加任务
- 点击复选框标记任务完成
- 删除前会有确认提示
- 任务数据自动保存到本地

## 浏览器兼容性

- Chrome (推荐)
- Firefox
- Safari
- Edge
- 现代移动浏览器

## 许可证

MIT License

---

**提示**: 每天午夜时自动切换到新的日期，任务不会丢失，会保留在历史记录中。
