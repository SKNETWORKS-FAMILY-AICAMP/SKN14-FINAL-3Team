// Team Channel Column Component JavaScript

class TeamChannelColumn {
    constructor() {
        this.isExpanded = false;
        this.init();
        this.syncExpandedState();
    }
    
    init() {
        this.setupEventListeners();
        this.setupChannelSwitching();
        this.setupMemberActions();
        this.setupChatInput();
    }
    
    syncExpandedState() {
        const teamChannelColumn = document.querySelector('.team_channel_column');
        if (teamChannelColumn) {
            this.isExpanded = teamChannelColumn.classList.contains('expanded');
            console.log('Synced expanded state:', this.isExpanded);
        }
    }
    
    setupEventListeners() {
        const teamChannelColumn = document.querySelector('.team_channel_column');
        const collapseBtn = document.getElementById('team-channel-collapse');
        
        console.log('Team Channel Column - Setting up event listeners');
        console.log('Team Channel Column found:', teamChannelColumn);
        console.log('Collapse Button found:', collapseBtn);
        
        // team_channel_column 전체 클릭 시 확장만 (축소는 X 버튼으로만)
        if (teamChannelColumn) {
            teamChannelColumn.addEventListener('click', (e) => {
                console.log('Team channel column clicked, target:', e.target);
                // X 버튼 클릭이 아닌 경우에만 확장
                if (!e.target.closest('.collapse_btn')) {
                    console.log('Expanding team channel column');
                    this.expand();
                }
            });
        }
        
        // X 버튼 클릭 시 축소
        if (collapseBtn) {
            collapseBtn.addEventListener('click', (e) => {
                console.log('X button clicked - collapsing team channel column');
                e.stopPropagation();
                this.collapse();
            });
        } else {
            console.error('Collapse button not found!');
        }
    }
    
    toggleExpansion() {
        const teamChannelColumn = document.querySelector('.team_channel_column');
        
        if (teamChannelColumn) {
            this.isExpanded = !this.isExpanded;
            
            if (this.isExpanded) {
                teamChannelColumn.classList.add('expanded');
            } else {
                teamChannelColumn.classList.remove('expanded');
            }
        }
    }
    
    setupChannelSwitching() {
        const channelItems = document.querySelectorAll('.channel_item');
        
        channelItems.forEach(item => {
            item.addEventListener('click', () => {
                // 모든 채널에서 active 클래스 제거
                channelItems.forEach(channel => channel.classList.remove('active'));
                
                // 클릭된 채널에 active 클래스 추가
                item.classList.add('active');
                
                // 채널 이름 업데이트
                const channelName = item.querySelector('.channel_name').textContent;
                this.updateChatHeader(channelName);
                
                // 채널별 메시지 로드 (실제로는 API 호출)
                this.loadChannelMessages(channelName);
            });
        });
    }
    
    setupMemberActions() {
        const memberItems = document.querySelectorAll('.member_item');
        
        memberItems.forEach(item => {
            const actionBtn = item.querySelector('.member_action');
            
            if (actionBtn) {
                actionBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    
                    const memberName = item.querySelector('.member_name').textContent;
                    const memberDept = item.querySelector('.member_dept').textContent;
                    
                    // 개인 메시지 시작 (실제로는 모달이나 새 창 열기)
                    this.startPrivateMessage(memberName, memberDept);
                });
            }
        });
    }
    
    setupChatInput() {
        const chatInput = document.querySelector('.chat_input_field');
        const sendButton = document.querySelector('.send_button');
        
        if (chatInput && sendButton) {
            // 엔터키로 메시지 전송
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.sendMessage();
                }
            });
            
            // 전송 버튼 클릭
            sendButton.addEventListener('click', () => {
                this.sendMessage();
            });
        }
    }
    
    updateChatHeader(channelName) {
        const chatTitle = document.querySelector('.chat_title .channel_name');
        
        if (chatTitle) {
            chatTitle.textContent = channelName;
        }
    }
    
    loadChannelMessages(channelName) {
        const chatMessages = document.querySelector('.chat_messages');
        
        if (chatMessages) {
            // 실제로는 API에서 메시지를 가져와야 함
            // 여기서는 시뮬레이션
            chatMessages.innerHTML = `
                <div class="message">
                    <div class="message_info">
                        <span class="sender_name">시스템</span>
                        <span class="message_time">${new Date().toLocaleTimeString()}</span>
                    </div>
                    <div class="message_content">${channelName} 채널로 전환되었습니다.</div>
                </div>
            `;
        }
    }
    
    sendMessage() {
        const chatInput = document.querySelector('.chat_input_field');
        const chatMessages = document.querySelector('.chat_messages');
        
        if (chatInput && chatMessages && chatInput.value.trim()) {
            const message = chatInput.value.trim();
            
            // 메시지 추가
            this.addMessage('나', message, true);
            
            // 입력 필드 초기화
            chatInput.value = '';
            
            // 실제로는 서버에 메시지 전송
            console.log('메시지 전송:', message);
        }
    }
    
    addMessage(sender, content, isOwn = false) {
        const chatMessages = document.querySelector('.chat_messages');
        
        if (chatMessages) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message';
            
            if (isOwn) {
                messageDiv.style.textAlign = 'right';
            }
            
            messageDiv.innerHTML = `
                <div class="message_info">
                    <span class="sender_name">${sender}</span>
                    <span class="message_time">${new Date().toLocaleTimeString()}</span>
                </div>
                <div class="message_content">${content}</div>
            `;
            
            chatMessages.appendChild(messageDiv);
            
            // 스크롤을 맨 아래로
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
    
    startPrivateMessage(memberName, memberDept) {
        // 개인 메시지 시작 로직
        console.log(`개인 메시지 시작: ${memberName} (${memberDept})`);
        
        // 실제로는 모달이나 새 창을 열어야 함
        alert(`${memberName}님과의 개인 메시지를 시작합니다.`);
    }
    
    // 외부에서 호출할 수 있는 메서드들
    expand() {
        const teamChannelColumn = document.querySelector('.team_channel_column');
        
        if (teamChannelColumn && !this.isExpanded) {
            this.isExpanded = true;
            teamChannelColumn.classList.add('expanded');
            console.log('Successfully expanded team channel column');
        }
    }
    
    collapse() {
        const teamChannelColumn = document.querySelector('.team_channel_column');
        
        console.log('Collapse method called');
        console.log('Team Channel Column found:', teamChannelColumn);
        console.log('Is expanded:', this.isExpanded);
        
        if (teamChannelColumn && this.isExpanded) {
            this.isExpanded = false;
            teamChannelColumn.classList.remove('expanded');
            console.log('Successfully collapsed team channel column');
        } else {
            console.log('Cannot collapse - either element not found or not expanded');
        }
    }
    
    isExpandedState() {
        return this.isExpanded;
    }
}

// 전역 인스턴스 생성
let teamChannelColumnInstance = null;

// 초기화 함수
function initTeamChannelColumn() {
    console.log('Initializing Team Channel Column...');
    const teamChannelElement = document.querySelector('.team_channel_column');
    console.log('Team Channel Column element found:', teamChannelElement);
    console.log('Existing instance:', teamChannelColumnInstance);
    
    if (teamChannelElement && !teamChannelColumnInstance) {
        console.log('Creating new TeamChannelColumn instance');
        teamChannelColumnInstance = new TeamChannelColumn();
        window.teamChannelColumn = teamChannelColumnInstance;
        console.log('TeamChannelColumn initialized successfully');
    } else {
        console.log('TeamChannelColumn already initialized or element not found');
    }
}

// DOM 로드 시 초기화
document.addEventListener('DOMContentLoaded', initTeamChannelColumn);

// DOM이 이미 로드된 경우를 위한 백업
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    initTeamChannelColumn();
}
