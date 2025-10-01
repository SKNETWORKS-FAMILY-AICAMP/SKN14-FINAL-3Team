// Exchange Rate Widget JavaScript

// 배포할때는 무료 alpha vantage api 받아야함
// 지금은 시뮬레이션으로 처리되고 있음 (금액은 실제금액)
class ExchangeRateWidget {
    constructor() {
        this.currencies = ['USD', 'EUR', 'JPY', 'CNY'];
        this.previousRates = {};
        this.isFirstLoad = true;
        this.initialChanges = {}; // 첫 로드 시 변동 정보 저장
        this.init();
    }
    
    init() {
        this.fetchExchangeRates();
        this.setupAutoRefresh();
        this.setupRefreshButton();
    }
    
    async fetchExchangeRates() {
        try {
            // ExchangeRate-API 사용 (무료, 안정적)
            const response = await fetch('https://api.exchangerate-api.com/v4/latest/KRW');
            const data = await response.json();
            
            if (data.rates) {
                this.updateExchangeRatesWithSimulation(data.rates);
                this.updateLastUpdateTime();
            } else {
                this.showErrorState('API 응답 에러');
            }
            
            // 첫 로드 후 플래그 변경
            if (this.isFirstLoad) {
                this.isFirstLoad = false;
            }
            
        } catch (error) {
            console.error('환율 정보를 가져오는데 실패했습니다:', error);
            this.showErrorState('네트워크 에러: ' + error.message);
        }
    }
    
    
    updateExchangeRatesWithSimulation(rates) {
        // ExchangeRate-API 데이터 처리 (변동 정보 시뮬레이션)
        const currencyData = {
            'USD': { rate: rates.USD, label: 'USD/KRW' },
            'EUR': { rate: rates.EUR, label: 'EUR/KRW' },
            'JPY': { rate: rates.JPY, label: 'JPY/KRW' },
            'CNY': { rate: rates.CNY, label: 'CNY/KRW' }
        };
        
        this.currencies.forEach(currency => {
            const data = currencyData[currency];
            if (data) {
                // 환율 표시 (실제 API 데이터)
                const displayRate = this.formatRate(1 / data.rate, currency);
                document.getElementById(`${currency.toLowerCase()}-rate`).textContent = displayRate;
                
                // 변동 정보 시뮬레이션
                this.updateCurrencyWithSimulation(currency, 1 / data.rate);
            }
        });
    }
    
    updateCurrencyWithSimulation(currency, currentRate) {
        // 변동 정보 시뮬레이션
        if (this.isFirstLoad) {
            // 첫 로드 시 랜덤 변동 생성
            const randomChange = (Math.random() - 0.5) * 20; // -10 ~ +10 범위
            const randomPercent = (Math.random() - 0.5) * 2; // -1 ~ +1 범위
            
            const isPositive = randomChange > 0;
            const changeValue = Math.abs(randomChange).toFixed(2);
            const changePercentValue = Math.abs(randomPercent).toFixed(2);
            
            // 변동 정보 표시
            const changeValueElement = document.getElementById(`${currency.toLowerCase()}-change`);
            const changePercentElement = document.getElementById(`${currency.toLowerCase()}-percent`);
            
            if (changeValueElement) {
                changeValueElement.textContent = `${isPositive ? '+' : '-'}${changeValue}`;
                changeValueElement.className = `change-value ${isPositive ? 'positive' : 'negative'}`;
            }
            
            if (changePercentElement) {
                changePercentElement.textContent = `${isPositive ? '↑' : '↓'} ${changePercentValue}%`;
                changePercentElement.className = `change-percent ${isPositive ? 'positive' : 'negative'}`;
            }
            
            // 첫 로드 시 변동 정보 저장
            this.initialChanges[currency] = {
                value: `${isPositive ? '+' : '-'}${changeValue}`,
                percent: `${isPositive ? '↑' : '↓'} ${changePercentValue}%`,
                isPositive: isPositive
            };
        } else {
            // 이후에는 저장된 변동 정보 유지
            const savedChange = this.initialChanges[currency];
            if (savedChange) {
                const changeValueElement = document.getElementById(`${currency.toLowerCase()}-change`);
                const changePercentElement = document.getElementById(`${currency.toLowerCase()}-percent`);
                
                if (changeValueElement) {
                    changeValueElement.textContent = savedChange.value;
                    changeValueElement.className = `change-value ${savedChange.isPositive ? 'positive' : 'negative'}`;
                }
                
                if (changePercentElement) {
                    changePercentElement.textContent = savedChange.percent;
                    changePercentElement.className = `change-percent ${savedChange.isPositive ? 'positive' : 'negative'}`;
                }
            }
        }
        
        // 이전 환율 저장
        this.previousRates[currency] = currentRate;
    }
    
    formatRate(rate, currency) {
        if (currency === 'JPY') {
            // JPY는 100엔 기준
            return (rate * 100).toFixed(2);
        } else {
            return rate.toFixed(2);
        }
    }
    
    updateLastUpdateTime() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('ko-KR', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: true
        });
        
        document.getElementById('exchange-last-update').textContent = `마지막 업데이트: ${timeString}`;
    }
    
    showErrorState(errorMessage = '데이터 로드 실패') {
        this.currencies.forEach(currency => {
            // 에러 시 에러 메시지 표시
            document.getElementById(`${currency.toLowerCase()}-rate`).textContent = '에러';
            
            const changeValueElement = document.getElementById(`${currency.toLowerCase()}-change`);
            changeValueElement.textContent = '--';
            changeValueElement.className = 'change-value';
            
            const changePercentElement = document.getElementById(`${currency.toLowerCase()}-percent`);
            changePercentElement.textContent = '--';
            changePercentElement.className = 'change-percent';
        });
        
        document.getElementById('exchange-last-update').textContent = `에러: ${errorMessage}`;
    }
    
    setupAutoRefresh() {
        // 5분마다 자동 새로고침
        setInterval(() => {
            this.fetchExchangeRates();
        }, 5 * 60 * 1000);
    }
    
    setupRefreshButton() {
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.fetchExchangeRates();
                
                // 버튼 애니메이션
                refreshBtn.style.transform = 'rotate(360deg)';
                setTimeout(() => {
                    refreshBtn.style.transform = 'rotate(0deg)';
                }, 300);
            });
        }
    }
}


// 페이지 로드 시 위젯 초기화
document.addEventListener('DOMContentLoaded', function() {
    window.exchangeRateWidget = new ExchangeRateWidget();
});
