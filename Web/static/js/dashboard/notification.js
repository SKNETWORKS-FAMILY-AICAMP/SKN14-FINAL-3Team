// Notification Widget JavaScript

class NotificationWidget {
    constructor() {
        this.notifications = [
            {
                id: 1,
                type: 'urgent',
                title: '긴급 공지',
                message: '시스템 점검 예정 (오늘 오후 11시~12시)',
                time: '5분 전',
                timestamp: Date.now() - 5 * 60 * 1000
            },
            {
                id: 2,
                type: 'info',
                title: '신규 서비스',
                message: 'KB 스마트뱅킹 2.0 출시 안내',
                time: '1시간 전',
                timestamp: Date.now() - 60 * 60 * 1000
            },
            {
                id: 3,
                type: 'success',
                title: '업데이트 완료',
                message: '보안 시스템 업데이트가 완료되었습니다',
                time: '2시간 전',
                timestamp: Date.now() - 2 * 60 * 60 * 1000
            },
            {
                id: 4,
                type: 'warning',
                title: '보안 알림',
                message: '의심스러운 로그인 시도 감지',
                time: '3시간 전',
                timestamp: Date.now() - 3 * 60 * 60 * 1000
            }
        ];
        
        this.init();
    }
    
    init() {
        this.updateDisplay();
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // 알림 아이템 클릭 이벤트
        document.addEventListener('click', (event) => {
            const notificationItem = event.target.closest('.notification-item');
            if (notificationItem) {
                this.onNotificationClick(notificationItem);
            }
        });
    }
    
    updateDisplay() {
        // 알림 개수 업데이트
        const countElement = document.getElementById('notification-count');
        if (countElement) {
            countElement.textContent = this.notifications.length;
        }
        
        // 시간 업데이트
        this.updateNotificationTimes();
    }
    
    updateNotificationTimes() {
        const now = Date.now();
        
        this.notifications.forEach(notification => {
            const timeDiff = now - notification.timestamp;
            const minutes = Math.floor(timeDiff / (1000 * 60));
            const hours = Math.floor(timeDiff / (1000 * 60 * 60));
            
            let timeText;
            if (minutes < 60) {
                timeText = `${minutes}분 전`;
            } else if (hours < 24) {
                timeText = `${hours}시간 전`;
            } else {
                const days = Math.floor(hours / 24);
                timeText = `${days}일 전`;
            }
            
            notification.time = timeText;
        });
    }
    
    onNotificationClick(notificationItem) {
        // 클릭 시 애니메이션 효과
        notificationItem.style.transform = 'scale(0.98)';
        setTimeout(() => {
            notificationItem.style.transform = '';
        }, 150);
        
        // 실제로는 알림 상세 페이지로 이동하거나 모달을 띄울 수 있음
        console.log('알림 클릭됨:', notificationItem);
    }
    
    
    // 특정 타입의 알림 개수 가져오기
    getNotificationCount(type = null) {
        if (type) {
            return this.notifications.filter(n => n.type === type).length;
        }
        return this.notifications.length;
    }
}

// 페이지 로드 시 위젯 초기화
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM 로드 완료, 알림 위젯 초기화 시작');
    if (document.querySelector('.notification-widget')) {
        console.log('알림 위젯 요소 발견, 초기화 중...');
        window.notificationWidget = new NotificationWidget();
        console.log('알림 위젯 초기화 완료');
    } else {
        console.log('알림 위젯 요소를 찾을 수 없습니다.');
    }
});

// DOM이 이미 로드된 경우를 위한 백업
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    console.log('DOM 이미 로드됨, 즉시 초기화');
    if (document.querySelector('.notification-widget')) {
        window.notificationWidget = new NotificationWidget();
    }
}
