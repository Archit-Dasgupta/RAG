const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

// Chat Handling
function addMessage(text, sender) {
    const div = document.createElement('div');
    div.className = `message ${sender}`;
    div.textContent = text;

    // Insert before typing indicator if it exists
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator && typingIndicator.parentNode === chatMessages) {
        chatMessages.insertBefore(div, typingIndicator);
    } else {
        chatMessages.appendChild(div);
    }

    scrollToBottom();
}

function scrollToBottom() {
    requestAnimationFrame(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    });
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    // Hide suggested questions after first message
    const suggestionsContainer = document.getElementById('suggested-questions');
    if (suggestionsContainer) {
        suggestionsContainer.style.display = 'none';
    }

    const typingIndicator = document.getElementById('typing-indicator');

    // Add user message
    addMessage(text, 'user');
    userInput.value = '';
    userInput.disabled = true;
    sendBtn.disabled = true;

    // Show typing indicator
    if (typingIndicator) {
        typingIndicator.style.display = 'flex';
        scrollToBottom();
    }

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: text })
        });

        const data = await response.json();

        // Hide typing indicator
        if (typingIndicator) typingIndicator.style.display = 'none';

        if (response.ok) {
            addMessage(data.response, 'bot');
        } else {
            addMessage('Error: ' + data.detail, 'bot');
        }
    } catch (error) {
        if (typingIndicator) typingIndicator.style.display = 'none';
        addMessage('Error: Could not connect to server.', 'bot');
    } finally {
        userInput.disabled = false;
        sendBtn.disabled = false;
        userInput.focus();
        scrollToBottom();
    }
}

if (sendBtn) {
    sendBtn.addEventListener('click', sendMessage);
}

if (userInput) {
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
}

// Suggested Questions
const suggestedQuestions = document.querySelectorAll('.suggestion-chip');
suggestedQuestions.forEach(chip => {
    chip.addEventListener('click', () => {
        userInput.value = chip.textContent;
        sendMessage();
    });
});
