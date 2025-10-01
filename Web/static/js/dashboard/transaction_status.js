// Transaction Status Widget JavaScript

class TransactionStatusWidget {
    constructor() {
        this.transactions = {
            deposit: 1247,
            withdrawal: 892,
            transfer: 2156,
            total: 4295
        };
        
        this.updateInterval = null;
        this.init();
    }
    
    init() {
        this.updateDisplay();
        this.setupAutoRefresh();
        this.setupRefreshButton();
    }
    
    setupAutoRefresh() {
        // 1분마다 자동으로 거래 현황 업데이트
        this.updateInterval = setInterval(() => {
            this.refreshTransactions();
        }, 60000); // 1분 = 60초
    }
    
    setupRefreshButton() {
        const refreshBtn = document.getElementById('transaction-refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshTransactions());
        }
    }
    
    updateDisplay() {
        // 각 거래 건수 업데이트
        Object.keys(this.transactions).forEach(type => {
            const element = document.getElementById(`${type}-count`);
            if (element) {
                element.textContent = this.transactions[type].toLocaleString();
            }
        });
        
        // 변동률 업데이트
        this.updateChangeRates();
        
        // 업데이트 시간 표시
        this.updateLastUpdateTime();
    }
    
    refreshTransactions() {
        const refreshBtn = document.getElementById('transaction-refresh-btn');
        
        if (refreshBtn) {
            // 버튼 애니메이션 (환율 위젯과 동일)
            refreshBtn.style.transform = 'rotate(360deg)';
            setTimeout(() => {
                refreshBtn.style.transform = 'rotate(0deg)';
            }, 300);
        }
        
        // 거래 현황 시뮬레이션 업데이트
        this.simulateTransactionUpdate();
        this.updateDisplay();
    }
    
    updateLastUpdateTime() {
        const lastUpdateElement = document.getElementById('transaction-last-update');
        if (lastUpdateElement) {
            const now = new Date();
            const timeStr = now.toLocaleTimeString('ko-KR', {
                hour12: true,
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
            lastUpdateElement.textContent = `마지막 업데이트: ${timeStr}`;
        }
    }
    
    simulateTransactionUpdate() {
        // 실제로는 API에서 받아온 데이터로 업데이트
        // 여기서는 시뮬레이션으로 거래 건수 증가
        Object.keys(this.transactions).forEach(type => {
            const increase = Math.floor(Math.random() * 10) + 1; // 1~10건 증가
            this.transactions[type] += increase;
        });
        
        // 총 거래 건수는 개별 거래의 합
        this.transactions.total = this.transactions.deposit + this.transactions.withdrawal + this.transactions.transfer;
    }
    
    updateChangeRates() {
        // 변동률 시뮬레이션 (실제로는 이전 데이터와 비교)
        const changeData = {
            deposit: { value: '+156', percent: '↑ 12.5%' },
            withdrawal: { value: '-29', percent: '↓ 3.2%' },
            transfer: { value: '+187', percent: '↑ 8.7%' },
            total: { value: '+314', percent: '↑ 5.8%' }
        };
        
        Object.keys(changeData).forEach(type => {
            const changeValueElement = document.getElementById(`${type}-change`);
            const changePercentElement = document.getElementById(`${type}-percent`);
            
            if (changeValueElement && changePercentElement) {
                const data = changeData[type];
                changeValueElement.textContent = data.value;
                changePercentElement.textContent = data.percent;
                
                // 색상 클래스 적용
                const isPositive = data.value.startsWith('+');
                changeValueElement.className = `change-value ${isPositive ? 'positive' : 'negative'}`;
                changePercentElement.className = `change-percent ${isPositive ? 'positive' : 'negative'}`;
            }
        });
    }
    
    // 특정 거래 타입의 값을 가져오는 메서드
    getTransactionCount(type) {
        return this.transactions[type] || null;
    }
}

// 페이지 로드 시 위젯 초기화
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM 로드 완료, 거래 현황 위젯 초기화 시작');
    if (document.querySelector('.transaction-status-widget')) {
        console.log('거래 현황 위젯 요소 발견, 초기화 중...');
        window.transactionStatusWidget = new TransactionStatusWidget();
        console.log('거래 현황 위젯 초기화 완료');
    } else {
        console.log('거래 현황 위젯 요소를 찾을 수 없습니다.');
    }
});

// DOM이 이미 로드된 경우를 위한 백업
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    console.log('DOM 이미 로드됨, 즉시 초기화');
    if (document.querySelector('.transaction-status-widget')) {
        window.transactionStatusWidget = new TransactionStatusWidget();
    }
}

// 페이지 언로드 시 정리
window.addEventListener('beforeunload', function() {
    if (window.transactionStatusWidget && window.transactionStatusWidget.updateInterval) {
        clearInterval(window.transactionStatusWidget.updateInterval);
    }
});
