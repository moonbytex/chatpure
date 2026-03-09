# ChatPure 后端服务 🐍

基于 Python 标准库 `http.server` 实现的轻量级 HTTP 服务，零第三方依赖。

## 功能特性

- ✅ 静态文件服务 - 托管前端页面（`/` 访问前端）
- ✅ `GET /health` - 健康检查端点
- ✅ `POST /chat` - 对话端点，转发请求到大模型 API
- ✅ CORS 支持（允许前端跨域请求）
- ✅ 会话管理（支持多轮对话上下文）
- ✅ 参数配置（model, temperature, max_tokens, system_prompt）
- ✅ 错误处理和日志记录
- ✅ 测试模式（未配置 API Key 时返回模拟回复）

## 功能特性

- ✅ `GET /health` - 健康检查端点
- ✅ `POST /chat` - 对话端点，转发请求到大模型 API
- ✅ CORS 支持（允许前端跨域请求）
- ✅ 会话管理（支持多轮对话上下文）
- ✅ 错误处理和日志记录
- ✅ 测试模式（未配置 API Key 时返回模拟回复）

## 快速开始

### 1. 配置环境变量

```bash
# 必需：大模型 API 密钥
export LLM_API_KEY="your-api-key-here"

# 可选：自定义 API URL（默认使用 OpenClaw Gateway）
export LLM_API_URL="https://api.openclaw.ai/v1/chat/completions"

# 可选：服务端口（默认 8000）
export PORT=8000
```

### 2. 启动服务器

```bash
python3 server.py
```

### 3. 测试端点

**健康检查：**
```bash
curl http://localhost:8000/health
# 响应：{"status": "ok", "timestamp": "2026-03-09T07:14:00Z"}
```

**对话测试：**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好"}'
# 响应：{"reply": "你好！我是 AI 助手", "conversation_id": "uuid"}
```

**多轮对话：**
```bash
# 第一次请求
RESPONSE=$(curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "我叫小明"}')
CONV_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['conversation_id'])")

# 第二次请求（使用相同的 conversation_id）
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"记住我的名字\", \"conversation_id\": \"$CONV_ID\"}"
```

## API 规范

详见：`../api-spec.json`

### 端点列表

| 端点 | 方法 | 描述 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/chat` | POST | 发送对话消息 |

### 请求/响应格式

**POST /chat 请求：**
```json
{
  "message": "用户输入的消息",
  "conversation_id": "可选的会话 ID"
}
```

**POST /chat 响应：**
```json
{
  "reply": "大模型的回复",
  "conversation_id": "会话 ID"
}
```

**错误响应：**
```json
{
  "error": "错误类型",
  "message": "错误详情"
}
```

## 项目结构

```
backend/
├── server.py      # 主服务器文件
└── README.md      # 使用说明
```

## 注意事项

- 会话数据存储在内存中，重启服务器后会丢失
- 生产环境建议使用数据库持久化会话
- 测试模式下（未配置 API Key）返回模拟回复
