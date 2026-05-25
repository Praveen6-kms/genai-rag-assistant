// Generate unique session ID
const sessionId = localStorage.getItem('sessionId') || 
    'session_' + Math.random().toString(36).substr(2, 9);
localStorage.setItem('sessionId', sessionId);

// Set initial timestamp
document.getElementById('initTime').textContent = getTime();

function getTime() {
    const now = new Date();
    return now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
}

function handleKeyPress(event) {
    if (event.key === 'Enter') sendMessage();
}

function newChat() {
    // Clear messages
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.innerHTML = `
        <div class="message-wrapper bot-wrapper">
            <div class="message bot-message">
                👋 Hello! I'm your AI assistant powered by RAG technology.
                How can I help you today?
            </div>
            <span class="timestamp">${getTime()}</span>
        </div>
    `;
    // Generate new session
    const newSessionId = 'session_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('sessionId', newSessionId);
    location.reload();
}

async function sendMessage() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    if (!message) return;

    // Show user message
    addMessage(message, 'user');
    input.value = '';

    // Show typing indicator
    showTyping(true);

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                sessionId: sessionId,
                message: message
            })
        });

        const data = await response.json();
        showTyping(false);

        if (data.reply) {
            addMessage(data.reply, 'bot', data.retrievedChunks);
        } else if (data.error) {
            addMessage('⚠️ ' + data.error, 'bot');
        }

    } catch (error) {
        showTyping(false);
        addMessage('⚠️ Connection error. Please try again!', 'bot');
    }
}

function addMessage(text, sender, chunks = 0) {
    const chatMessages = document.getElementById('chatMessages');

    const wrapper = document.createElement('div');
    wrapper.classList.add('message-wrapper');
    wrapper.classList.add(sender === 'user' ? 'user-wrapper' : 'bot-wrapper');

    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    messageDiv.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
    messageDiv.innerHTML = `<p>${text}</p>`;

    const timestamp = document.createElement('span');
    timestamp.classList.add('timestamp');
    timestamp.textContent = getTime();

    wrapper.appendChild(messageDiv);

    // Show chunks badge for bot messages
    if (sender === 'bot' && chunks > 0) {
        const badge = document.createElement('span');
        badge.classList.add('chunks-badge');
        badge.textContent = `📚 ${chunks} relevant document${chunks > 1 ? 's' : ''} retrieved`;
        wrapper.appendChild(badge);
    }

    wrapper.appendChild(timestamp);
    chatMessages.appendChild(wrapper);

    // Auto scroll
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTyping(show) {
    const indicator = document.getElementById('typingWrapper');
    indicator.style.display = show ? 'block' : 'none';
    
    if (show) {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}