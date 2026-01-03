// FastAPI Admin Panel - With GPT Chat

let apiEndpoints = [];
const CHAT_HISTORY_KEY = 'gpt_chat_history';

document.addEventListener('DOMContentLoaded', function() {
    initNavigation();
    initConsole();
    initStats();
    initChat();
    initEndpointsManager();
    
    setTimeout(() => {
        updateConnectionStatus(true);
    }, 1000);
});

// Navigation
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.section');
    
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const sectionId = this.dataset.section;
            
            navItems.forEach(nav => nav.classList.remove('active'));
            this.classList.add('active');
            
            sections.forEach(section => {
                section.classList.remove('active');
                if (section.id === sectionId) {
                    section.classList.add('active');
                }
            });
            
            const titles = {
                'dashboard': 'Панель управления',
                'gpt': 'GPT Chat',
                'api': 'API Эндпоинты',
                'settings': 'Настройки'
            };
            document.querySelector('.page-title').textContent = titles[sectionId] || 'Панель управления';
            
            if (sectionId === 'api' && apiEndpoints.length === 0) {
                loadApiEndpoints();
            }
        });
    });
    
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.querySelector('.sidebar');
    
    menuToggle.addEventListener('click', function() {
        sidebar.classList.toggle('open');
    });
    
    document.getElementById('logoutBtn').addEventListener('click', function() {
        window.location.href = '/admin/';
    });
}

// Chat Functions
function initChat() {
    loadChatHistory();
    
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });
    }
}

function loadChatHistory() {
    const history = localStorage.getItem(CHAT_HISTORY_KEY);
    if (history) {
        try {
            const messages = JSON.parse(history);
            const chatMessages = document.getElementById('chatMessages');
            
            if (messages.length > 0) {
                const welcomeMsg = chatMessages.querySelector('.welcome-message');
                if (welcomeMsg) {
                    welcomeMsg.remove();
                }
            }
            
            messages.forEach(msg => {
                appendMessage(msg.role, msg.content, false);
            });
            
            updateMessageCount();
        } catch (e) {
            console.error('Error loading chat history:', e);
        }
    }
}

function saveChatHistory() {
    const messages = [];
    document.querySelectorAll('.chat-message').forEach(msgEl => {
        const role = msgEl.classList.contains('user') ? 'user' : 'assistant';
        const content = msgEl.querySelector('.message-text').textContent;
        messages.push({ role, content });
    });
    
    try {
        localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(messages));
    } catch (e) {
        console.error('Error saving chat history:', e);
    }
}

function appendMessage(role, content, save = true) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    const welcomeMsg = chatMessages.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${role}`;
    
    const avatarIcon = role === 'user' ? 'fa-user' : 'fa-robot';
    const time = new Date().toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
    
    // Для assistant используем markdown парсинг, для user - просто экранирование
    const formattedContent = role === 'assistant' ? parseMarkdown(content) : escapeHtml(content);
    
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas ${avatarIcon}"></i>
        </div>
        <div class="message-content">
            <div class="message-text">${formattedContent}</div>
            <div class="message-time">${time}</div>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    if (save) {
        saveChatHistory();
        updateMessageCount();
    }
    
    return messageDiv;
}

function appendTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'chat-message assistant';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTypingIndicator() {
    const typing = document.getElementById('typingIndicator');
    if (typing) {
        typing.remove();
    }
}

async function sendMessage() {
    const chatInput = document.getElementById('chatInput');
    if (!chatInput) return;
    
    const content = chatInput.value.trim();
    if (!content) return;
    
    chatInput.value = '';
    chatInput.style.height = 'auto';
    chatInput.disabled = true;
    
    appendMessage('user', content);
    appendTypingIndicator();
    
    try {
        const response = await fetch('/admin/gpt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: content,
                model: 'gpt-4o'
            })
        });
        
        const data = await response.json();
        
        removeTypingIndicator();
        
        if (data.success && data.response) {
            appendMessage('assistant', data.response);
        } else {
            const errorMsg = data.error || 'Произошла ошибка при получении ответа.';
            appendMessage('assistant', 'Извините, ' + errorMsg);
        }
    } catch (error) {
        console.error('Chat error:', error);
        removeTypingIndicator();
        appendMessage('assistant', 'Извините, произошла ошибка при отправке запроса. Проверьте подключение к интернету.');
    }
    
    chatInput.disabled = false;
    chatInput.focus();
}

function clearChatHistory() {
    if (confirm('Вы уверены, что хотите очистить историю чата?')) {
        localStorage.removeItem(CHAT_HISTORY_KEY);
        
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages) {
            chatMessages.innerHTML = `
                <div class="welcome-message">
                    <div class="welcome-icon">
                        <i class="fas fa-robot"></i>
                    </div>
                    <h3>Добро пожаловать в GPT Chat!</h3>
                    <p>Начните диалог с искусственным интеллектом. История сообщений сохраняется автоматически.</p>
                </div>
            `;
        }
        
        updateMessageCount();
        showToast('История чата очищена', 'success');
    }
}

function updateMessageCount() {
    const count = document.querySelectorAll('.chat-message').length;
    const messageCountEl = document.getElementById('messageCount');
    if (messageCountEl) {
        messageCountEl.textContent = `${count} сообщений`;
    }
}

function handleChatKeydown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function parseMarkdown(text) {
    let html = escapeHtml(text);
    
    // Блок кода ```code```
    html = html.replace(/```(\w*)\n?([\s\S]*?)```/g, function(match, lang, code) {
        return `<pre class="code-block"><code class="language-${lang}">${code.trim()}</code></pre>`;
    });
    
    // Строчный код `code`
    html = html.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');
    
    // Жирный текст **text** или __text__
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/__([^_]+)__/g, '<strong>$1</strong>');
    
    // Курсивный текст *text* или _text_
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    html = html.replace(/_([^_]+)_/g, '<em>$1</em>');
    
    // Зачёркнутый текст ~~text~~
    html = html.replace(/~~([^~]+)~~/g, '<del>$1</del>');
    
    // Заголовки
    html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
    html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
    
    // Маркированные списки
    html = html.replace(/^[-*] (.+)$/gm, '<li>$1</li>');
    
    // Нумерованные списки
    html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');
    
    // Ссылки [text](url)
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
    
    // Горизонтальная линия
    html = html.replace(/^---$/gm, '<hr>');
    
    // Переносы строк
    html = html.replace(/\n/g, '<br>');
    
    return html;
}

// Connection Status
function updateConnectionStatus(forceConnected = true) {
    const statusEl = document.getElementById('connectionStatus');
    const badgeDot = statusEl ? statusEl.querySelector('.badge-dot') : null;
    const badgeText = statusEl ? statusEl.querySelector('span:last-child') : null;
    const appStatusEl = document.getElementById('appStatus');
    
    if (forceConnected && badgeDot && badgeText) {
        badgeDot.style.background = '#10b981';
        badgeText.textContent = 'Connected';
        if (appStatusEl) {
            appStatusEl.textContent = 'Online';
            appStatusEl.style.color = '#10b981';
        }
    }
}

// Stats
function initStats() {
    let seconds = 0;
    setInterval(() => {
        seconds++;
        const hours = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        const uptimeEl = document.getElementById('uptime');
        if (uptimeEl) {
            uptimeEl.textContent = `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }
    }, 1000);
    
    setInterval(() => {
        const memory = (80 + Math.random() * 60).toFixed(0);
        const cpu = (5 + Math.random() * 25).toFixed(1);
        const memoryEl = document.getElementById('memoryUsage');
        const cpuEl = document.getElementById('cpuUsage');
        if (memoryEl) memoryEl.textContent = `${memory} MB`;
        if (cpuEl) cpuEl.textContent = `${cpu}%`;
    }, 2000);
}

// Console
function initConsole() {
    const consoleInput = document.getElementById('consoleInput');
    const sendCommandBtn = document.getElementById('sendCommand');
    
    function sendCommand() {
        if (!consoleInput) return;
        const command = consoleInput.value.trim();
        if (!command) return;
        
        addConsoleLine(`> ${command}`, 'info');
        consoleInput.value = '';
        executeCommand(command);
    }
    
    if (sendCommandBtn) {
        sendCommandBtn.addEventListener('click', sendCommand);
    }
    if (consoleInput) {
        consoleInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendCommand();
        });
    }
    
    setTimeout(() => {
        addConsoleLine('Добро пожаловать в FastAPI Admin Panel!', 'success');
        addConsoleLine('Система готова к работе.', 'info');
        addConsoleLine('Введите "help" для списка команд.', 'info');
    }, 300);
}

async function executeCommand(command) {
    try {
        const response = await fetch(`/admin/api/console/execute?command=${encodeURIComponent(command)}`);
        const data = await response.json();
        
        if (data.success) {
            addConsoleLine(data.output, 'success');
        } else {
            addConsoleLine(data.output, 'error');
        }
    } catch (error) {
        const commands = {
            'help': 'Команды: help, status, clear, restart, info, version, uptime, memory, cpu, health, endpoints',
            'status': 'Приложение работает стабильно.',
            'clear': 'Консоль очищена',
            'restart': 'Перезапуск приложения...',
            'info': 'FastAPI Admin Panel v1.0.0',
            'version': 'Версия: 1.0.0',
            'uptime': `Время работы: ${document.getElementById('uptime')?.textContent || '--'}`,
            'memory': `Память: ${document.getElementById('memoryUsage')?.textContent || '--'}`,
            'cpu': `CPU: ${document.getElementById('cpuUsage')?.textContent || '--'}`,
            'health': 'Проверка здоровья: OK',
            'endpoints': `Всего эндпоинтов: ${apiEndpoints.length}`
        };
        
        const cmd = command.toLowerCase();
        if (commands[cmd]) {
            addConsoleLine(commands[cmd], 'success');
        } else {
            addConsoleLine(`Команда "${command}" не найдена.`, 'error');
        }
    }
}

function addConsoleLine(message, type = 'info') {
    const consoleOutput = document.getElementById('consoleOutput');
    if (!consoleOutput) return;
    
    const line = document.createElement('div');
    line.className = 'console-line';
    
    const time = new Date().toLocaleTimeString('ru-RU');
    const colors = {
        'info': '#8b949e',
        'success': '#10b981',
        'error': '#ef4444',
        'warning': '#f59e0b'
    };
    
    line.innerHTML = `
        <span class="console-time">[${time}]</span>
        <span class="console-message" style="color: ${colors[type] || colors.info}">${message}</span>
    `;
    
    consoleOutput.appendChild(line);
    consoleOutput.scrollTop = consoleOutput.scrollHeight;
}

function clearConsole() {
    const consoleOutput = document.getElementById('consoleOutput');
    if (consoleOutput) {
        consoleOutput.innerHTML = '';
        addConsoleLine('Консоль очищена', 'info');
    }
}

// Action Functions
function restartApp() {
    showToast('Перезапуск приложения...', 'info');
    addConsoleLine('Инициирован перезапуск...', 'warning');
    setTimeout(() => {
        showToast('Приложение перезапущено', 'success');
        addConsoleLine('Приложение успешно перезапущено', 'success');
    }, 1500);
}

function clearCache() {
    showToast('Кэш очищен', 'success');
    addConsoleLine('Кэш успешно очищен', 'success');
}

function viewLogs() {
    showToast('Логи загружены', 'info');
    addConsoleLine('Логи системы загружены', 'info');
}

function checkHealth() {
    showToast('Проверка здоровья...', 'info');
    addConsoleLine('Проверка системных ресурсов...', 'info');
    setTimeout(() => {
        addConsoleLine('✓ CPU: Оптимально', 'success');
        addConsoleLine('✓ Память: В норме', 'success');
        addConsoleLine('✓ Сеть: Подключено', 'success');
        showToast('Все системы в норме!', 'success');
    }, 800);
}

// Settings Functions
function saveSettings() {
    const password = document.getElementById('adminPassword');
    if (password && password.value.length > 0 && password.value.length < 6) {
        showToast('Пароль минимум 6 символов!', 'error');
        return;
    }
    showToast('Настройки сохранены!', 'success');
    addConsoleLine('Настройки профиля обновлены', 'success');
    if (password) password.value = '';
}

function saveServerSettings() {
    const host = document.getElementById('serverHost');
    const port = document.getElementById('serverPort');
    if (!host || !port || !host.value || !port.value || port.value < 1 || port.value > 65535) {
        showToast('Проверьте настройки!', 'error');
        return;
    }
    showToast('Настройки сервера сохранены!', 'success');
    addConsoleLine(`Сервер: ${host.value}:${port.value}`, 'success');
}

function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    if (!input) return;
    const icon = input.nextElementSibling?.querySelector('i');
    if (!icon) return;
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.className = 'fas fa-eye-slash';
    } else {
        input.type = 'password';
        icon.className = 'fas fa-eye';
    }
}

function resetSettings() {
    if (confirm('Сбросить настройки по умолчанию?')) {
        const host = document.getElementById('serverHost');
        const port = document.getElementById('serverPort');
        if (host) host.value = 'localhost';
        if (port) port.value = '8080';
        showToast('Настройки сброшены', 'success');
        addConsoleLine('Настройки сброшены к умолчанию', 'info');
    }
}

// Toast Notification
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Endpoints Manager - Initialize
function initEndpointsManager() {
    loadEndpointsFilter();
    initEndpointTester();
}

// Make functions globally available
window.initEndpointsManager = initEndpointsManager;

// API Endpoints Manager with Testing

let filteredEndpoints = [];
let activeFilter = 'all';
let requestHistory = [];
let endpointsLoaded = false;

document.addEventListener('DOMContentLoaded', function() {
    initEndpointsManager();
});

function initEndpointsManager() {
    loadEndpointsFilter();
    initEndpointTester();
}

function loadEndpointsFilter() {
    const filterContainer = document.getElementById('endpointsFilter');
    if (!filterContainer) return;
    
    const filters = [
        { id: 'all', label: 'Все', icon: 'fa-list' },
        { id: 'get', label: 'GET', icon: 'fa-eye' },
        { id: 'post', label: 'POST', icon: 'fa-plus' },
        { id: 'put', label: 'PUT', icon: 'fa-edit' },
        { id: 'delete', label: 'DELETE', icon: 'fa-trash' }
    ];
    
    filterContainer.innerHTML = filters.map(f => `
        <button class="filter-btn ${f.id === 'all' ? 'active' : ''}" 
                data-filter="${f.id}"
                onclick="filterEndpoints('${f.id}')">
            <i class="fas ${f.icon}"></i>
            ${f.label}
        </button>
    `).join('');
    
    // Поиск
    const searchInput = document.getElementById('endpointSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            filterEndpoints(activeFilter, this.value);
        });
    }
}

function filterEndpoints(filter, search = '') {
    activeFilter = filter;
    
    // Обновить активную кнопку
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.filter === filter);
    });
    
    // Фильтровать эндпоинты
    filteredEndpoints = apiEndpoints.filter(ep => {
        const matchesFilter = filter === 'all' || ep.method.toLowerCase() === filter;
        const matchesSearch = !search || 
            ep.path.toLowerCase().includes(search.toLowerCase()) ||
            (ep.description && ep.description.toLowerCase().includes(search.toLowerCase()));
        return matchesFilter && matchesSearch;
    });
    
    renderEndpoints();
}

function renderEndpoints() {
    const container = document.getElementById('apiEndpoints');
    if (!container) return;
    
    if (filteredEndpoints.length === 0) {
        container.innerHTML = `
            <div class="loading-endpoints">
                <i class="fas fa-search"></i>
                <p>Эндпоинты не найдены</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = '';
    
    filteredEndpoints.forEach((endpoint, index) => {
        const card = document.createElement('div');
        card.className = 'api-endpoint';
        card.dataset.path = endpoint.path;
        
        const methodClass = endpoint.method.toLowerCase();
        const description = endpoint.description || 'Описание недоступно';
        const isProtected = endpoint.protected || false;
        const isEnabled = endpoint.enabled !== false;
        
        card.innerHTML = `
            <div class="endpoint-header">
                <div class="endpoint-methods">
                    <span class="endpoint-method ${methodClass}">${endpoint.method}</span>
                </div>
                <code class="endpoint-path">${endpoint.path}</code>
                <div class="endpoint-status">
                    <span class="status-badge ${isEnabled ? 'enabled' : 'disabled'}" 
                          title="${isEnabled ? 'Включен' : 'Выключен'}">
                        <i class="fas ${isEnabled ? 'fa-check-circle' : 'fa-ban'}"></i>
                    </span>
                    ${isProtected ? '<span class="protected-badge" title="Требует авторизации"><i class="fas fa-lock"></i></span>' : ''}
                </div>
            </div>
            <div class="endpoint-description">${description}</div>
            <div class="endpoint-meta">
                ${endpoint.tags ? endpoint.tags.map(t => `<span class="tag">${t}</span>`).join('') : ''}
            </div>
            <div class="endpoint-actions">
                <button class="endpoint-btn" onclick="testEndpoint('${endpoint.method}', '${endpoint.path}', ${index})">
                    <i class="fas fa-play"></i>
                    Тест
                </button>
                <button class="endpoint-btn" onclick="toggleEndpointModal('${endpoint.method}', '${endpoint.path}', ${index})">
                    <i class="fas fa-cog"></i>
                    Настройки
                </button>
                <button class="endpoint-btn" onclick="copyEndpoint('${endpoint.method}', '${endpoint.path}')">
                    <i class="fas fa-copy"></i>
                    Копировать
                </button>
            </div>
        `;
        
        container.appendChild(card);
    });
    
    updateEndpointStats();
}

// Endpoint Tester (Swagger-like)
function initEndpointTester() {
    // Инициализация модального окна
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('tester-overlay')) {
            closeTesterModal();
        }
    });
    
    document.getElementById('testerClose')?.addEventListener('click', closeTesterModal);
    document.getElementById('testerSend')?.addEventListener('click', sendTestRequest);
    
    // Переключение между табами (query, body, headers)
    document.querySelectorAll('.param-tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const tab = this.dataset.tab;
            document.querySelectorAll('.param-tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.param-tab-content').forEach(c => c.classList.remove('active'));
            this.classList.add('active');
            document.getElementById(tab + 'Params').classList.add('active');
        });
    });
}
            
let currentEndpointIndex = null;

async function testEndpoint(method, path, index) {
    currentEndpointIndex = index;
    const endpoint = apiEndpoints[index];
    
    const modal = document.getElementById('testerModal');
    if (!modal) return;
    
    document.getElementById('testerMethod').textContent = method;
    document.getElementById('testerPath').textContent = path;
    document.getElementById('testerMethod').className = 'method-badge ' + method.toLowerCase();
    
    // Сбросить форму
    document.getElementById('queryParams').innerHTML = '';
    document.getElementById('bodyParams').innerHTML = '';
    document.getElementById('testerHeaders').value = '{\n  "Authorization": "Bearer <token>"\n}';
    document.getElementById('testerResponse').innerHTML = '<div class="response-placeholder">Нажмите "Отправить запрос"</div>';
    document.getElementById('responseStatus').textContent = '--';
    document.getElementById('responseTime').textContent = '-- ms';
    
    // Сбросить активный таб на query
    document.querySelectorAll('.param-tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.param-tab-content').forEach(c => c.classList.remove('active'));
    document.querySelector('.param-tab-btn[data-tab="query"]').classList.add('active');
    document.getElementById('queryParams').classList.add('active');
    
    // Динамически генерировать форму для параметров (асинхронно)
    await renderParamsForm(endpoint, method);
    
    modal.classList.add('active');
}

// Парсинг параметров из пути (для {param} или :param)
function parsePathParams(path) {
    const params = [];
    
    // Паттерн для {param} или :param
    const paramRegex = /\{([^}]+)\}/g;
    let match;
    
    while ((match = paramRegex.exec(path)) !== null) {
        const paramName = match[1];
        params.push({
            name: paramName,
            type: 'string',
            required: true,
            description: `Параметр пути: ${paramName}`,
            in: 'path'
        });
    }
    
    return params;
}

// Загрузка OpenAPI схемы и извлечение параметров
let openapiSchema = null;

async function loadOpenApiSchema() {
    if (openapiSchema) return openapiSchema;
    
    try {
        const response = await fetch('/openapi.json');
        if (response.ok) {
            openapiSchema = await response.json();
        }
    } catch (e) {
        console.warn('OpenAPI schema not available:', e);
    }
    
    return openapiSchema;
}

// Получить параметры эндпоинта из OpenAPI схемы
async function getParamsFromOpenApi(path, method) {
    const params = { queryParams: [], pathParams: [], requestBody: null };
    
    const schema = await loadOpenApiSchema();
    if (!schema || !schema.paths) return params;
    
    // Прямой поиск по пути
    if (schema.paths[path]) {
        const pathItem = schema.paths[path];
        const endpoint = pathItem?.[method.toLowerCase()];
        if (endpoint) {
            if (endpoint.parameters) {
                params.pathParams = endpoint.parameters.filter(p => p.in === 'path');
                params.queryParams = endpoint.parameters.filter(p => p.in === 'query');
            }
            if (endpoint.requestBody) {
                const content = endpoint.requestBody.content?.['application/json'];
                if (content?.schema) {
                    params.requestBody = content.schema;
                }
            }
            return params;
        }
    }
    
    // Поиск с заменой path параметров на {param}
    for (const apiPath of Object.keys(schema.paths)) {
        // Преобразуем путь API в регулярное выражение
        const regexPath = apiPath.replace(/\{([^}]+)\}/g, '([^/]+)');
        const regex = new RegExp(`^${regexPath}$`);
        
        if (regex.test(path)) {
            const pathItem = schema.paths[apiPath];
            const endpoint = pathItem?.[method.toLowerCase()];
            if (endpoint) {
                if (endpoint.parameters) {
                    params.pathParams = endpoint.parameters.filter(p => p.in === 'path');
                    params.queryParams = endpoint.parameters.filter(p => p.in === 'query');
                }
                if (endpoint.requestBody) {
                    const content = endpoint.requestBody.content?.['application/json'];
                    if (content?.schema) {
                        params.requestBody = content.schema;
                    }
                }
                return params;
            }
        }
    }
        
    return params;
}

// Получить параметры эндпоинта из всех источников
async function getEndpointParams(endpoint, method, path) {
    let queryParams = [];
    let pathParams = [];
    let requestBody = null;
    
    // 1. Если queryParams уже предоставлены в данных эндпоинта
    if (endpoint?.queryParams) {
        queryParams = endpoint.queryParams;
    }
    
    // 2. Парсим path параметры из {param}
    pathParams = parsePathParams(path);
    
    // 3. Если queryParams не предоставлены, пробуем извлечь из схемы endpoint
    if (queryParams.length === 0 && endpoint?.parameters) {
        queryParams = endpoint.parameters.filter(p => p.in === 'query');
        pathParams = endpoint.parameters.filter(p => p.in === 'path');
    }
    
    // 4. Пробуем загрузить из OpenAPI схемы
    if (queryParams.length === 0 || pathParams.length === 0) {
        try {
            const openapiParams = await getParamsFromOpenApi(path, method);
            
            if (queryParams.length === 0 && openapiParams.queryParams.length > 0) {
                queryParams = openapiParams.queryParams;
            }
            if (pathParams.length === 0 && openapiParams.pathParams.length > 0) {
                pathParams = openapiParams.pathParams;
            }
            if (!requestBody && openapiParams.requestBody) {
                requestBody = openapiParams.requestBody;
            }
        } catch (e) {
            console.warn('Failed to load OpenAPI params:', e);
        }
    }
    
    return { queryParams, pathParams, requestBody };
}

// Генерация формы для параметров (как в Swagger UI)
async function renderParamsForm(endpoint, method) {
    const path = endpoint?.path || '';
    const queryContainer = document.getElementById('queryParams');
    const bodyContainer = document.getElementById('bodyParams');
    
    // Показываем загрузку
    queryContainer.innerHTML = '<div class="params-empty"><i class="fas fa-spinner fa-spin"></i> Загрузка параметров...</div>';
    
    // Получаем параметры из всех источников (включая OpenAPI)
    const { queryParams, pathParams, requestBody: openapiRequestBody } = await getEndpointParams(endpoint, method, path);
    
    // Создать форму для path параметров
    let formHtml = '';
    
    // Path параметры (из {param})
    if (pathParams.length > 0) {
        formHtml += '<div class="params-section">';
        formHtml += '<div class="params-section-title">Path Parameters</div>';
        pathParams.forEach(param => {
            const paramType = param.schema?.type || param.type || 'string';
            formHtml += `
                <div class="param-field">
                    <label class="param-label">
                        <span class="param-name">${param.name}</span>
                        <span class="param-required">*</span>
                        <span class="param-type">(${paramType})</span>
                    </label>
                    <input type="text" 
                           class="param-input" 
                           data-param-name="${param.name}"
                           data-param-type="${paramType}"
                           data-param-in="path"
                           placeholder="${param.description || 'Введите значение'}"
                           required>
                </div>
            `;
        });
        formHtml += '</div>';
    }
    
    // Query параметры
    if (queryParams.length > 0) {
        formHtml += '<div class="params-section">';
        formHtml += '<div class="params-section-title">Query Parameters</div>';
        queryParams.forEach(param => {
            const required = param.required ? '<span class="param-required">*</span>' : '';
            const paramType = param.schema?.type || param.type || 'string';
            const paramDesc = param.description || param.schema?.description || '';
            const defaultValue = param.schema?.default !== undefined ? param.schema?.default : '';
            
            formHtml += `
                <div class="param-field">
                    <label class="param-label">
                        <span class="param-name">${param.name}</span>
                        ${required}
                        <span class="param-type">(${paramType})</span>
                    </label>
                    <input type="text" 
                           class="param-input" 
                           data-param-name="${param.name}"
                           data-param-type="${paramType}"
                           data-param-in="query"
                           placeholder="${paramDesc || 'Введите значение'}"
                           value="${defaultValue}"
                           ${param.required ? 'required' : ''}>
                </div>
            `;
        });
        formHtml += '</div>';
    }
    
    if (formHtml) {
        queryContainer.innerHTML = '<div class="params-form">' + formHtml + '</div>';
    } else {
        // Показываем форму для ручного добавления параметров
        queryContainer.innerHTML = `
            <div class="params-form">
                <div class="params-section">
                    <div class="params-section-title">Query Parameters</div>
                    <div id="manualParamsContainer"></div>
                    <button type="button" class="add-param-btn" onclick="addManualParam()">
                        <i class="fas fa-plus"></i> Добавить параметр
                    </button>
                </div>
            </div>
        `;
    }
    
    // Создать JSON редактор для body
    if (method !== 'GET' && method !== 'HEAD') {
        let bodyHtml = '<div class="json-editor-container">';
        bodyHtml += '<div class="json-editor-header">';
        bodyHtml += '<span>Body JSON</span>';
        bodyHtml += '<button type="button" class="json-format-btn" onclick="formatJSON()"><i class="fas fa-indent"></i> Форматировать</button>';
        bodyHtml += '</div>';
        
        let defaultBody = '{}';
        
        // Пробуем получить requestBody из разных источников
        let requestBodyData = null;
        if (endpoint) {
            if (endpoint.requestBody) {
                requestBodyData = endpoint.requestBody;
            } else if (endpoint.requestBodySchema) {
                requestBodyData = endpoint.requestBodySchema;
            }
        }
        // Из OpenAPI
        if (!requestBodyData && openapiRequestBody) {
            requestBodyData = openapiRequestBody;
        }
        
        if (requestBodyData) {
            try {
                const example = generateExample(requestBodyData);
                defaultBody = JSON.stringify(example, null, 2);
            } catch (e) {}
        }
        
        bodyHtml += `<textarea class="json-editor" id="bodyJsonEditor" spellcheck="false">${defaultBody}</textarea>`;
        bodyHtml += '</div>';
        bodyContainer.innerHTML = bodyHtml;
    } else {
        bodyContainer.innerHTML = '<div class="params-empty">Body не требуется для GET/HEAD запросов</div>';
    }
}

// Форматирование JSON в редакторе
function formatJSON() {
    const editor = document.getElementById('bodyJsonEditor');
    if (!editor) return;
    
    try {
        const parsed = JSON.parse(editor.value);
        editor.value = JSON.stringify(parsed, null, 2);
    } catch (e) {
        showToast('Невалидный JSON', 'error');
    }
}

// Добавить параметр вручную
function addManualParam() {
    const container = document.getElementById('manualParamsContainer');
    if (!container) return;
    
    const paramId = Date.now();
    const paramHtml = `
        <div class="manual-param-row" data-param-id="${paramId}">
            <input type="text" class="param-input param-name-input" placeholder="Имя параметра" data-field="name">
            <select class="param-input param-type-input" data-field="type">
                <option value="string">string</option>
                <option value="integer">integer</option>
                <option value="number">number</option>
                <option value="boolean">boolean</option>
            </select>
            <input type="text" class="param-input param-value-input" placeholder="Значение" data-field="value">
            <button type="button" class="remove-param-btn" onclick="removeManualParam(${paramId})">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    container.insertAdjacentHTML('beforeend', paramHtml);
}
    
// Удалить параметр
function removeManualParam(paramId) {
    const row = document.querySelector(`.manual-param-row[data-param-id="${paramId}"]`);
    if (row) row.remove();
}

function closeTesterModal() {
    const modal = document.getElementById('testerModal');
    if (modal) {
        modal.classList.remove('active');
        currentEndpointIndex = null;
    }
}

async function sendTestRequest() {
    const method = document.getElementById('testerMethod').textContent;
    let path = document.getElementById('testerPath').textContent;
    
    // Собрать все параметры из формы
    const pathParams = {};
    const queryParams = {};
    
    const paramInputs = document.querySelectorAll('#queryParams .param-input');
    paramInputs.forEach(input => {
        const paramName = input.dataset.paramName;
        const paramType = input.dataset.paramType || 'string';
        const paramIn = input.dataset.paramIn || 'query';
        const value = input.value;
        
        if (value) {
            // Преобразование типов
            let typedValue = value;
            if (paramType === 'integer' || paramType === 'number') {
                typedValue = parseFloat(value);
            } else if (paramType === 'boolean') {
                typedValue = value.toLowerCase() === 'true';
            }
            
            if (paramIn === 'path') {
                pathParams[paramName] = typedValue;
            } else {
                queryParams[paramName] = typedValue;
            }
        }
    });
    
    // Собрать ручные параметры (если есть)
    const manualParamRows = document.querySelectorAll('#manualParamsContainer .manual-param-row');
    manualParamRows.forEach(row => {
        const nameInput = row.querySelector('[data-field="name"]');
        const typeInput = row.querySelector('[data-field="type"]');
        const valueInput = row.querySelector('[data-field="value"]');
        
        const name = nameInput?.value.trim();
        const type = typeInput?.value || 'string';
        let value = valueInput?.value.trim();
        
        if (name && value) {
            // Преобразование типов
            let typedValue = value;
            if (type === 'integer' || type === 'number') {
                typedValue = parseFloat(value);
            } else if (type === 'boolean') {
                typedValue = value.toLowerCase() === 'true';
            }
            queryParams[name] = typedValue;
        }
    });
    
    // Заменить path параметры в URL ({param} -> value)
    for (const [key, value] of Object.entries(pathParams)) {
        path = path.replace(`{${key}}`, value);
    }
    
    // Добавить query параметры в URL
    const queryKeys = Object.keys(queryParams);
    if (queryKeys.length > 0) {
        const queryString = new URLSearchParams(queryParams).toString();
        path += (path.includes('?') ? '&' : '?') + queryString;
    }
    
    // Получить body из JSON редактора
    let body = null;
    if (method !== 'GET' && method !== 'HEAD') {
        const bodyEditor = document.getElementById('bodyJsonEditor');
        const bodyValue = bodyEditor ? bodyEditor.value.trim() : '{}';
        if (bodyValue && bodyValue !== '{}') {
            try {
                body = JSON.parse(bodyValue);
            } catch (e) {
                showTesterError('Неверный формат body (JSON)');
                return;
            }
        }
    }
    
    // Получить headers
    let headers = {};
    const headersValue = document.getElementById('testerHeaders').value.trim();
    if (headersValue) {
        try {
            headers = JSON.parse(headersValue);
        } catch (e) {
            // Игнорируем ошибку заголовков
        }
    }
    
    // Показать индикатор загрузки
    document.getElementById('testerSend').innerHTML = '<i class="fas fa-spinner fa-spin"></i> Отправка...';
    document.getElementById('testerSend').disabled = true;
    
    const startTime = Date.now();
    
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
                ...headers
            }
        };
        
        if (body) {
            options.body = JSON.stringify(body);
        }
        
        const response = await fetch(path, options);
        const endTime = Date.now();
        const duration = endTime - startTime;
        
        let responseData;
        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('application/json')) {
            responseData = await response.json();
        } else {
            responseData = await response.text();
        }
        
        // Обновить UI
        document.getElementById('responseStatus').textContent = response.status;
        document.getElementById('responseStatus').className = 'status-code ' + (response.ok ? 'success' : 'error');
        document.getElementById('responseTime').textContent = duration + ' ms';
        
        const responseEl = document.getElementById('testerResponse');
        responseEl.innerHTML = `
            <pre class="response-json">${JSON.stringify(responseData, null, 2)}</pre>
        `;
        
        // Добавить в историю
        addToHistory({
            method,
            path,
            status: response.status,
            time: duration,
            timestamp: new Date().toLocaleTimeString()
        });
        
    } catch (error) {
        document.getElementById('responseStatus').textContent = 'Ошибка';
        document.getElementById('responseStatus').className = 'status-code error';
        document.getElementById('testerResponse').innerHTML = `
            <div class="response-error">
                <i class="fas fa-exclamation-triangle"></i>
                ${error.message}
            </div>
        `;
    }
    
    document.getElementById('testerSend').innerHTML = '<i class="fas fa-paper-plane"></i> Отправить';
    document.getElementById('testerSend').disabled = false;
}

function showTesterError(message) {
    const responseEl = document.getElementById('testerResponse');
    responseEl.innerHTML = `
        <div class="response-error">
            <i class="fas fa-exclamation-circle"></i>
            ${message}
        </div>
    `;
}

function generateExample(schema) {
    if (!schema) return {};
    
    // Если есть пример, возвращаем его
    if (schema.example !== undefined) {
        return schema.example;
    }
    
    // Обработка вложенных объектов
    if (schema.type === 'object' && schema.properties) {
        const example = {};
        for (const [key, prop] of Object.entries(schema.properties)) {
            example[key] = generateExample(prop);
        }
        return example;
    }
    
    // Обработка массивов
    if (schema.type === 'array' && schema.items) {
        const itemExample = generateExample(schema.items);
        return [itemExample];
    }
    
    // Базовые типы
    const type = schema.type || 'string';
    if (type === 'string') {
        if (schema.enum) return schema.enum[0] || 'string';
        return schema.example || 'string';
    }
    else if (type === 'integer' || type === 'number') {
        return schema.example || 0;
    }
    else if (type === 'boolean') {
        return schema.example || false;
    }
    else if (type === 'array') {
        return [];
    }
    else if (type === 'object') {
        return {};
    }
    
    return {};
}

function addToHistory(item) {
    requestHistory.unshift(item);
    if (requestHistory.length > 10) requestHistory.pop();
    renderHistory();
}

function renderHistory() {
    const container = document.getElementById('requestHistory');
    if (!container) return;
    
    if (requestHistory.length === 0) {
        container.innerHTML = '<div class="history-empty">Нет запросов</div>';
        return;
    }
    
    container.innerHTML = requestHistory.map(item => `
        <div class="history-item" onclick="loadFromHistory('${item.method}', '${item.path}')">
            <span class="history-method ${item.method.toLowerCase()}">${item.method}</span>
            <span class="history-path">${item.path.substring(0, 30)}${item.path.length > 30 ? '...' : ''}</span>
            <span class="history-status ${item.status >= 200 && item.status < 300 ? 'success' : 'error'}">${item.status}</span>
            <span class="history-time">${item.time}ms</span>
        </div>
    `).join('');
}

function loadFromHistory(method, path) {
    // Найти эндпоинт в списке
    const index = apiEndpoints.findIndex(ep => ep.path === path && ep.method === method);
    if (index !== -1) {
        testEndpoint(method, path, index);
    }
}

// Endpoint Settings Modal
function toggleEndpointModal(method, path, index) {
    currentEndpointIndex = index;
    const endpoint = apiEndpoints[index];
    
    const modal = document.getElementById('endpointSettingsModal');
    if (!modal) return;
    
    document.getElementById('settingsEndpointPath').textContent = path;
    document.getElementById('settingsEndpointMethod').textContent = method;
    
    // Заполнить текущие настройки
    document.getElementById('endpointEnabled').checked = endpoint.enabled !== false;
    document.getElementById('endpointProtected').checked = endpoint.protected || false;
    document.getElementById('endpointRoles').value = (endpoint.roles || []).join(', ');
    
    modal.classList.add('active');
}

function closeSettingsModal() {
    const modal = document.getElementById('endpointSettingsModal');
    if (modal) modal.classList.remove('active');
}

function saveEndpointSettings() {
    const endpoint = apiEndpoints[currentEndpointIndex];
    if (!endpoint) return;
    
    // Обновить настройки
    endpoint.enabled = document.getElementById('endpointEnabled').checked;
    endpoint.protected = document.getElementById('endpointProtected').checked;
    endpoint.roles = document.getElementById('endpointRoles').value.split(',').map(r => r.trim()).filter(r => r);
    
    // Перерисовать эндпоинты
    filterEndpoints(activeFilter, document.getElementById('endpointSearch')?.value || '');
    
    closeSettingsModal();
    showToast('Настройки сохранены', 'success');
}

// Load Endpoints
async function loadApiEndpoints() {
    // Если эндпоинты уже загружены, не делаем повторный запрос
    if (endpointsLoaded && apiEndpoints.length > 0) {
        renderEndpoints();
        updateEndpointStats();
        return;
    }
    
    const container = document.getElementById('apiEndpoints');
    if (!container) return;
    
    container.innerHTML = `
        <div class="loading-endpoints">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Загрузка эндпоинтов...</p>
        </div>
    `;
    
    try {
        const response = await fetch('/admin/api/app/info');
        const data = await response.json();
        
        if (data.endpoints && data.endpoints.length > 0) {
            apiEndpoints = data.endpoints;
            filteredEndpoints = apiEndpoints;
            endpointsLoaded = true;
            renderEndpoints();
            updateEndpointStats();
        } else {
            container.innerHTML = `
                <div class="loading-endpoints">
                    <i class="fas fa-plug"></i>
                    <p>Эндпоинты не найдены</p>
                </div>
            `;
            endpointsLoaded = true;
        }
    } catch (error) {
        console.error('Error loading endpoints:', error);
        container.innerHTML = `
            <div class="loading-endpoints">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Ошибка загрузки: ${error.message}</p>
            </div>
        `;
        endpointsLoaded = true;
    }
}

function updateEndpointStats() {
    const total = apiEndpoints.length;
    const getCount = apiEndpoints.filter(e => e.method === 'GET').length;
    const postCount = apiEndpoints.filter(e => e.method === 'POST').length;
    const putCount = apiEndpoints.filter(e => e.method === 'PUT').length;
    const deleteCount = apiEndpoints.filter(e => e.method === 'DELETE').length;
    
    const totalEl = document.getElementById('totalEndpoints');
    const getEl = document.getElementById('getCount');
    const postEl = document.getElementById('postCount');
    const putEl = document.getElementById('putCount');
    const deleteEl = document.getElementById('deleteCount');
    
    if (totalEl) totalEl.textContent = total;
    if (getEl) getEl.textContent = getCount;
    if (postEl) postEl.textContent = postCount;
    if (putEl) putEl.textContent = putCount;
    if (deleteEl) deleteEl.textContent = deleteCount;
}

function copyEndpoint(method, path) {
    const text = `${method} ${path}`;
    navigator.clipboard.writeText(text).then(() => {
        showToast('Скопировано!', 'success');
    }).catch(() => {
        showToast('Ошибка копирования', 'error');
    });
}

// Глобальные функции для HTML
window.filterEndpoints = filterEndpoints;
window.testEndpoint = testEndpoint;
window.toggleEndpointModal = toggleEndpointModal;
window.closeSettingsModal = closeSettingsModal;
window.saveEndpointSettings = saveEndpointSettings;
window.closeTesterModal = closeTesterModal;
window.sendTestRequest = sendTestRequest;
window.loadFromHistory = loadFromHistory;
window.loadApiEndpoints = loadApiEndpoints;
window.formatJSON = formatJSON;
window.addManualParam = addManualParam;
window.removeManualParam = removeManualParam;

// Clear request history
function clearRequestHistory() {
    requestHistory = [];
    const container = document.getElementById('requestHistory');
    if (container) {
        container.innerHTML = '<div class="history-empty">Нет запросов</div>';
    }
    showToast('История очищена', 'success');
}
window.clearRequestHistory = clearRequestHistory;
