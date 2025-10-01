const headerLogo = document.querySelector('.kb-logo');
const logoutBtn = document.querySelector('.logout-btn');

if (headerLogo) {
    headerLogo.addEventListener('click', () => {
        window.location.href = '/kb_bank/dashboard/';
    });
}

// 로그아웃 버튼이 존재할 때만 이벤트 리스너 추가
if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
        // 보고서 목록 초기화
        if (window.reportsColumn) {
            console.log('로그아웃 시 보고서 목록 초기화');
            window.reportsColumn.clearReportsOnLogout();
        }
        
        // Django logout view를 호출하여 세션을 정리하고 로그인 페이지로 리다이렉트
        window.location.href = '/kb_bank/logout/';
    });
}

