#!/usr/bin/env python3
"""
大模型对话后端 API 服务
使用 Python 标准库 http.server 实现，无框架依赖
"""

import json
import os
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import uuid

# 配置
PORT = int(os.environ.get('PORT', 8000))
LLM_API_KEY = os.environ.get('LLM_API_KEY', '')
LLM_API_URL = os.environ.get('LLM_API_URL', 'https://api.openclaw.ai/v1/chat/completions')

# 内存中的会话存储（生产环境应使用数据库）
conversations = {}


class ChatAPIHandler(BaseHTTPRequestHandler):
    """HTTP 请求处理器"""

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

    def do_OPTIONS(self):
        """处理 CORS 预检请求"""
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        """处理 GET 请求"""
        if self.path == '/health':
            self.handle_health()
        else:
            self._send_error_response(404, 'NOT_FOUND', '端点不存在')

    def do_POST(self):
        """处理 POST 请求"""
        if self.path == '/chat':
            self.handle_chat()
        else:
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


def run_server():
    """启动 HTTP 服务器"""
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, ChatAPIHandler)
    print(f"🚀 服务器启动在 http://localhost:{PORT}")
    print(f"📍 健康检查：GET http://localhost:{PORT}/health")
    print(f"💬 对话端点：POST http://localhost:{PORT}/chat")
    if not LLM_API_KEY:
        print("⚠️  警告：未设置 LLM_API_KEY，将使用测试模式")
    print("按 Ctrl+C 停止服务器\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
        httpd.server_close()


if __name__ == '__main__':
    run_server()
