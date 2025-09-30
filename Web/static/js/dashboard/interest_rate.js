// Interest Rate Widget JavaScript

class InterestRateWidget {
    constructor() {
        this.rates = {
            deposit: 3.25,
            mortgage: 4.15,
            credit: 5.85,
            savings: 3.45,
            business: 4.75,
            foreign: 2.95
        };
        
        this.updateInterval = null;
        this.init();
    }
    
    init() {
        // 즉시 실행
        this.updateDisplay();
        this.setupAutoRefresh();
        this.setupRefreshButton();
    }
    
    setupAutoRefresh() {
        // 5분마다 자동으로 금리 정보 업데이트
        this.updateInterval = setInterval(() => {
            this.refreshRates();
        }, 300000); // 5분 = 300초
    }
    
    setupRefreshButton() {
        const refreshBtn = document.getElementById('interest-refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshRates());
        }
    }
    
    updateDisplay() {
        // 각 금리 값 업데이트
        Object.keys(this.rates).forEach(type => {
            const element = document.getElementById(`${type}-rate`);
            if (element) {
                element.textContent = this.rates[type].toFixed(2);
            }
        });
        
        // 업데이트 시간 표시
        this.updateLastUpdateTime();
    }
    
    refreshRates() {
        const refreshBtn = document.getElementById('interest-refresh-btn');
        
        if (refreshBtn) {
            // 금리 정보 업데이트
            this.simulateRateChange();
            this.updateDisplay();
            
            // 버튼 애니메이션 (환율 위젯과 동일)
            refreshBtn.style.transform = 'rotate(360deg)';
            setTimeout(() => {
                refreshBtn.style.transform = 'rotate(0deg)';
            }, 300);
        }
    }
    
    
    updateLastUpdateTime() {
        const lastUpdateElement = document.getElementById('last-update');
        if (lastUpdateElement) {
            const now = new Date();
            const timeStr = now.toLocaleTimeString('ko-KR', {
                hour12: true,
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
            lastUpdateElement.textContent = `마지막 업데이트: ${timeStr}`;
            console.log('금리 정보 시간 업데이트:', timeStr); // 디버깅용
        } else {
            console.log('last-update 요소를 찾을 수 없습니다.'); // 디버깅용
        }
    }
    
    simulateRateChange() {
        // 실제로는 API에서 받아온 데이터로 업데이트
        // 여기서는 시뮬레이션으로 ±0.05% 범위에서 랜덤 변동
        Object.keys(this.rates).forEach(type => {
            const change = (Math.random() - 0.5) * 0.1; // -0.05 ~ +0.05
            this.rates[type] = Math.max(0, this.rates[type] + change);
        });
    }
    
    onRateItemClick(event) {
        const rateItem = event.currentTarget;
        const rateType = rateItem.dataset.type;
        const rateValue = this.rates[rateType];
        
        // 클릭된 금리 항목에 대한 상세 정보 표시 (선택사항)
        console.log(`${rateType} 금리: ${rateValue}%`);
        
        // 시각적 피드백
        rateItem.style.transform = 'scale(0.95)';
        setTimeout(() => {
            rateItem.style.transform = '';
        }, 150);
    }
    
    
    // 특정 금리 타입의 값을 가져오는 메서드
    getRate(type) {
        return this.rates[type] || null;
    }
    
}


// 페이지 로드 시 위젯 초기화
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM 로드 완료, 금리 위젯 초기화 시작');
    if (document.querySelector('.interest-rate-widget')) {
        console.log('금리 위젯 요소 발견, 초기화 중...');
        window.interestRateWidget = new InterestRateWidget();
        console.log('금리 위젯 초기화 완료');
    } else {
        console.log('금리 위젯 요소를 찾을 수 없습니다.');
    }
});

// DOM이 이미 로드된 경우를 위한 백업
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    console.log('DOM 이미 로드됨, 즉시 초기화');
    if (document.querySelector('.interest-rate-widget')) {
        window.interestRateWidget = new InterestRateWidget();
    }
}

// 페이지 언로드 시 정리
window.addEventListener('beforeunload', function() {
    if (window.interestRateWidget && window.interestRateWidget.updateInterval) {
        clearInterval(window.interestRateWidget.updateInterval);
    }
});

