// KB국민은행 직원 업무시스템 - 대시보드 JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // KB 업무 지원 챗봇 클릭 이벤트
    const chatbotContainer = document.querySelector('.chatbot_container');
    if (chatbotContainer) {
        chatbotContainer.addEventListener('click', function() {
            window.location.href = '/kb_bank/chatbot/';
        });
    }

    // KB 대시보드 클릭 이벤트
    const creditAssessmentContainer = document.querySelector('.credit_assessment_container');
    if (creditAssessmentContainer) {
        creditAssessmentContainer.addEventListener('click', function() {
            window.location.href = '/kb_bank/credit_assessment/';
        });
    }
});

// 로그아웃 함수
function logout() {
    if (confirm('로그아웃 하시겠습니까?')) {
        // 보고서 목록 초기화
        if (window.reportsColumn) {
            console.log('로그아웃 시 보고서 목록 초기화');
            window.reportsColumn.clearReportsOnLogout();
        }
        
        window.location.href = '/kb_bank/logout/';
    }
}
