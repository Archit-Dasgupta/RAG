const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const fileList = document.getElementById('file-list');
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

// File Upload Handling
dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = 'var(--accent-color)';
});

dropZone.addEventListener('dragleave', () => {
    dropZone.style.borderColor = 'var(--border-color)';
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = 'var(--border-color)';
    handleFiles(e.dataTransfer.files);
});

fileInput.addEventListener('change', (e) => {
    handleFiles(e.target.files);
});

async function handleFiles(files) {
    const formData = new FormData();
    let count = 0;
    for (const file of files) {
        if (file.type === 'text/plain' || file.name.endsWith('.md') || file.name.endsWith('.txt') || file.name.toLowerCase().endsWith('.pdf')) {
            formData.append('files', file);
            addFileToList(file.name, 'uploading');
            count++;
        }
    }

    if (count === 0) return;

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        if (response.ok) {
            updateFileStatus('uploaded');
        } else {
            updateFileStatus('error');
            alert('Upload failed: ' + result.detail);
        }
    } catch (error) {
        console.error('Error:', error);
        updateFileStatus('error');
    }
}

function addFileToList(name, status) {
    const div = document.createElement('div');
    div.className = 'file-item';
    div.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
        <span style="flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${name}</span>
        <span class="status-text" style="font-size:0.8em; color:var(--text-secondary)">${status}</span>
    `;
    fileList.prepend(div);
}

function updateFileStatus(status) {
    const items = fileList.querySelectorAll('.status-text');
    items.forEach(item => {
        if (item.textContent === 'uploading') {
            item.textContent = status;
            item.style.color = status === 'uploaded' ? '#4ade80' : '#f87171';
        }
    });
}

// Chat Handling
function addMessage(text, sender) {
    const div = document.createElement('div');
    div.className = `message ${sender}`;
    div.textContent = text;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    const typingIndicator = document.getElementById('typing-indicator');

    addMessage(text, 'user');
    userInput.value = '';
    userInput.disabled = true;
    sendBtn.disabled = true;

    // Show typing indicator
    typingIndicator.style.display = 'block';
    chatMessages.scrollTop = chatMessages.scrollHeight;

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
        typingIndicator.style.display = 'none';

        if (response.ok) {
            addMessage(data.response, 'bot');
        } else {
            addMessage('Error: ' + data.detail, 'bot');
        }
    } catch (error) {
        typingIndicator.style.display = 'none';
        addMessage('Error: Could not connect to server.', 'bot');
    } finally {
        userInput.disabled = false;
        sendBtn.disabled = false;
        userInput.focus();
    }
}

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

// Mobile Menu Toggle
const mobileMenuBtn = document.getElementById('mobile-menu-btn');
const sidebar = document.querySelector('.sidebar');

if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener('click', () => {
        sidebar.classList.toggle('active');
    });
}

// Close sidebar when clicking outside on mobile
document.addEventListener('click', (e) => {
    if (window.innerWidth <= 768) {
        if (sidebar.classList.contains('active') &&
            !sidebar.contains(e.target) &&
            !mobileMenuBtn.contains(e.target)) {
            sidebar.classList.remove('active');
        }
    }
});

// Suggested Questions
const suggestedQuestions = document.querySelectorAll('.suggestion-chip');
suggestedQuestions.forEach(chip => {
    chip.addEventListener('click', () => {
        userInput.value = chip.textContent;
        sendMessage();
    });
});

function scrollToBottom() {
    requestAnimationFrame(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    });
}

// Update addMessage to use new scroll
const originalAddMessage = addMessage;
addMessage = function (text, sender) {
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
};

// Update sendMessage to use new scroll and hide suggestions
const originalSendMessage = sendMessage;
sendMessage = async function () {
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

    // Show typing indicator at the bottom
    typingIndicator.style.display = 'flex'; // Changed to flex for alignment
    scrollToBottom();

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
        typingIndicator.style.display = 'none';

        if (response.ok) {
            addMessage(data.response, 'bot');
        } else {
            addMessage('Error: ' + data.detail, 'bot');
        }
    } catch (error) {
        typingIndicator.style.display = 'none';
        addMessage('Error: Could not connect to server.', 'bot');
    } finally {
        userInput.disabled = false;
        sendBtn.disabled = false;
        userInput.focus();
        scrollToBottom();
    }
};
