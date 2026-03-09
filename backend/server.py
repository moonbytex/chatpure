#!/usr/bin/env python3
"""
ChatPure 后端服务
使用 Python 标准库 http.server 实现，无框架依赖
集成静态文件服务和对话 API
"""

import json
import os
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import uuid
from pathlib import Path

# 配置
PORT = int(os.environ.get('PORT', 8000))
LLM_API_KEY = os.environ.get('LLM_API_KEY', '')
LLM_API_URL = os.environ.get('LLM_API_URL', 'https://api.openclaw.ai/v1/chat/completions')

# 获取项目根目录和前端目录路径
SCRIPT_DIR = Path(__file__).parent.resolve()
FRONTEND_DIR = SCRIPT_DIR.parent / 'frontend'

# 内存中的会话存储（生产环境应使用数据库）
conversations = {}

# MIME 类型映射
MIME_TYPES = {
    '.html': 'text/html; charset=utf-8',
    '.htm': 'text/html; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon',
    '.txt': 'text/plain; charset=utf-8',
    '.xml': 'application/xml',
    '.pdf': 'application/pdf',
}


class ChatPureHandler(BaseHTTPRequestHandler):
    """HTTP 请求处理器 - 支持 API 和静态文件"""

    def _set_cors_headers(self):
        """设置 CORS 头，允许跨域请求"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def _send_json_response(self, status_code, data):
        """发送 JSON 响应"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def _send_error_response(self, status_code, error_type, message):
        """发送错误响应"""
        self._send_json_response(status_code, {
            'error': error_type,
            'message': message
        })

    def _serve_static_file(self, file_path):
        """提供静态文件"""
        try:
            if not file_path.exists():
                self._send_error_response(404, 'NOT_FOUND', '文件不存在')
                return

            # 读取文件内容
            with open(file_path, 'rb') as f:
                content = f.read()

            # 获取 MIME 类型
            mime_type = MIME_TYPES.get(file_path.suffix.lower(), 'application/octet-stream')

            self.send_response(200)
            self.send_header('Content-Type', mime_type)
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)

        except Exception as e:
            print(f"提供静态文件时出错：{e}")
            self._send_error_response(500, 'INTERNAL_ERROR', str(e))

    def do_OPTIONS(self):
        """处理 CORS 预检请求"""
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        """处理 GET 请求"""
        # API 端点
        if self.path == '/health':
            self.handle_health()
            return

        # 静态文件服务
        # 根路径返回 index.html
        if self.path == '/':
            index_path = FRONTEND_DIR / 'index.html'
            self._serve_static_file(index_path)
            return

        # 其他静态文件
        # 移除查询参数
        clean_path = self.path.split('?')[0]
        file_path = FRONTEND_DIR / clean_path.lstrip('/')

        # 安全检查：防止目录遍历攻击
        try:
            file_path.resolve().relative_to(FRONTEND_DIR.resolve())
        except ValueError:
            self._send_error_response(403, 'FORBIDDEN', '禁止访问')
            return

        self._serve_static_file(file_path)

    def do_POST(self):
        """处理 POST 请求"""
        if self.path == '/chat':
            self.handle_chat()
        else:
            # 尝试返回 404 页面
            self._send_error_response(404, 'NOT_FOUND', '端点不存在')

    def handle_health(self):
        """健康检查端点"""
        self._send_json_response(200, {
            'status': 'ok',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })

    def handle_chat(self):
        """对话端点"""
        try:
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self._send_error_response(400, 'BAD_REQUEST', '请求体不能为空')
                return

            body = self.rfile.read(content_length)
            request_data = json.loads(body.decode('utf-8'))

            # 验证必填字段
            if 'message' not in request_data or not request_data['message']:
                self._send_error_response(400, 'BAD_REQUEST', 'message 字段不能为空')
                return

            message = request_data['message']
            conversation_id = request_data.get('conversation_id', str(uuid.uuid4()))

            # 获取或创建会话历史
            if conversation_id not in conversations:
                conversations[conversation_id] = []

            # 添加用户消息到历史
            conversations[conversation_id].append({
                'role': 'user',
                'content': message
            })

            # 调用大模型 API
            reply = self.call_llm_api(conversations[conversation_id])

            # 添加助手回复到历史
            conversations[conversation_id].append({
                'role': 'assistant',
                'content': reply
            })

            # 返回响应
            self._send_json_response(200, {
                'reply': reply,
                'conversation_id': conversation_id
            })

        except json.JSONDecodeError:
            self._send_error_response(400, 'BAD_REQUEST', '无效的 JSON 格式')
        except Exception as e:
            print(f"处理请求时出错：{e}")
            self._send_error_response(500, 'INTERNAL_ERROR', str(e))

    def call_llm_api(self, messages):
        """调用大模型 API 获取回复"""
        if not LLM_API_KEY:
            # 如果没有配置 API Key，返回模拟回复（用于测试）
            return f"[测试模式] 收到消息：{messages[-1]['content']}"

        try:
            # 构建请求
            payload = json.dumps({
                'model': 'qwen3.5-plus',
                'messages': messages,
                'max_tokens': 1024
            }).encode('utf-8')

            req = urllib.request.Request(
                LLM_API_URL,
                data=payload,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {LLM_API_KEY}'
                },
                method='POST'
            )

            # 发送请求
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('choices', [{}])[0].get('message', {}).get('content', '无回复')

        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else ''
            print(f"LLM API 请求失败：{e.code} - {error_body}")
            raise Exception(f'大模型 API 请求失败：{e.code}')
        except Exception as e:
            print(f"调用 LLM API 时出错：{e}")
            raise

    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {args[0]}")


def run_server():
    """启动 HTTP 服务器"""
    # 检查前端目录是否存在
    if not FRONTEND_DIR.exists():
        print(f"❌ 错误：前端目录不存在：{FRONTEND_DIR}")
        return

    server_address = ('', PORT)
    httpd = HTTPServer(server_address, ChatPureHandler)
    print(f"🚀 ChatPure 服务启动在 http://localhost:{PORT}")
    print(f"📁 前端目录：{FRONTEND_DIR}")
    print(f"📍 健康检查：GET http://localhost:{PORT}/health")
    print(f"💬 对话端点：POST http://localhost:{PORT}/chat")
    if not LLM_API_KEY:
        print("⚠️  警告：未设置 LLM_API_KEY，将使用测试模式")
    print("\n按 Ctrl+C 停止服务器\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
        httpd.server_close()


if __name__ == '__main__':
    run_server()
