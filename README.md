# ChatPure 🎨

纯净、简洁的大模型对话界面

## 项目简介

ChatPure 是一个简单优雅的大模型对话 Web 应用，采用前后端分离架构：
- **前端**: 纯 HTML + CSS + JavaScript（无任何框架）
- **后端**: Python HTTP 服务（无任何框架）
- **特点**: 轻量、快速、易于理解和定制

## 项目结构

```
chatpure/
├── frontend/           # 前端文件
│   ├── index.html      # 主页面
│   ├── styles.css      # 样式表
│   └── app.js          # 前端逻辑
├── backend/            # 后端文件
│   ├── server.py       # Python HTTP 服务
│   └── README.md       # 后端说明
└── README.md           # 本文件
```

## 快速开始

### 后端启动

```bash
cd backend
python3 server.py
```

服务将在 `http://localhost:8000` 启动

### 前端使用

直接在浏览器中打开 `frontend/index.html`，或将其部署到任何静态文件服务器

## API 接口

### POST /chat

发送对话消息并获取大模型回复

**请求:**
```json
{
  "message": "你好",
  "conversation_id": "可选的会话 ID"
}
```

**响应:**
```json
{
  "reply": "你好！有什么我可以帮助你的吗？",
  "conversation_id": "会话 ID"
}
```

### GET /health

健康检查端点

**响应:**
```json
{
  "status": "ok"
}
```

## 技术栈

- **前端**: HTML5, CSS3, Vanilla JavaScript
- **后端**: Python 3, http.server
- **API**: RESTful JSON

## 设计理念

✨ **页面美观整洁** — 简洁现代的视觉风格，舒适的配色方案，良好的用户体验

## 许可证

MIT License

---

*由 Alice (前端) 和 Bob (后端) 协作完成*
