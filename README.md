# ChatPure 🤖

一个简洁优雅的大模型对话 Web 界面。

![ChatPure](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ 特性

- 🎨 **美观界面** - 现代化渐变设计，响应式布局
- ⚙️ **参数配置** - 支持自定义模型、温度、系统提示词等
- 🚀 **一键启动** - 简单脚本即可运行整个应用
- 🔌 **灵活对接** - 支持多种大模型 API
- 💾 **会话保持** - 自动保存对话历史
- 📱 **移动适配** - 完美支持手机和平板

## 🚀 快速开始

### 一键启动

**Linux / macOS:**
```bash
./start.sh
```

**Windows:**
```bash
start.bat
```

启动后访问：**http://localhost:8000**

### 手动启动

```bash
# 进入后端目录
cd backend

# 设置 API Key（可选，不设置则使用测试模式）
export LLM_API_KEY="your-api-key"

# 启动服务
python3 server.py
```

## ⚙️ 配置说明

### 前端配置

访问页面后，点击右上角 **⚙️ 设置** 按钮，可以配置以下参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| **API 端点** | 后端服务地址 | `http://localhost:8000` |
| **模型名称** | 大模型名称 | `qwen-plus` |
| **系统提示词** | 设置 AI 角色（可选） | - |
| **温度** | 回复随机性（0-2） | `0.7` |
| **最大 token 数** | 回复长度限制 | `2048` |

配置会自动保存到浏览器本地存储，页面刷新后不丢失。

### 后端配置

通过环境变量配置：

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `LLM_API_KEY` | 大模型 API 密钥 | - |
| `LLM_API_URL` | 大模型 API 地址 | `https://api.openclaw.ai/v1/chat/completions` |
| `PORT` | 服务端口 | `8000` |

**示例：**
```bash
export LLM_API_KEY="sk-xxx"
export LLM_API_URL="https://api.openai.com/v1/chat/completions"
export PORT=8000
python3 server.py
```

## 📁 项目结构

```
chatpure/
├── frontend/              # 前端文件
│   ├── index.html        # 主页面
│   ├── styles.css        # 样式表
│   └── app.js            # 前端逻辑
├── backend/              # 后端文件
│   ├── server.py         # Python HTTP 服务
│   └── README.md         # 后端说明
├── start.sh              # Linux/Mac 启动脚本
├── start.bat             # Windows 启动脚本
├── .gitignore            # Git 忽略文件
└── README.md             # 项目说明
```

## 🔌 API 文档

### 健康检查

```http
GET /health
```

**响应：**
```json
{
  "status": "ok",
  "timestamp": "2026-03-09T07:17:21.274717Z"
}
```

### 对话接口

```http
POST /chat
Content-Type: application/json
```

**请求体：**
```json
{
  "message": "你好，请介绍一下你自己",
  "conversation_id": "可选的会话 ID",
  "model": "qwen-plus",
  "temperature": 0.7,
  "max_tokens": 2048,
  "system_prompt": "可选的系统提示词"
}
```

**响应：**
```json
{
  "reply": "你好！我是大模型助手...",
  "conversation_id": "会话 ID"
}
```

**错误响应：**
```json
{
  "error": "BAD_REQUEST",
  "message": "message 字段不能为空"
}
```

## 🛠️ 技术栈

**前端：**
- HTML5 + CSS3 + JavaScript（无框架）
- 响应式设计
- localStorage 本地存储

**后端：**
- Python 3（标准库 http.server）
- 零第三方依赖
- 内存会话存储

## 📦 部署选项

### 本地部署

最简单的方式，适合个人使用：

```bash
./start.sh
```

### 服务器部署

适合团队或公开服务：

1. 上传代码到服务器
2. 配置环境变量
3. 使用 systemd 或 supervisor 管理进程
4. 配置 Nginx 反向代理（可选）

**systemd 服务示例：**
```ini
[Unit]
Description=ChatPure Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/chatpure/backend
Environment="LLM_API_KEY=your-key"
ExecStart=/usr/bin/python3 server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Docker 部署（计划中）

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
EXPOSE 8000
CMD ["python3", "backend/server.py"]
```

## 🎨 配置示例

### 使用不同的模型

在设置面板中修改模型名称：

- `qwen-plus` - 通义千问 Plus
- `deepseek-chat` - DeepSeek Chat
- `gpt-4` - GPT-4
- `claude-3` - Claude 3

### 自定义系统提示词

设置 AI 的角色和行为：

```
你是一个专业的编程助手，擅长 Python 和 JavaScript 开发。
请用简洁清晰的方式回答问题，并提供代码示例。
```

### 调整回复风格

- **温度 0.1-0.3** - 确定性强，适合事实性问题
- **温度 0.5-0.7** - 平衡，适合日常对话
- **温度 1.0-2.0** - 创意性强，适合头脑风暴

## ❓ 常见问题

### Q: 为什么返回的是测试模式回复？

A: 如果没有配置 `LLM_API_KEY`，后端会运行在测试模式，返回模拟回复。配置真实的 API Key 即可。

### Q: 如何清空对话历史？

A: 刷新页面即可清空当前会话。配置保存在 localStorage 中不会被清空。

### Q: 可以修改端口吗？

A: 可以，设置环境变量 `PORT`：
```bash
export PORT=3000
python3 server.py
```

### Q: 支持哪些大模型 API？

A: 任何兼容 OpenAI API 格式的服务都可以，包括：
- 通义千问
- DeepSeek
- OpenAI GPT
- Claude
- 本地部署的模型（如 Ollama）

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 👥 作者

- **前端**: Alice
- **后端**: Bob

---

**Enjoy Chatting with AI!** 🎉
