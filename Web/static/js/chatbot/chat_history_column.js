// KB국민은행 직원 업무시스템 - Chat History Column Component

class ChatHistoryColumn {
    constructor() {
        this.currentChatId = null;
        this.chatHistory = []; // 빈 배열로 시작
        
        this.init();
    }
    
    init() {
        console.log('Chat History Column - Initializing');
        this.hasInitialized = false;  // 초기화 플래그 설정
        this.setupEventListeners();
        this.setupKeyboardShortcuts();
        this.loadChatHistories();
    }
    
    setupEventListeners() {
        const newChatSection = document.querySelector('.new_chat_section');
        const chatSearchSection = document.querySelector('.chat_search_section');
        const historyItems = document.querySelectorAll('.history_item');
        const functionIcons = document.querySelectorAll('.function_icon');
        const storageSection = document.querySelector('.chat_storage_section');
        const settingSection = document.querySelector('.chat_setting_section');
        
        console.log('Chat History Column - Setting up event listeners');
        console.log('New Chat Section found:', newChatSection);
        console.log('Chat Search Section found:', chatSearchSection);
        console.log('History Items found:', historyItems.length);
        
        // 메뉴 외부 클릭 시 메뉴 닫기
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.function_icon')) {
                this.closeAllMenus();
            }
        });
        
        // 새 채팅 섹션 클릭
        if (newChatSection) {
            newChatSection.addEventListener('click', (e) => {
                console.log('New chat section clicked');
                e.stopPropagation();
                this.createNewChat();
            });
        }
        
        // 채팅 검색 섹션 클릭
        if (chatSearchSection) {
            chatSearchSection.addEventListener('click', (e) => {
                console.log('Chat search section clicked');
                e.stopPropagation();
                this.openSearch();
            });
        }
        
        // 히스토리 아이템 클릭
        historyItems.forEach((item, index) => {
            item.addEventListener('click', (e) => {
                // function_icon 클릭이 아닌 경우에만 채팅 선택
                if (!e.target.closest('.function_icon')) {
                    console.log('History item clicked:', index);
                    e.stopPropagation();
                    this.selectChat(index);
                }
            });
        });
        
        // Function Icon 클릭 (세로 점 3개)
        functionIcons.forEach((icon, index) => {
            icon.addEventListener('click', (e) => {
                console.log('Function icon clicked:', index);
                e.stopPropagation();
                this.showContextMenu(e, index);
            });
        });
        
        // 저장소 섹션 클릭
        if (storageSection) {
            storageSection.addEventListener('click', (e) => {
                console.log('Storage section clicked');
                e.stopPropagation();
                this.openStorage();
            });
        }
        
        // 설정 섹션 클릭
        if (settingSection) {
            settingSection.addEventListener('click', (e) => {
                console.log('Setting section clicked');
                e.stopPropagation();
                this.openSettings();
            });
        }
    }
    
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl + Shift + N: 새 채팅
            if (e.ctrlKey && e.shiftKey && e.key === 'N') {
                e.preventDefault();
                console.log('Keyboard shortcut: New chat');
                this.createNewChat();
            }
            
            // Ctrl + K: 채팅 검색
            if (e.ctrlKey && e.key === 'k') {
                e.preventDefault();
                console.log('Keyboard shortcut: Chat search');
                this.openSearch();
            }
        });
    }
    
    // CSRF 토큰 가져오기
    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
    
    async createNewChat() {
        console.log('Creating new chat');
        
        // 이미 빈 새 채팅이 있는지 확인 (제목이 "새 채팅"이고 메시지가 없는 것)
        const existingEmptyChat = this.chatHistory.find(chat => 
            chat.title === "새 채팅"
        );
        
        if (existingEmptyChat) {
            // 해당 채팅에 실제로 메시지가 있는지 확인
            try {
                const messages = await this.loadChatMessages(existingEmptyChat.id);
                if (messages.length === 0) {
                    console.log('Empty new chat already exists, using existing one:', existingEmptyChat.id);
                    
                    // 현재 채팅 ID 설정
                    this.currentChatId = existingEmptyChat.id;
                    
                    // 히스토리 목록 렌더링
                    this.renderHistoryList();
                    
                    // 기존 빈 채팅을 선택하고 새 채팅으로 시작
                    const existingChatIndex = this.chatHistory.findIndex(chat => chat.id === existingEmptyChat.id);
                    this.selectChat(existingChatIndex);
                    this.notifyMainChatbot('new_chat', existingEmptyChat);
                    
                    return existingEmptyChat.id;
                } else {
                    console.log('Existing "새 채팅" has messages, will create new one');
                }
            } catch (error) {
                console.log('Error checking existing chat messages, will create new one:', error);
            }
        }
        
        try {
            // 서버에 새 채팅 히스토리 생성 요청
            const response = await fetch('/kb_bank/chatbot/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    message: '',  // 빈 메시지로 새 채팅 생성
                    chat_id: null
                })
            });
            
            const data = await response.json();
            
            if (data.success && data.chat_history_id) {
                const newChatId = data.chat_history_id;
                const newChat = {
                    id: newChatId,
                    title: "새 채팅",
                    time: "방금 전",
                    timestamp: Date.now(),
                    isNew: true  // 새 채팅임을 표시
                };
                
                // 히스토리 맨 위에 추가
                this.chatHistory.unshift(newChat);
                
                // 현재 채팅 ID 설정
                this.currentChatId = newChatId;
                
                // UI 업데이트
                this.renderHistoryList();
                this.selectChat(0);
                
                // 메인 챗봇의 currentChatId도 업데이트
                if (window.currentChatId !== undefined) {
                    window.currentChatId = newChatId;
                    console.log('Updated main chatbot currentChatId to:', newChatId);
                }
                
                // 메인 챗봇에 새 채팅 생성 알림
                this.notifyMainChatbot('new_chat', newChat);
                
                console.log('New chat created with final ID:', newChatId);
                return newChatId;
            } else {
                console.error('Failed to create new chat:', data.message || 'Unknown error');
                return null;
            }
        } catch (error) {
            console.error('Error creating new chat:', error);
            return null;
        }
    }
    
    async selectChat(indexOrId) {
        console.log('Selecting chat:', indexOrId);
        
        // 히스토리가 비어있으면 선택할 수 없음
        if (this.chatHistory.length === 0) {
            console.log('No chat history available');
            return;
        }
        
        // indexOrId가 ID인지 인덱스인지 확인
        let index;
        if (typeof indexOrId === 'number' && indexOrId < this.chatHistory.length) {
            // 인덱스인 경우
            index = indexOrId;
        } else {
            // ID인 경우, 해당 ID를 가진 채팅의 인덱스 찾기
            index = this.chatHistory.findIndex(chat => 
                chat.id === indexOrId || 
                chat.id === parseInt(indexOrId) || 
                chat.id === String(indexOrId)
            );
            if (index === -1) {
                console.error('Chat not found with ID:', indexOrId);
                return;
            }
        }
        
        // 모든 히스토리 아이템에서 active 클래스 제거
        const historyItems = document.querySelectorAll('.history_item');
        historyItems.forEach(item => {
            item.classList.remove('active');
        });
        
        // 선택된 아이템에 active 클래스 추가
        if (historyItems[index] && this.chatHistory[index]) {
            historyItems[index].classList.add('active');
            this.currentChatId = this.chatHistory[index].id;
            
            const selectedChat = this.chatHistory[index];
            console.log('Selected chat:', selectedChat);
            
            // 새 채팅이 아닌 경우 메시지 로드
            if (!selectedChat.isNew) {
                try {
                    const messages = await this.loadChatMessages(selectedChat.id);
                    console.log('Loaded messages for chat:', selectedChat.id, messages);
                    
                    // 메인 챗봇에 선택된 채팅과 메시지 전달
                    this.notifyMainChatbot('load_chat', {
                        chat: selectedChat,
                        messages: messages
                    });
                } catch (error) {
                    console.error('Error loading chat messages:', error);
                    // 에러 발생 시에도 채팅 선택은 진행
                    this.notifyMainChatbot('load_chat', selectedChat);
                }
            } else {
                // 새 채팅인 경우 메시지 없이 전달
                this.notifyMainChatbot('load_chat', selectedChat);
            }
        }
    }
    
    showContextMenu(event, index) {
        console.log('Showing context menu for item:', index);
        
        // 다른 메뉴들 닫기
        this.closeAllMenus();
        
        // 현재 메뉴 표시
        const functionIcon = event.currentTarget;
        const contextMenu = functionIcon.querySelector('.context_menu');
        
        if (contextMenu) {
            contextMenu.classList.add('show');
            
            // 메뉴 아이템 클릭 이벤트 추가
            const menuItems = contextMenu.querySelectorAll('.menu_item');
            menuItems.forEach(item => {
                item.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const action = item.getAttribute('data-action');
                    this.handleMenuAction(action, index);
                    this.closeAllMenus();
                });
            });
        }
    }
    
    closeAllMenus() {
        const allMenus = document.querySelectorAll('.context_menu');
        allMenus.forEach(menu => {
            menu.classList.remove('show');
        });
    }
    
    handleMenuAction(action, index) {
        console.log('Menu action:', action, 'for item:', index);
        
        switch (action) {
            case 'save':
                this.saveChat(index);
                break;
            case 'delete':
                this.deleteChat(index);
                break;
            default:
                console.log('Unknown action:', action);
        }
    }
    
    saveChat(index) {
        const chat = this.chatHistory[index];
        if (chat) {
            console.log('Saving chat:', chat.title);
            // 실제 저장 로직 구현
            alert(`"${chat.title}" 채팅이 저장되었습니다.`);
        }
    }
    
    renameChat(index) {
        const newName = prompt('새 이름을 입력하세요:', this.chatHistory[index].title);
        if (newName && newName.trim()) {
            this.chatHistory[index].title = newName.trim();
            this.renderHistoryList();
        }
    }
    
    async deleteChat(index) {
        const chat = this.chatHistory[index];
        if (!chat) return;
        
        // 모든 채팅은 데이터베이스에 저장된 채팅이므로 서버에 완전 삭제 요청
        if (confirm('이 채팅을 완전히 삭제하시겠습니까? 삭제된 채팅은 복구할 수 없습니다.')) {
            try {
                const response = await fetch(`/kb_bank/chatbot/api/chat/histories/${chat.id}/delete/`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    console.log('Chat deleted successfully:', chat.id);
                    
                    // 히스토리 새로고침
                    await this.refreshChatHistories();
                    
                    // 삭제된 채팅이 현재 선택된 채팅인 경우 처리
                    if (this.currentChatId === chat.id || this.currentChatId === String(chat.id)) {
                        // 현재 채팅 ID 초기화
                        this.currentChatId = null;
                        window.currentChatId = null;
                        
                        // 히스토리가 비어있으면 빈 상태 표시, 아니면 첫 번째 채팅 선택
                        if (this.chatHistory.length === 0) {
                            this.showEmptyState();
                        } else {
                            // 첫 번째 채팅을 자동으로 선택
                            this.selectChat(0);
                        }
                    }
                } else {
                    alert('채팅 삭제에 실패했습니다: ' + data.message);
                    console.error('Delete failed:', data.message);
                }
            } catch (error) {
                console.error('Error deleting chat:', error);
                alert('채팅 삭제 중 오류가 발생했습니다.');
            }
        }
    }
    
    exportChat(index) {
        console.log('Exporting chat:', index);
        // 채팅 내보내기 기능 구현
    }
    
    openSearch() {
        console.log('Opening chat search');
        // 채팅 검색 모달 또는 기능 구현
    }
    
    openStorage() {
        console.log('Opening chat storage');
        // 채팅 저장소 페이지로 이동
    }
    
    openSettings() {
        console.log('Opening chat settings');
        // 채팅 설정 페이지로 이동
    }
    
    renderHistoryList() {
        const historyList = document.querySelector('.chat_history_list');
        if (!historyList) return;
        
        // 기존 히스토리 아이템 제거
        historyList.innerHTML = '';
        
        // 히스토리가 비어있으면 빈 상태 메시지 표시
        if (this.chatHistory.length === 0) {
            historyList.innerHTML = `
                <div class="empty_history">
                    <div class="empty_message">
                        <i class="bi bi-chat-dots"></i>
                        <p>아직 대화 기록이 없습니다.</p>
                        <p>새 채팅을 시작해보세요!</p>
                    </div>
                </div>
            `;
            return;
        }
        
        // 새로운 히스토리 아이템 생성
        this.chatHistory.forEach((chat, index) => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history_item';
            // 현재 선택된 채팅에 active 클래스 추가
            if (chat.id === this.currentChatId) {
                historyItem.classList.add('active');
            }
            
            historyItem.innerHTML = `
                <div class="history_content">
                    <div class="history_title">${chat.title}</div>
                    <div class="history_time">${chat.time}</div>
                </div>
                <div class="function_icon">
                    <i class="bi bi-three-dots-vertical"></i>
                    <div class="context_menu">
                        <div class="menu_item" data-action="save">
                            <i class="bi bi-bookmark"></i>
                            <span>저장</span>
                        </div>
                        <div class="menu_item" data-action="delete">
                            <i class="bi bi-trash"></i>
                            <span>삭제</span>
                        </div>
                    </div>
                </div>
            `;
            
            // 클릭 이벤트 추가
            historyItem.addEventListener('click', (e) => {
                if (!e.target.closest('.function_icon')) {
                    e.stopPropagation();
                    this.selectChat(index);
                }
            });
            
            // Function icon 클릭 이벤트 추가
            const functionIcon = historyItem.querySelector('.function_icon');
            functionIcon.addEventListener('click', (e) => {
                e.stopPropagation();
                this.showContextMenu(e, index);
            });
            
            historyList.appendChild(historyItem);
        });
    }
    
    notifyMainChatbot(action, data) {
        console.log('Notifying main chatbot:', action, data);
        
        // 커스텀 이벤트 발생
        const event = new CustomEvent('chatHistoryAction', {
            detail: { action, data }
        });
        document.dispatchEvent(event);
    }
    
    // 데이터베이스에서 채팅 히스토리 로드
    async loadChatHistories() {
        try {
            const response = await fetch('/kb_bank/chatbot/api/chat/histories/');
            const data = await response.json();
            
            if (data.success) {
                this.chatHistory = data.histories.map(history => ({
                    id: history.id,
                    title: history.title,
                    time: this.formatTime(history.last_message_time),
                    timestamp: new Date(history.last_message_time).getTime(),
                    isNew: false  // 데이터베이스에서 로드된 채팅
                }));
                
                console.log('Loaded chat histories:', this.chatHistory);
                console.log('Chat history length:', this.chatHistory.length);
                console.log('Has initialized:', this.hasInitialized);
                
                // 초기 로드 시에만 처리
                if (!this.hasInitialized) {
                    if (this.chatHistory.length === 0) {
                        // 히스토리가 없으면 새 채팅 생성하지 않고 사용법 안내만 표시
                        console.log('No chat history found, showing empty state');
                        this.renderHistoryList();
                        this.showEmptyState();
                    } else {
                        // 히스토리가 있으면 가장 최근 채팅을 자동으로 선택
                        console.log('Chat history found, selecting most recent chat');
                        this.renderHistoryList();
                        // 가장 최근 채팅 (인덱스 0)을 선택
                        this.selectChat(0);
                    }
                    this.hasInitialized = true;
                } else {
                    // 히스토리 목록 렌더링 (항상 실행)
                    console.log('Rendering history list (already initialized)');
                    this.renderHistoryList();
                }
            } else {
                console.error('Failed to load chat histories:', data.message);
                // 로드 실패 시에도 빈 상태 표시 (새 채팅 자동 생성하지 않음)
                if (!this.hasInitialized) {
                    this.renderHistoryList();
                    this.showEmptyState();
                    this.hasInitialized = true;
                }
            }
        } catch (error) {
            console.error('Error loading chat histories:', error);
            // 에러 발생 시에도 빈 상태 표시 (새 채팅 자동 생성하지 않음)
            if (!this.hasInitialized) {
                this.renderHistoryList();
                this.showEmptyState();
                this.hasInitialized = true;
            }
        }
    }
    
    // 시간 포맷팅 함수
    formatTime(isoString) {
        const date = new Date(isoString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        if (diffMins < 1) return '방금 전';
        if (diffMins < 60) return `${diffMins}분 전`;
        if (diffHours < 24) return `${diffHours}시간 전`;
        if (diffDays < 7) return `${diffDays}일 전`;
        
        return date.toLocaleDateString('ko-KR');
    }
    
    // 특정 채팅의 메시지 로드
    async loadChatMessages(chatId) {
        try {
            const response = await fetch(`/kb_bank/chatbot/api/chat/histories/${chatId}/messages/`);
            const data = await response.json();
            
            if (data.success) {
                return data.messages;
            } else {
                console.error('Failed to load chat messages:', data.message);
                return [];
            }
        } catch (error) {
            console.error('Error loading chat messages:', error);
            return [];
        }
    }
    
    // 채팅 히스토리 새로고침
    async refreshChatHistories() {
        console.log('Refreshing chat histories...');
        // 새로고침 시에는 초기화 플래그를 true로 설정하여 새 채팅 생성을 방지
        this.hasInitialized = true;
        await this.loadChatHistories();
    }
    
    // 외부에서 호출할 수 있는 메서드들
    addChatMessage(chatId, message) {
        const chat = this.chatHistory.find(c => c.id === chatId);
        if (chat) {
            chat.title = message.length > 20 ? message.substring(0, 20) + '...' : message;
            chat.time = '방금 전';
            chat.timestamp = Date.now();
            chat.isNew = false;  // 메시지가 있으므로 더 이상 새 채팅이 아님
            
            // UI 업데이트
            this.renderHistoryList();
        }
    }
    
    // 새 채팅 상태를 업데이트하는 함수
    updateChatStatus(chatId, isNew = false) {
        const chat = this.chatHistory.find(c => c.id === chatId);
        if (chat) {
            chat.isNew = isNew;
            this.renderHistoryList();
        }
    }
    
    // 채팅 제목 업데이트 함수
    updateChatTitle(chatId, title) {
        console.log('updateChatTitle called:', { chatId, title });
        console.log('Current chat history:', this.chatHistory);
        
        // 해당 채팅 ID를 가진 채팅 찾기 (타입 변환 고려)
        const chatIndex = this.chatHistory.findIndex(chat => 
            chat.id === chatId || 
            chat.id === parseInt(chatId) || 
            chat.id === String(chatId)
        );
        console.log('Found chat index:', chatIndex);
        
        if (chatIndex !== -1) {
            const currentTitle = this.chatHistory[chatIndex].title;
            console.log('Current title:', currentTitle);
            
            // 제목 업데이트 (조건 완화)
            if (title && title.trim()) {
                this.chatHistory[chatIndex].title = title.trim();
                this.renderHistoryList();
                console.log('Chat title updated successfully from', currentTitle, 'to', title.trim());
            } else {
                console.log('Title not updated - no valid title provided:', title);
            }
        } else {
            console.log('Chat not found for ID:', chatId);
        }
    }
    
    // 빈 상태 표시 함수 (히스토리가 없을 때)
    showEmptyState() {
        console.log('Showing empty state - no chat history');
        
        // 웰컴 메시지와 자주 묻는 질문을 먼저 숨김
        const welcomeMessageContainer = document.getElementById('welcome_message_container');
        const suggestedQuestionsContainer = document.querySelector('.suggested_questions_container');
        
        if (welcomeMessageContainer) {
            welcomeMessageContainer.style.display = 'none';
        }
        if (suggestedQuestionsContainer) {
            suggestedQuestionsContainer.innerHTML = '';
            suggestedQuestionsContainer.style.display = 'none';
        }
        
        // 메인 챗봇에 빈 상태 알림
        this.notifyMainChatbot('empty_state', null);
    }
}

// DOM이 로드되면 초기화
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing Chat History Column');
    window.chatHistoryColumn = new ChatHistoryColumn();
});