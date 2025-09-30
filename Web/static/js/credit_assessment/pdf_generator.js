/**
 * PDF 보고서 생성 유틸리티
 * 하드코딩된 HTML/CSS를 제거하고 서버 템플릿을 사용
 */

/**
 * CSRF 토큰 가져오기
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * 서버에서 PDF 템플릿 생성
 */
async function generatePdfTemplate(customerName, thirdColumnHTML) {
    try {
        const csrfToken = getCookie('csrftoken');
        console.log('CSRF 토큰:', csrfToken);
        
        const response = await fetch('/kb_bank/credit_assessment/api/generate-pdf-report/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                customer_name: customerName,
                third_column_html: thirdColumnHTML
            })
        });
        
        console.log('서버 응답 상태:', response.status);
        console.log('서버 응답 헤더:', response.headers);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('서버 오류 응답:', errorText);
            throw new Error(`서버 오류 (${response.status}): ${errorText}`);
        }
        
        const result = await response.json();
        console.log('서버 응답 데이터:', result);
        
        if (!result.success) {
            throw new Error(result.message || 'PDF 템플릿 생성에 실패했습니다.');
        }
        
        return result.pdf_html;
        
    } catch (error) {
        console.error('PDF 템플릿 생성 오류:', error);
        throw error;
    }
}

/**
 * PDF 다운로드 실행
 */
async function downloadPdfReport(customerName, thirdColumnHTML) {
    try {
        console.log('PDF 보고서 생성 시작...');
        
        // 서버에서 PDF 템플릿 생성
        const reportContent = await generatePdfTemplate(customerName, thirdColumnHTML);
        
        // Blob 생성
        const blob = new Blob([reportContent], { type: 'text/html' });
        const blobUrl = URL.createObjectURL(blob);
        
        // 현재 날짜 생성
        const now = new Date();
        const dateString = now.toLocaleDateString('ko-KR', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        }).replace(/\./g, '-').replace(/\s/g, '');
        
        // 보고서 객체 생성
        const report = {
            name: `${customerName}_신용평가보고서_${dateString}`,
            date: now.toLocaleDateString('ko-KR'),
            url: blobUrl,
            filePath: blobUrl,
            filename: `${customerName}_신용평가보고서_${dateString}.html`
        };
        
        // 보고서 리스트에 추가
        if (window.reportsColumn) {
            window.reportsColumn.addReport(report);
            console.log('보고서가 리스트에 추가되었습니다.');
        } else {
            console.warn('reportsColumn이 정의되지 않았습니다.');
        }
        
        // 새 창 열지 않고 보고서 리스트에만 추가
        console.log('PDF 보고서가 보고서 리스트에 추가되었습니다. 리스트에서 클릭하여 확인하세요.');
        
        console.log('PDF 보고서 생성 완료');
        
    } catch (error) {
        console.error('PDF 생성 중 오류:', error);
        alert('PDF 생성 중 오류가 발생했습니다: ' + error.message);
    }
}

/**
 * 기존 generateReport 함수를 새로운 방식으로 교체
 */
window.generateReport = async function() {
    // 기존 로직에서 필요한 데이터 추출
    const customerName = window.currentCustomer?.full_name || '고객';
    const thirdColumnElement = document.querySelector('.third_column');
    
    if (!thirdColumnElement) {
        alert('심사 결과가 없습니다. 먼저 여신 심사를 진행해주세요.');
        return;
    }
    
    const thirdColumnHTML = thirdColumnElement.outerHTML;
    
    // PDF 생성 실행
    await downloadPdfReport(customerName, thirdColumnHTML);
};
