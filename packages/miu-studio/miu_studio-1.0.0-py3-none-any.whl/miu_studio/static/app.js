/**
 * miu Studio WebSocket Chat Client
 */

// DOM elements
const chatEl = document.getElementById('chat');
const inputEl = document.getElementById('input');
const sendBtn = document.getElementById('send');
const statusEl = document.getElementById('status');
const sessionIdEl = document.getElementById('session-id');

// State
let ws = null;
let sessionId = null;
let currentAssistantMessage = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);

async function init() {
    await createSession();
    connectWebSocket();

    // Enter key to send
    inputEl.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            send();
        }
    });
}

async function createSession() {
    try {
        const response = await fetch('/api/v1/sessions/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: 'Web Chat' })
        });

        if (!response.ok) {
            throw new Error(`Failed to create session: ${response.status}`);
        }

        const data = await response.json();
        sessionId = data.id;
        sessionIdEl.textContent = sessionId.substring(0, 8) + '...';
        addMessage('system', `Session created: ${sessionId.substring(0, 8)}...`);
    } catch (error) {
        addMessage('error', `Failed to create session: ${error.message}`);
    }
}

function connectWebSocket() {
    if (!sessionId) {
        setTimeout(connectWebSocket, 1000);
        return;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/v1/chat/ws/${sessionId}`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        setConnected(true);
        addMessage('system', 'Connected to server');
    };

    ws.onclose = (event) => {
        setConnected(false);
        if (event.code !== 1000) {
            addMessage('system', `Disconnected (code: ${event.code}). Reconnecting...`);
            setTimeout(connectWebSocket, 3000);
        }
    };

    ws.onerror = () => {
        addMessage('error', 'WebSocket error occurred');
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            handleMessage(data);
        } catch (error) {
            console.error('Failed to parse message:', error);
        }
    };
}

function handleMessage(data) {
    switch (data.type) {
        case 'chunk':
            if (!currentAssistantMessage) {
                currentAssistantMessage = addMessage('assistant', '', true);
            }
            appendToMessage(currentAssistantMessage, data.content);
            break;

        case 'done':
            if (currentAssistantMessage) {
                finalizeMessage(currentAssistantMessage);
                currentAssistantMessage = null;
            }
            setInputEnabled(true);
            break;

        case 'error':
            addMessage('error', data.content);
            currentAssistantMessage = null;
            setInputEnabled(true);
            break;
    }
}

function send() {
    const message = inputEl.value.trim();
    if (!message || !ws || ws.readyState !== WebSocket.OPEN) {
        return;
    }

    addMessage('user', message);
    inputEl.value = '';
    setInputEnabled(false);

    ws.send(JSON.stringify({ message }));
}

function addMessage(role, content, streaming = false) {
    const messageEl = document.createElement('div');
    messageEl.className = `message ${role}`;

    if (role !== 'system') {
        const roleEl = document.createElement('div');
        roleEl.className = 'role';
        roleEl.textContent = role === 'user' ? 'You' : role === 'assistant' ? 'Assistant' : 'Error';
        messageEl.appendChild(roleEl);
    }

    const contentEl = document.createElement('div');
    contentEl.className = 'content';
    contentEl.textContent = content;

    if (streaming) {
        contentEl.classList.add('typing');
    }

    messageEl.appendChild(contentEl);
    chatEl.appendChild(messageEl);
    chatEl.scrollTop = chatEl.scrollHeight;

    return messageEl;
}

function appendToMessage(messageEl, content) {
    const contentEl = messageEl.querySelector('.content');
    if (contentEl) {
        contentEl.textContent += content;
        chatEl.scrollTop = chatEl.scrollHeight;
    }
}

function finalizeMessage(messageEl) {
    const contentEl = messageEl.querySelector('.content');
    if (contentEl) {
        contentEl.classList.remove('typing');
    }
}

function setConnected(connected) {
    statusEl.textContent = connected ? 'Connected' : 'Disconnected';
    statusEl.className = connected ? 'connected' : '';
    setInputEnabled(connected);
}

function setInputEnabled(enabled) {
    inputEl.disabled = !enabled;
    sendBtn.disabled = !enabled;
    if (enabled) {
        inputEl.focus();
    }
}
