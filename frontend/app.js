// 大模型对话界面 - 前端逻辑

// API 配置
const API_BASE_URL = 'http://localhost:8000';

// 状态管理
const state = {
    conversationId: null,
    isConnected: false,
    isLoading: false
};

// DOM 元素
const elements = {
    messages: document.getElementById('messages'),
    messageInput: document.getElementById('messageInput'),
    sendBtn: document.getElementById('sendBtn'),
    status: document.getElementById('status'),
    statusDot: document.querySelector('.status-dot'),
    statusText: document.querySelector('.status-text')
};

// 初始化
function init() {
    setupEventListeners();
    checkHealth();
    autoResizeTextarea();
}

// 设置事件监听
function setupEventListeners() {
    // 发送按钮点击
    elements.sendBtn.addEventListener('click', sendMessage);
    
    // 输入框回车发送（Shift+Enter 换行）
    elements.messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // 输入框自动调整高度
    elements.messageInput.addEventListener('input', autoResizeTextarea);
}

// 自动调整文本框高度
function autoResizeTextarea() {
    const textarea = elements.messageInput;
    textarea.style.height = 'auto';
    const newHeight = Math.min(textarea.scrollHeight, 120);
    textarea.style.height = newHeight + 'px';
}

// 检查后端健康状态
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            const data = await response.json();
            updateStatus('connected', '已连接');
            state.isConnected = true;
            console.log('后端服务正常:', data);
        } else {
            throw new Error('健康检查失败');
        }
    } catch (error) {
        updateStatus('error', '连接失败');
        state.isConnected = false;
        console.error('健康检查失败:', error);
        addSystemMessage('无法连接到后端服务，请确保后端正在运行');
    }
}

// 更新连接状态
function updateStatus(status, text) {
    elements.statusDot.className = 'status-dot ' + status;
    elements.statusText.textContent = text;
}

// 发送消息
async function sendMessage() {
    const message = elements.messageInput.value.trim();
    
    if (!message || state.isLoading) return;
    
    // 添加用户消息到界面
    addMessage(message, 'user');
    elements.messageInput.value = '';
    autoResizeTextarea();
    
    // 设置加载状态
    setLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                conversation_id: state.conversationId || undefined
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        // 保存会话 ID
        if (data.conversation_id) {
            state.conversationId = data.conversation_id;
        }
        
        // 显示机器人回复
        addMessage(data.reply, 'bot');
        
    } catch (error) {
        console.error('发送消息失败:', error);
        addMessage(`错误：${error.message}`, 'error');
    } finally {
        setLoading(false);
    }
}

// 设置加载状态
function setLoading(loading) {
    state.isLoading = loading;
    elements.sendBtn.disabled = loading;
    elements.messageInput.disabled = loading;
    
    if (loading) {
        elements.sendBtn.classList.add('loading');
        elements.messageInput.placeholder = '大模型思考中...';
    } else {
        elements.sendBtn.classList.remove('loading');
        elements.messageInput.placeholder = '输入你的消息...';
        elements.messageInput.focus();
    }
}

// 添加消息到界面
function addMessage(content, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;
    
    messageDiv.appendChild(contentDiv);
    elements.messages.appendChild(messageDiv);
    
    // 滚动到底部
    scrollToBottom();
}

// 添加系统消息
function addSystemMessage(content) {
    addMessage(content, 'system');
}

// 滚动到底部
function scrollToBottom() {
    const chatContainer = document.querySelector('.chat-container');
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', init);
