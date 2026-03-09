// 大模型对话界面 - 前端逻辑

// 默认配置
const DEFAULT_CONFIG = {
    apiEndpoint: 'http://localhost:8000',
    modelName: 'qwen-plus',
    systemPrompt: '',
    temperature: 0.7,
    maxTokens: 2048
};

// 配置管理
const config = {
    ...DEFAULT_CONFIG,
    
    // 从 localStorage 加载配置
    load() {
        try {
            const saved = localStorage.getItem('chatpure_config');
            if (saved) {
                const parsed = JSON.parse(saved);
                Object.assign(this, parsed);
            }
        } catch (e) {
            console.error('加载配置失败:', e);
        }
    },
    
    // 保存配置到 localStorage
    save() {
        try {
            localStorage.setItem('chatpure_config', JSON.stringify({
                apiEndpoint: this.apiEndpoint,
                modelName: this.modelName,
                systemPrompt: this.systemPrompt,
                temperature: this.temperature,
                maxTokens: this.maxTokens
            }));
        } catch (e) {
            console.error('保存配置失败:', e);
        }
    },
    
    // 重置为默认配置
    reset() {
        Object.assign(this, DEFAULT_CONFIG);
        this.save();
    }
};

// 状态管理
const state = {
    conversationId: null,
    isConnected: false,
    isLoading: false
};

// DOM 元素
const elements = {};

// 初始化
function init() {
    cacheElements();
    config.load();
    setupEventListeners();
    setupSettingsPanel();
    checkHealth();
    autoResizeTextarea();
}

// 缓存 DOM 元素
function cacheElements() {
    elements.messages = document.getElementById('messages');
    elements.messageInput = document.getElementById('messageInput');
    elements.sendBtn = document.getElementById('sendBtn');
    elements.status = document.getElementById('status');
    elements.statusDot = document.querySelector('.status-dot');
    elements.statusText = document.querySelector('.status-text');
    
    // 设置面板元素
    elements.settingsBtn = document.getElementById('settingsBtn');
    elements.settingsModal = document.getElementById('settingsModal');
    elements.closeSettingsBtn = document.getElementById('closeSettingsBtn');
    elements.saveSettingsBtn = document.getElementById('saveSettingsBtn');
    elements.resetSettingsBtn = document.getElementById('resetSettingsBtn');
    
    // 配置输入元素
    elements.apiEndpoint = document.getElementById('apiEndpoint');
    elements.modelName = document.getElementById('modelName');
    elements.systemPrompt = document.getElementById('systemPrompt');
    elements.temperature = document.getElementById('temperature');
    elements.temperatureValue = document.getElementById('temperatureValue');
    elements.maxTokens = document.getElementById('maxTokens');
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

// 设置面板事件监听
function setupSettingsPanel() {
    // 打开设置面板
    elements.settingsBtn.addEventListener('click', openSettingsPanel);
    
    // 关闭设置面板
    elements.closeSettingsBtn.addEventListener('click', closeSettingsPanel);
    elements.settingsModal.addEventListener('click', (e) => {
        if (e.target === elements.settingsModal) {
            closeSettingsPanel();
        }
    });
    
    // 保存配置
    elements.saveSettingsBtn.addEventListener('click', saveSettings);
    
    // 重置配置
    elements.resetSettingsBtn.addEventListener('click', resetSettings);
    
    // 温度滑块实时更新显示值
    elements.temperature.addEventListener('input', (e) => {
        elements.temperatureValue.textContent = e.target.value;
    });
    
    // 加载当前配置到表单
    loadSettingsToForm();
}

// 打开设置面板
function openSettingsPanel() {
    loadSettingsToForm();
    elements.settingsModal.classList.add('active');
}

// 关闭设置面板
function closeSettingsPanel() {
    elements.settingsModal.classList.remove('active');
}

// 加载配置到表单
function loadSettingsToForm() {
    elements.apiEndpoint.value = config.apiEndpoint;
    elements.modelName.value = config.modelName;
    elements.systemPrompt.value = config.systemPrompt;
    elements.temperature.value = config.temperature;
    elements.temperatureValue.textContent = config.temperature;
    elements.maxTokens.value = config.maxTokens;
}

// 保存配置
function saveSettings() {
    config.apiEndpoint = elements.apiEndpoint.value.trim() || DEFAULT_CONFIG.apiEndpoint;
    config.modelName = elements.modelName.value.trim() || DEFAULT_CONFIG.modelName;
    config.systemPrompt = elements.systemPrompt.value.trim();
    config.temperature = parseFloat(elements.temperature.value) || DEFAULT_CONFIG.temperature;
    config.maxTokens = parseInt(elements.maxTokens.value) || DEFAULT_CONFIG.maxTokens;
    
    config.save();
    
    closeSettingsPanel();
    addSystemMessage('✅ 配置已保存');
    
    // 重新检查健康状态
    checkHealth();
}

// 重置配置
function resetSettings() {
    config.reset();
    loadSettingsToForm();
    addSystemMessage('🔄 配置已重置为默认值');
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
        const response = await fetch(`${config.apiEndpoint}/health`);
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
        // 构建请求体
        const requestBody = {
            message: message,
            conversation_id: state.conversationId || undefined,
            model: config.modelName,
            temperature: config.temperature,
            max_tokens: config.maxTokens
        };
        
        // 如果有系统提示词，添加到请求中
        if (config.systemPrompt) {
            requestBody.system_prompt = config.systemPrompt;
        }
        
        const response = await fetch(`${config.apiEndpoint}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
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
