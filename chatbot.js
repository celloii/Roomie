/**
 * Chatbot Component
 * A clickable chatbot widget in the bottom right corner
 * Uses Claude API to help users navigate the site
 */

(function() {
    'use strict';

    // Create chatbot HTML structure
    const chatbotHTML = `
        <div id="chatbot-container" class="chatbot-container">
            <div id="chatbot-window" class="chatbot-window" style="display: none;">
                <div class="chatbot-header">
                    <div class="chatbot-title">
                        <span class="chatbot-icon">💬</span>
                        <span>Need Help?</span>
                    </div>
                    <button id="chatbot-close" class="chatbot-close" aria-label="Close chatbot">×</button>
                </div>
                <div id="chatbot-messages" class="chatbot-messages"></div>
                <div class="chatbot-input-container">
                    <input 
                        type="text" 
                        id="chatbot-input" 
                        class="chatbot-input" 
                        placeholder="Ask me anything about accommodations or events..."
                        autocomplete="off"
                    />
                    <button id="chatbot-send" class="chatbot-send" aria-label="Send message">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="22" y1="2" x2="11" y2="13"></line>
                            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                        </svg>
                    </button>
                </div>
            </div>
            <button id="chatbot-toggle" class="chatbot-toggle" aria-label="Open chatbot">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
            </button>
        </div>
    `;

    // Create chatbot CSS
    const chatbotCSS = `
        <style id="chatbot-styles">
            .chatbot-container {
                position: fixed;
                bottom: 20px;
                right: 20px;
                z-index: 10000;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            }

            .chatbot-toggle {
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: linear-gradient(135deg, #0077b6 0%, #03045e 100%);
                border: none;
                color: white;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(0, 119, 182, 0.4);
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s ease;
                position: relative;
            }

            .chatbot-toggle:hover {
                transform: scale(1.1);
                box-shadow: 0 6px 20px rgba(0, 119, 182, 0.5);
            }

            .chatbot-toggle:active {
                transform: scale(0.95);
            }

            .chatbot-window {
                position: absolute;
                bottom: 80px;
                right: 0;
                width: 380px;
                max-width: calc(100vw - 40px);
                height: 600px;
                max-height: calc(100vh - 100px);
                background: white;
                border-radius: 16px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
                display: flex;
                flex-direction: column;
                overflow: hidden;
                animation: slideUp 0.3s ease;
            }

            @keyframes slideUp {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            .chatbot-header {
                background: linear-gradient(135deg, #0077b6 0%, #03045e 100%);
                color: white;
                padding: 16px 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .chatbot-title {
                display: flex;
                align-items: center;
                gap: 10px;
                font-weight: 600;
                font-size: 16px;
            }

            .chatbot-icon {
                font-size: 20px;
            }

            .chatbot-close {
                background: transparent;
                border: none;
                color: white;
                font-size: 28px;
                cursor: pointer;
                width: 32px;
                height: 32px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                transition: background 0.2s;
                line-height: 1;
            }

            .chatbot-close:hover {
                background: rgba(255, 255, 255, 0.2);
            }

            .chatbot-messages {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                display: flex;
                flex-direction: column;
                gap: 12px;
                background: #f7f7f7;
            }

            .chatbot-message {
                max-width: 80%;
                padding: 12px 16px;
                border-radius: 12px;
                word-wrap: break-word;
                animation: fadeIn 0.3s ease;
            }

            @keyframes fadeIn {
                from {
                    opacity: 0;
                    transform: translateY(10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            .chatbot-message.user {
                align-self: flex-end;
                background: linear-gradient(135deg, #0077b6 0%, #03045e 100%);
                color: white;
                border-bottom-right-radius: 4px;
            }

            .chatbot-message.bot {
                align-self: flex-start;
                background: white;
                color: #333;
                border: 1px solid #e0e0e0;
                border-bottom-left-radius: 4px;
            }

            .chatbot-message.typing {
                align-self: flex-start;
                background: white;
                padding: 12px 16px;
            }

            .typing-indicator {
                display: flex;
                gap: 4px;
            }

            .typing-indicator span {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #999;
                animation: typing 1.4s infinite;
            }

            .typing-indicator span:nth-child(2) {
                animation-delay: 0.2s;
            }

            .typing-indicator span:nth-child(3) {
                animation-delay: 0.4s;
            }

            @keyframes typing {
                0%, 60%, 100% {
                    transform: translateY(0);
                    opacity: 0.7;
                }
                30% {
                    transform: translateY(-10px);
                    opacity: 1;
                }
            }

            .chatbot-input-container {
                display: flex;
                padding: 16px;
                background: white;
                border-top: 1px solid #e0e0e0;
                gap: 8px;
            }

            .chatbot-input {
                flex: 1;
                padding: 12px 16px;
                border: 1px solid #e0e0e0;
                border-radius: 24px;
                font-size: 14px;
                outline: none;
                transition: border-color 0.2s;
            }

            .chatbot-input:focus {
                border-color: #0077b6;
            }

            .chatbot-send {
                width: 44px;
                height: 44px;
                border-radius: 50%;
                background: linear-gradient(135deg, #0077b6 0%, #03045e 100%);
                border: none;
                color: white;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.2s;
                flex-shrink: 0;
            }

            .chatbot-send:hover {
                transform: scale(1.05);
            }

            .chatbot-send:active {
                transform: scale(0.95);
            }

            .chatbot-send:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }

            /* Scrollbar styling */
            .chatbot-messages::-webkit-scrollbar {
                width: 6px;
            }

            .chatbot-messages::-webkit-scrollbar-track {
                background: transparent;
            }

            .chatbot-messages::-webkit-scrollbar-thumb {
                background: #ccc;
                border-radius: 3px;
            }

            .chatbot-messages::-webkit-scrollbar-thumb:hover {
                background: #999;
            }

            /* Mobile responsiveness */
            @media (max-width: 480px) {
                .chatbot-window {
                    width: calc(100vw - 20px);
                    right: 10px;
                    bottom: 80px;
                    height: calc(100vh - 100px);
                }

                .chatbot-container {
                    bottom: 10px;
                    right: 10px;
                }
            }
        </style>
    `;

    // Chatbot class
    class Chatbot {
        constructor() {
            this.conversationHistory = [];
            this.isOpen = false;
            this.init();
        }

        init() {
            // Inject CSS
            if (!document.getElementById('chatbot-styles')) {
                document.head.insertAdjacentHTML('beforeend', chatbotCSS);
            }

            // Inject HTML
            document.body.insertAdjacentHTML('beforeend', chatbotHTML);

            // Get elements
            this.container = document.getElementById('chatbot-container');
            this.window = document.getElementById('chatbot-window');
            this.toggle = document.getElementById('chatbot-toggle');
            this.close = document.getElementById('chatbot-close');
            this.messages = document.getElementById('chatbot-messages');
            this.input = document.getElementById('chatbot-input');
            this.sendBtn = document.getElementById('chatbot-send');

            // Event listeners
            this.toggle.addEventListener('click', () => this.toggleChatbot());
            this.close.addEventListener('click', () => this.closeChatbot());
            this.sendBtn.addEventListener('click', () => this.sendMessage());
            this.input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });

            // Add welcome message
            this.addWelcomeMessage();
        }

        toggleChatbot() {
            if (this.isOpen) {
                this.closeChatbot();
            } else {
                this.openChatbot();
            }
        }

        openChatbot() {
            this.window.style.display = 'flex';
            this.isOpen = true;
            this.input.focus();
        }

        closeChatbot() {
            this.window.style.display = 'none';
            this.isOpen = false;
        }

        addWelcomeMessage() {
            const welcomeMsg = "Hi! I'm here to help you find the perfect accommodation and events. Ask me anything! 😊";
            this.addMessage('bot', welcomeMsg);
        }

        addMessage(role, content) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `chatbot-message ${role}`;
            messageDiv.textContent = content;
            this.messages.appendChild(messageDiv);
            this.messages.scrollTop = this.messages.scrollHeight;
        }

        addTypingIndicator() {
            const typingDiv = document.createElement('div');
            typingDiv.className = 'chatbot-message typing';
            typingDiv.id = 'typing-indicator';
            typingDiv.innerHTML = `
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            `;
            this.messages.appendChild(typingDiv);
            this.messages.scrollTop = this.messages.scrollHeight;
        }

        removeTypingIndicator() {
            const typing = document.getElementById('typing-indicator');
            if (typing) {
                typing.remove();
            }
        }

        async sendMessage() {
            const message = this.input.value.trim();
            if (!message) return;

            // Add user message to UI
            this.addMessage('user', message);
            this.input.value = '';

            // Disable input while processing
            this.input.disabled = true;
            this.sendBtn.disabled = true;

            // Add typing indicator
            this.addTypingIndicator();

            // Add to conversation history
            this.conversationHistory.push({
                role: 'user',
                content: message
            });

            try {
                // Call API
                const response = await fetch('/api/chatbot', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message: message,
                        conversation_history: this.conversationHistory
                    })
                });

                // Check if response is OK
                if (!response.ok) {
                    // Try to get error details from response
                    let errorData;
                    try {
                        errorData = await response.json();
                    } catch (e) {
                        errorData = { error: `HTTP ${response.status} error` };
                    }
                    const errorMsg = errorData.error || `HTTP error! status: ${response.status}`;
                    throw new Error(errorMsg);
                }

                const data = await response.json();

                // Remove typing indicator
                this.removeTypingIndicator();

                if (data.success && data.response) {
                    // Add bot response to UI
                    this.addMessage('bot', data.response);

                    // Add to conversation history
                    this.conversationHistory.push({
                        role: 'assistant',
                        content: data.response
                    });
                } else {
                    // Show error message with more details
                    let errorMsg = 'Sorry, I encountered an error. ';
                    if (data.error) {
                        console.error('Chatbot error:', data.error);
                        console.error('Full error data:', data);
                        
                        // Show user-friendly error message based on error type
                        if (data.error.includes('API key not found') || data.error.includes('not configured')) {
                            errorMsg = 'The chatbot service is not properly configured. Please contact support.';
                        } else if (data.error.includes('authentication') || data.error.includes('401') || data.error.includes('403')) {
                            errorMsg = 'Authentication error with Claude API. Please check your API key.';
                        } else if (data.error.includes('rate limit') || data.error.includes('429')) {
                            errorMsg = 'Too many requests. Please wait a moment and try again.';
                        } else if (data.error.includes('Invalid API key') || data.error.includes('authentication_error')) {
                            errorMsg = 'Invalid API key. Please check your Claude API key configuration.';
                        } else {
                            // Show the actual error message (truncated if too long)
                            const errorText = data.error.length > 200 ? data.error.substring(0, 200) + '...' : data.error;
                            errorMsg += errorText;
                        }
                    } else {
                        errorMsg += 'Please try again later.';
                    }
                    this.addMessage('bot', errorMsg);
                    if (data.details) {
                        console.error('Error details:', data.details);
                    }
                }
            } catch (error) {
                // Remove typing indicator
                this.removeTypingIndicator();

                // Show more specific error message
                let errorMsg = 'Sorry, I encountered an error. ';
                if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
                    errorMsg += 'Could not connect to the server. Please make sure the server is running.';
                } else if (error.message.includes('HTTP error')) {
                    errorMsg += `Server error: ${error.message}`;
                } else {
                    errorMsg += error.message || 'Please try again later.';
                }
                this.addMessage('bot', errorMsg);
                console.error('Chatbot error:', error);
            } finally {
                // Re-enable input
                this.input.disabled = false;
                this.sendBtn.disabled = false;
                this.input.focus();
            }
        }
    }

    // Initialize chatbot when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            new Chatbot();
        });
    } else {
        new Chatbot();
    }
})();

