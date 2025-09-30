// 전역 변수
window.isGeneratingReport = false;

// 심사 결과 컬럼 초기화 함수
window.clearAssessmentResults = function() {
    console.log('=== 심사 결과 컬럼 초기화 시작 ===');
    
    const thirdColumn = document.querySelector('.third_column');
    if (thirdColumn) {
        // third_column 안의 심사 결과만 제거하고 usage_guide_container는 그대로 유지
        const assessmentResults = thirdColumn.querySelectorAll('.assessment_result, .assessment_summary, .assessment_chart, .assessment_results');
        assessmentResults.forEach(result => {
            result.remove();
        });
        
        // usage_guide_container가 없다면 원래 HTML로 복원
        const usageGuideContainer = thirdColumn.querySelector('#usage_guide_container');
        if (!usageGuideContainer) {
            // 원래 HTML 구조로 복원
            thirdColumn.innerHTML = `
                <div id="usage_guide_container">
                    <div class="usage_guide">
                        <div class="usage_guide_header">
                            <div class="usage_guide_icon">
                                <i class="bi bi-lightbulb"></i>
                            </div>
                            <h3 class="usage_guide_title">KB FinAIssist 여신심사 사용법</h3>
                        </div>
                        <div class="usage_guide_content">
                            <div class="usage_guide_step">
                                <div class="step_number">1</div>
                                <div class="step_content">
                                    <h4>고객 정보 확인</h4>
                                    <p>고객명, 주민번호, 연락처를 입력하여 고객 정보를 확인합니다.</p>
                                </div>
                            </div>
                            <div class="usage_guide_step">
                                <div class="step_number">2</div>
                                <div class="step_content">
                                    <h4>대출 정보 입력</h4>
                                    <p>대출 금액, 목적, 상품, 기간을 입력합니다.</p>
                                </div>
                            </div>
                            <div class="usage_guide_step">
                                <div class="step_number">3</div>
                                <div class="step_content">
                                    <h4>여신 심사 요청</h4>
                                    <p>모든 정보 입력 후 여신 심사를 요청합니다.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
        
        console.log('심사 결과 컬럼 초기화 완료');
    }
    
    // usage_guide_container 스타일 초기화 (인라인 스타일 제거)
    const usageGuideContainer = document.getElementById('usage_guide_container');
    if (usageGuideContainer) {
        usageGuideContainer.style.display = '';
        console.log('usage_guide_container 스타일 초기화됨');
    } else {
        console.log('usage_guide_container 요소를 찾을 수 없음');
        // third_column에서 다시 찾아보기
        const thirdColumn = document.querySelector('.third_column');
        if (thirdColumn) {
            const existingUsageGuide = thirdColumn.querySelector('#usage_guide_container');
            if (existingUsageGuide) {
                existingUsageGuide.style.display = '';
                console.log('third_column에서 usage_guide_container 찾아서 스타일 초기화됨');
            }
        }
    }
    
    console.log('=== 심사 결과 컬럼 초기화 완료 ===');
};

// createAndSaveReport 함수 (전역 함수로 노출)
window.createAndSaveReport = async function() {
    try {
        // 중복 실행 방지
        if (window.isGeneratingReport) {
            console.log('이미 보고서 생성 중입니다.');
            return;
        }
        
        window.isGeneratingReport = true;
        console.log('=== createAndSaveReport 함수 시작 ===');
        
        // third_column 요소 찾기
        const thirdColumn = document.querySelector('.third_column');
        if (!thirdColumn) {
            console.error('third_column 요소를 찾을 수 없습니다.');
            alert('심사 결과가 없습니다. 먼저 여신 심사를 진행해주세요.');
            window.isGeneratingReport = false;
            return;
        }
        
        // 고객명 가져오기
        const customerNameInput = document.querySelector('input[name="customer_name"]');
        const customerName = customerNameInput ? customerNameInput.value : '고객';
        
        // third_column의 HTML 내용을 직접 가져오기
        const thirdColumnHTML = thirdColumn.innerHTML;
        console.log('third_column HTML:', thirdColumnHTML);
        console.log('third_column HTML 길이:', thirdColumnHTML.length);
        
        // HTML 내용이 비어있는지 확인
        if (!thirdColumnHTML || thirdColumnHTML.trim().length === 0) {
            console.error('third_column HTML이 비어있습니다!');
            alert('심사 결과가 없습니다. 먼저 여신 심사를 진행해주세요.');
            window.isGeneratingReport = false;
            return;
        }
        
        // 새로운 PDF 생성 방식 사용
        await downloadPdfReport(customerName, thirdColumnHTML);
        
        // PDF 생성 완료
        window.isGeneratingReport = false;
        console.log('=== createAndSaveReport 함수 완료 ===');
        
    } catch (error) {
        console.error('PDF 생성 중 오류:', error);
        alert('PDF 생성 중 오류가 발생했습니다: ' + error.message);
        window.isGeneratingReport = false;
    }
};

console.log('=== createAndSaveReport 함수 정의 완료 (전역) ===');
