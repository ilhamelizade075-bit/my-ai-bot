<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Zaza AI Helper</title>
    <link rel="manifest" href="/static/manifest.json">
    <meta name="theme-color" content="#202123">
    <script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        html, body { height: 100%; width: 100%; overflow: hidden; background: #343541; color: #ececf1; }
        body { display: flex; flex-direction: row; }

        /* Sidebar Styles */
        #sidebar { width: 260px; background: #202123; display: flex; flex-direction: column; padding: 10px; border-right: 1px solid #4d4d4f; z-index: 10; transition: transform 0.3s ease; }
        .new-chat-btn { background: transparent; border: 1px solid #565869; color: #fff; padding: 10px; border-radius: 6px; cursor: pointer; text-align: left; display: flex; align-items: center; gap: 10px; font-size: 14px; margin-bottom: 10px; }
        .new-chat-btn:hover { background: #2a2b32; }
        #history-list { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 6px; }

        .history-item { padding: 10px; border-radius: 6px; cursor: pointer; font-size: 13px; color: #c5c5d2; display: flex; align-items: center; justify-content: space-between; gap: 8px; }
        .history-item:hover, .history-item.active { background: #343541; color: #fff; }
        .history-title { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex: 1; }
        .delete-btn { background: transparent; border: none; color: #8e8ea0; cursor: pointer; font-size: 14px; padding: 2px 4px; border-radius: 4px; display: none; }
        .history-item:hover .delete-btn { display: block; }
        .delete-btn:hover { color: #ef4444; }

        /* Main Area */
        #main-content { flex: 1; display: flex; flex-direction: column; height: 100dvh; width: 100%; position: relative; }
        header { background: #343541; padding: 10px 14px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #4d4d4f; height: 50px; }
        .header-left { display: flex; align-items: center; gap: 10px; }
        .header-title { font-size: 15px; font-weight: 600; }
        .menu-toggle { display: none; background: none; border: none; color: #fff; font-size: 18px; cursor: pointer; }

        /* Search Input */
        .search-box { position: relative; display: flex; align-items: center; }
        .search-box input { background: #40414f; border: 1px solid #565869; color: #fff; border-radius: 6px; padding: 5px 8px 5px 24px; font-size: 12px; outline: none; width: 130px; }
        .search-box input:focus { border-color: #10a37f; }
        .search-box input::placeholder { color: #8e8ea0; }
        .search-icon { position: absolute; left: 6px; font-size: 10px; color: #8e8ea0; pointer-events: none; }

        #chat-container { flex: 1; overflow-y: auto; padding: 12px; display: flex; flex-direction: column; gap: 12px; }
        .message { display: flex; gap: 10px; max-width: 800px; margin: 0 auto; width: 100%; padding: 10px; border-radius: 8px; }
        .message.user { background: #343541; }
        .message.bot { background: #444654; }
        .avatar { width: 28px; height: 28px; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px; flex-shrink: 0; }
        .user .avatar { background: #5436da; }
        .bot .avatar { background: #10a37f; }
        .content { font-size: 14px; line-height: 1.5; word-break: break-word; flex: 1; }

        /* Typing Dots Animation */
        .typing-dots { display: flex; align-items: center; gap: 4px; height: 20px; }
        .typing-dots span { width: 6px; height: 6px; background-color: #acacbe; border-radius: 50%; display: inline-block; animation: bounce 1.4s infinite ease-in-out both; }
        .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
        .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1.0); }
        }

        /* Footer / Message Box */
        footer { background: #343541; padding: 8px 12px; border-top: 1px solid #4d4d4f; }
        .input-box { max-width: 800px; margin: 0 auto; display: flex; flex-direction: column; gap: 6px; }
        .controls { display: flex; gap: 8px; align-items: center; background: #40414f; border-radius: 8px; padding: 6px 10px; }
        textarea { flex: 1; background: transparent; border: none; color: #fff; font-size: 14px; resize: none; outline: none; height: 24px; max-height: 100px; }
        .input-btn { background: transparent; border: none; color: #acacbe; cursor: pointer; padding: 4px; border-radius: 4px; font-size: 16px; flex-shrink: 0; }
        .input-btn:hover { color: #fff; }

        .media-preview-container { display: flex; align-items: center; gap: 8px; background: #202123; padding: 4px 8px; border-radius: 6px; font-size: 11px; }

        /* Overlay for Mobile Sidebar */
        #overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 5; }

        /* Mobile Adaptation Styles */
        @media (max-width: 768px) {
            #sidebar { position: fixed; top: 0; bottom: 0; left: 0; transform: translateX(-100%); }
            #sidebar.open { transform: translateX(0); }
            #overlay.show { display: block; }
            .menu-toggle { display: block; }
            .search-box input { width: 100px; }
        }
    </style>
</head>
<body>

    <div id="overlay" onclick="toggleSidebar()"></div>

    <!-- Left Sidebar -->
    <div id="sidebar">
        <button class="new-chat-btn" onclick="startNewChat()">➕ New Chat</button>
        <div id="history-list"></div>
    </div>

    <!-- Main Content Area -->
    <div id="main-content">
        <header>
            <div class="header-left">
                <button class="menu-toggle" onclick="toggleSidebar()">☰</button>
                <div class="header-title">🤖 Zaza AI Helper</div>
            </div>
            <div class="search-box">
                <span class="search-icon">🔍</span>
                <input type="text" id="search-chats-input" placeholder="Search..." oninput="filterChats(this.value)">
            </div>
        </header>

        <div id="chat-container"></div>

        <footer>
            <div class="input-box">
                <div id="media-preview" class="media-preview-container" style="display:none;">
                    <span id="preview-text"></span>
                    <button onclick="clearMedia()" style="background:none; border:none; color:#ef4444; cursor:pointer; margin-left:auto;">❌</button>
                </div>
                <div class="controls">
                    <label for="file-input" class="input-btn" title="Attach File">📎</label>
                    <input type="file" id="file-input" style="display:none;" onchange="handleFileSelect(event)">
                    
                    <textarea id="user-input" placeholder="Message Zaza..." rows="1" onkeydown="handleKeyDown(event)"></textarea>
                    
                    <button class="input-btn" onclick="sendMessage()" title="Send">➔</button>
                </div>
            </div>
        </footer>
    </div>

    <script>
        let chats = JSON.parse(localStorage.getItem('zaza_chats') || '[]');
        let currentChatId = null;
        let selectedFileBase64 = null;
        let selectedFileType = null;

        function init() {
            renderHistory();
            if (chats.length > 0) {
                loadChat(chats[0].id);
            } else {
                startNewChat();
            }
        }

        function toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('open');
            document.getElementById('overlay').classList.toggle('show');
        }

        function saveChats() {
            localStorage.setItem('zaza_chats', JSON.stringify(chats));
            renderHistory();
        }

        function startNewChat() {
            currentChatId = Date.now().toString();
            chats.unshift({ id: currentChatId, title: "New Chat", messages: [] });
            saveChats();
            loadChat(currentChatId);
            if(window.innerWidth <= 768) toggleSidebar();
        }

        function loadChat(id) {
            currentChatId = id;
            const chat = chats.find(c => c.id === id);
            const container = document.getElementById('chat-container');
            container.innerHTML = '';
            
            if (chat) {
                chat.messages.forEach(m => appendMessageToDOM(m.sender, m.text));
            }
            renderHistory();
        }

        function deleteChat(event, id) {
            event.stopPropagation();
            chats = chats.filter(c => c.id !== id);
            saveChats();

            if (currentChatId === id) {
                if (chats.length > 0) {
                    loadChat(chats[0].id);
                } else {
                    startNewChat();
                }
            }
        }

        function renderHistory(filteredChats = null) {
            const list = document.getElementById('history-list');
            list.innerHTML = '';
            const listToRender = filteredChats !== null ? filteredChats : chats;

            listToRender.forEach(c => {
                const item = document.createElement('div');
                item.className = `history-item ${c.id === currentChatId ? 'active' : ''}`;
                item.onclick = () => {
                    loadChat(c.id);
                    if(window.innerWidth <= 768) toggleSidebar();
                };

                const title = document.createElement('span');
                title.className = 'history-title';
                title.innerText = c.title || "New Chat";

                const delBtn = document.createElement('button');
                delBtn.className = 'delete-btn';
                delBtn.innerHTML = '🗑️';
                delBtn.title = 'Delete Chat';
                delBtn.onclick = (e) => deleteChat(e, c.id);

                item.appendChild(title);
                item.appendChild(delBtn);
                list.appendChild(item);
            });
        }

        function filterChats(query) {
            const searchQuery = query.toLowerCase().trim();
            if (!searchQuery) {
                renderHistory();
                return;
            }
            const filtered = chats.filter(c => 
                (c.title && c.title.toLowerCase().includes(searchQuery)) ||
                c.messages.some(m => m.text && m.text.toLowerCase().includes(searchQuery))
            );
            renderHistory(filtered);
        }

        function appendMessageToDOM(sender, text) {
            const container = document.getElementById('chat-container');
            const msgDiv = document.createElement('div');
            msgDiv.className = `message ${sender}`;
            
            const avatar = document.createElement('div');
            avatar.className = 'avatar';
            avatar.innerText = sender === 'user' ? 'You' : 'Zaza';

            const content = document.createElement('div');
            content.className = 'content';
            content.innerText = text;

            msgDiv.appendChild(avatar);
            msgDiv.appendChild(content);
            container.appendChild(msgDiv);
            container.scrollTop = container.scrollHeight;
            return content;
        }

        function createTypingIndicator() {
            const container = document.getElementById('chat-container');
            const msgDiv = document.createElement('div');
            msgDiv.className = 'message bot';
            msgDiv.id = 'typing-indicator-msg';
            
            const avatar = document.createElement('div');
            avatar.className = 'avatar';
            avatar.innerText = 'Zaza';

            const content = document.createElement('div');
            content.className = 'content';
            content.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';

            msgDiv.appendChild(avatar);
            msgDiv.appendChild(content);
            container.appendChild(msgDiv);
            container.scrollTop = container.scrollHeight;
            return msgDiv;
        }

        async function sendMessage() {
            const input = document.getElementById('user-input');
            const text = input.value.trim();
            if (!text && !selectedFileBase64) return;

            appendMessageToDOM('user', text || "[File Sent]");
            
            const currentChat = chats.find(c => c.id === currentChatId);
            if (currentChat) {
                if (currentChat.messages.length === 0 && text) {
                    currentChat.title = text.substring(0, 20) + "...";
                }
                currentChat.messages.push({ sender: 'user', text: text || "[File Sent]" });
            }

            input.value = '';
            const payload = { message: text, file_data: selectedFileBase64, file_type: selectedFileType };
            clearMedia();

            const typingMsgElement = createTypingIndicator();

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                
                typingMsgElement.remove();
                appendMessageToDOM('bot', data.response);

                if (currentChat) {
                    currentChat.messages.push({ sender: 'bot', text: data.response });
                    saveChats();
                }
            } catch (err) {
                typingMsgElement.remove();
                appendMessageToDOM('bot', "An error occurred, please try again.");
            }
        }

        function handleKeyDown(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        }

        function handleFileSelect(e) {
            const file = e.target.files[0];
            if (!file) return;
            selectedFileType = file.type;
            const reader = new FileReader();
            reader.onload = function(evt) {
                selectedFileBase64 = evt.target.result;
                document.getElementById('preview-text').innerText = `File: ${file.name}`;
                document.getElementById('media-preview').style.display = 'flex';
            };
            reader.readAsDataURL(file);
        }

        function clearMedia() {
            selectedFileBase64 = null;
            selectedFileType = null;
            document.getElementById('file-input').value = '';
            document.getElementById('media-preview').style.display = 'none';
        }

        init();
    </script>
</body>
</html>
