document.addEventListener('DOMContentLoaded', () => {
    const messageInput = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');
    const chatBox = document.getElementById('chat-box');

    let conversationHistory = [];
    let isLoading = false;
    let requestCount = 0;
    let lastRequestTime = Date.now();

    // Security: Get app configuration
    async function loadConfig() {
        try {
            const response = await fetch('/api/config');
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Failed to load config:', error);
        }
        return {
            max_message_length: 2000,
            max_conversation_history: 20
        };
    }

    let CONFIG = {
        max_message_length: 2000,
        max_conversation_history: 20
    };

    loadConfig().then(config => {
        CONFIG = config;
        console.log('Config loaded:', CONFIG);
    });

    // Input validation and sanitization
    function validateInput(text) {
        if (!text || typeof text !== 'string') {
            return { valid: false, error: 'Invalid input' };
        }

        const trimmed = text.trim();

        if (trimmed.length === 0) {
            return { valid: false, error: 'Message cannot be empty' };
        }

        if (trimmed.length > CONFIG.max_message_length) {
            return { valid: false, error: `Message exceeds maximum length of ${CONFIG.max_message_length} characters` };
        }

        // Check for suspicious patterns
        const suspiciousPatterns = [
            /<script/gi,
            /javascript:/gi,
            /on\w+\s*=/gi,
            /<iframe/gi,
            /<embed/gi,
            /<object/gi
        ];

        for (const pattern of suspiciousPatterns) {
            if (pattern.test(trimmed)) {
                return { valid: false, error: 'Message contains invalid content' };
            }
        }

        return { valid: true, error: '' };
    }

    // Convert user input to safe HTML
    function escapeHtml(unsafe) {
        if (typeof unsafe !== 'string') return '';
        return unsafe
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    // Rate limiting on frontend
    function checkRateLimit() {
        const now = Date.now();
        const timeDiff = now - lastRequestTime;

        if (timeDiff < 1000) {
            requestCount++;
        } else {
            requestCount = 1;
            lastRequestTime = now;
        }

        if (requestCount > 10) {
            return { allowed: false, message: 'Too many requests. Please wait a moment.' };
        }

        return { allowed: true };
    }

    const sendMessage = async () => {
        // Check rate limit
        const rateCheck = checkRateLimit();
        if (!rateCheck.allowed) {
            alert(rateCheck.message);
            return;
        }

        const messageText = messageInput.value.trim();

        // Validate input
        const validation = validateInput(messageText);
        if (!validation.valid) {
            alert(validation.error);
            messageInput.focus();
            return;
        }

        if (isLoading) {
            alert('Please wait for the current response to complete');
            return;
        }

        // Check conversation history limit
        if (conversationHistory.length >= CONFIG.max_conversation_history) {
            alert('Conversation history limit reached. Please start a new conversation');
            return;
        }

        isLoading = true;
        sendBtn.disabled = true;
        messageInput.disabled = true;

        const userMessage = { sender: 'user', text: messageText };
        conversationHistory.push(userMessage);

        appendMessage('user', messageText);
        messageInput.value = '';

        const aiMessageElement = createAiMessageElement();

        try {
            // Security: Only send to same origin
            const origin = window.location.origin;
            const chatUrl = new URL('/chat', origin);

            const response = await fetch(chatUrl.toString(), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin',  // Only send cookies for same-origin
                body: JSON.stringify({ messages: conversationHistory })
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({ error: 'Unknown error' }));
                throw new Error(error.error || `HTTP ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let aiResponseText = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                aiResponseText += chunk;
                // Display safely - don't use innerHTML during streaming
                aiMessageElement.textContent = aiResponseText;
                chatBox.scrollTop = chatBox.scrollHeight;
            }

            // Ensure final text is sanitized
            aiResponseText = sanitizeResponse(aiResponseText);

            const aiMessage = { sender: 'ai', text: aiResponseText };
            conversationHistory.push(aiMessage);

            // Process the complete message for code highlighting
            processMessageContent(aiMessageElement, aiResponseText);

        } catch (error) {
            console.error('Error:', error);
            const errorMsg = error.message || 'Something went wrong. Please try again.';
            aiMessageElement.innerHTML = `<p style="color: #ff6b6b;"><strong>⚠️ Error:</strong> ${escapeHtml(errorMsg)}</p>`;
        } finally {
            isLoading = false;
            sendBtn.disabled = false;
            messageInput.disabled = false;
            messageInput.focus();
        }
    };

    // Sanitize API response
    function sanitizeResponse(text) {
        if (typeof text !== 'string') return '';
        // Remove control characters except newlines and tabs
        return text.replace(/[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]/g, '');
    }

    const processMessageContent = (element, text) => {
        element.innerHTML = ''; // Clear

        // Code block regex - be strict about format
        const codeBlockRegex = /^```(\w*)[\r\n]([\s\S]*?)```$/gm;
        let lastIndex = 0;
        let match;

        while ((match = codeBlockRegex.exec(text)) !== null) {
            // Add text before the code block
            if (match.index > lastIndex) {
                const pre_text = document.createElement('p');
                // Use textContent to prevent XSS
                pre_text.textContent = text.substring(lastIndex, match.index);
                element.appendChild(pre_text);
            }

            // Create and append the code block safely
            const language = (match[1] || 'plaintext').replace(/[^a-z0-9\-]/gi, '');
            const code = match[2];
            const pre = document.createElement('pre');
            const codeEl = document.createElement('code');

            // Use textContent instead of innerHTML
            codeEl.textContent = code;

            // Add language class only if it's a known language
            const knownLanguages = ['javascript', 'python', 'java', 'cpp', 'csharp', 'html', 'css', 'sql', 'bash', 'shell', 'plaintext'];
            if (knownLanguages.includes(language.toLowerCase())) {
                codeEl.classList.add(`language-${language}`);
            } else {
                codeEl.classList.add('language-plaintext');
            }

            pre.appendChild(codeEl);
            element.appendChild(pre);

            // Only highlight if hljs is available
            if (typeof hljs !== 'undefined' && hljs.highlightElement) {
                try {
                    hljs.highlightElement(codeEl);
                } catch (e) {
                    console.error('Syntax highlighting error:', e);
                }
            }

            lastIndex = match.index + match[0].length;
        }

        // Add any remaining text after the last code block
        if (lastIndex < text.length) {
            const post_text = document.createElement('p');
            post_text.textContent = text.substring(lastIndex);
            element.appendChild(post_text);
        }

        addCopyButtons();
    };

    const appendMessage = (sender, message) => {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);

        const messageContent = document.createElement('div');
        messageContent.classList.add('message-content');

        if (sender === 'user') {
            // Use textContent for user messages to prevent XSS
            messageContent.textContent = message;
        }

        messageElement.appendChild(messageContent);
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;

        return messageContent;
    };

    const createAiMessageElement = () => {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', 'ai-message');

        const messageContent = document.createElement('div');
        messageContent.classList.add('message-content');
        messageContent.textContent = 'Thinking...';

        messageElement.appendChild(messageContent);
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;

        return messageContent;
    };

    const addCopyButtons = () => {
        const codeBlocks = document.querySelectorAll('pre');
        codeBlocks.forEach(block => {
            if (block.querySelector('.copy-btn')) return;

            const copyBtn = document.createElement('button');
            copyBtn.classList.add('copy-btn');
            copyBtn.innerHTML = '<i class="far fa-copy"></i> Copy';
            copyBtn.setAttribute('type', 'button');
            copyBtn.setAttribute('aria-label', 'Copy code to clipboard');

            copyBtn.addEventListener('click', (e) => {
                e.preventDefault();
                const codeElement = block.querySelector('code');
                if (!codeElement) return;

                const codeToCopy = codeElement.textContent;

                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(codeToCopy).then(() => {
                        copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
                        setTimeout(() => {
                            copyBtn.innerHTML = '<i class="far fa-copy"></i> Copy';
                        }, 2000);
                    }).catch(err => {
                        console.error('Failed to copy:', err);
                        copyBtn.innerHTML = '<i class="fas fa-times"></i> Failed';
                    });
                } else {
                    // Fallback for older browsers
                    const textarea = document.createElement('textarea');
                    textarea.value = codeToCopy;
                    document.body.appendChild(textarea);
                    textarea.select();
                    try {
                        document.execCommand('copy');
                        copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
                        setTimeout(() => {
                            copyBtn.innerHTML = '<i class="far fa-copy"></i> Copy';
                        }, 2000);
                    } catch (err) {
                        console.error('Fallback copy failed:', err);
                    } finally {
                        document.body.removeChild(textarea);
                    }
                }
            });

            block.appendChild(copyBtn);
        });
    };

    // Event listeners with security considerations
    sendBtn.addEventListener('click', (e) => {
        e.preventDefault();
        sendMessage();
    });

    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !isLoading && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Prevent accidental data loss
    window.addEventListener('beforeunload', (e) => {
        if (conversationHistory.length > 0 && !isLoading) {
            e.preventDefault();
            e.returnValue = '';
        }
    });

    // Focus on input on load
    messageInput.focus();

    console.log('Chat application initialized securely');
});
