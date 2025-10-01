/**
 * PDF 모달 관련 JavaScript 기능
 */

// PDF 모달 열기 함수 (전역 함수로 노출)
window.openPdfPopup = function(filePath, pdfTitle) {
    const modal = document.getElementById('pdfModal');
    const modalTitle = document.getElementById('pdfModalTitle');
    const modalViewer = document.getElementById('pdfModalViewer');
    const modalLoading = document.getElementById('pdfModalLoading');
    const modalError = document.getElementById('pdfModalError');
    
    if (!modal || !modalTitle || !modalViewer || !modalLoading || !modalError) {
        console.error('PDF 모달 요소를 찾을 수 없습니다.');
        return;
    }
    
    // 모달 제목 설정
    modalTitle.textContent = pdfTitle || 'PDF 문서';
    
    // 모달 표시
    modal.style.display = 'flex';
    
    // 로딩 상태 표시
    modalLoading.style.display = 'block';
    modalError.style.display = 'none';
    modalViewer.style.display = 'none';
    
    // PDF URL 처리 (Blob URL인지 일반 파일 경로인지 확인)
    let pdfUrl;
    
    if (filePath.startsWith('blob:')) {
        // Blob URL인 경우 직접 사용
        pdfUrl = filePath;
    } else {
        // 일반 파일 경로인 경우 서버 URL로 변환
        const encodedPath = encodeURIComponent(filePath);
        pdfUrl = `/kb_bank/chatbot/pdf/${encodedPath}`;
    }
    
    // iframe에 PDF 로드
    modalViewer.src = pdfUrl;
    
    // iframe 로드 이벤트 처리
    modalViewer.onload = function() {
        modalLoading.style.display = 'none';
        modalViewer.style.display = 'block';
    };
    
    // iframe 에러 이벤트 처리
    modalViewer.onerror = function() {
        modalLoading.style.display = 'none';
        modalError.style.display = 'block';
    };
    
    // Blob URL인 경우 추가 처리
    if (filePath.startsWith('blob:')) {
        // Blob URL의 경우 iframe이 로드되기까지 약간의 시간이 필요할 수 있음
        setTimeout(() => {
            if (modalViewer.contentDocument && modalViewer.contentDocument.readyState === 'complete') {
                modalLoading.style.display = 'none';
                modalViewer.style.display = 'block';
            }
        }, 500);
    }
    
    // body 스크롤 방지
    document.body.style.overflow = 'hidden';
}

// PDF 다운로드 함수 (HTML을 PDF로 변환하여 다운로드)
window.downloadPdf = function(filePath, fileName) {
    console.log(`PDF 다운로드 시도: ${fileName}, 경로: ${filePath}`);
    
    if (filePath.startsWith('blob:')) {
        // Blob URL인 경우 HTML 내용을 가져와서 PDF로 변환
        fetch(filePath)
            .then(response => response.text())
            .then(htmlContent => {
                // HTML을 PDF로 변환하는 함수 호출
                convertHtmlToPdf(htmlContent, fileName);
            })
            .catch(error => {
                console.error('HTML 내용 가져오기 오류:', error);
                alert('PDF 다운로드 중 오류가 발생했습니다.');
            });
    } else {
        // 일반 파일 경로인 경우
        const downloadLink = document.createElement('a');
        downloadLink.href = filePath;
        downloadLink.download = fileName || 'document.pdf';
        
        // 다운로드 실행
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
        
        console.log(`PDF 다운로드 완료: ${fileName}`);
    }
}

// HTML을 PDF로 변환하는 함수
function convertHtmlToPdf(htmlContent, fileName) {
    try {
        // 라이브러리 로딩 확인 (더 정확한 체크)
        if (typeof html2canvas === 'undefined' || typeof window.jsPDF === 'undefined') {
            console.warn('PDF 변환 라이브러리가 로드되지 않았습니다. HTML 파일로 다운로드합니다.');
            console.log('html2canvas:', typeof html2canvas);
            console.log('jsPDF:', typeof window.jsPDF);
            downloadAsHtml(htmlContent, fileName);
            return;
        }
        
        // 임시 div 생성하여 HTML 렌더링
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = htmlContent;
        tempDiv.style.position = 'absolute';
        tempDiv.style.left = '-9999px';
        tempDiv.style.top = '-9999px';
        tempDiv.style.width = '210mm'; // A4 너비
        tempDiv.style.backgroundColor = 'white';
        document.body.appendChild(tempDiv);
        
        // html2canvas로 캔버스 생성
        html2canvas(tempDiv, {
            scale: 2,
            useCORS: true,
            allowTaint: true,
            backgroundColor: '#ffffff'
        }).then(canvas => {
            // 임시 div 제거
            document.body.removeChild(tempDiv);
            
            // jsPDF로 PDF 생성
            const imgData = canvas.toDataURL('image/png');
            const pdf = new window.jsPDF('p', 'mm', 'a4');
            
            const imgWidth = 210; // A4 너비
            const pageHeight = 295; // A4 높이
            const imgHeight = (canvas.height * imgWidth) / canvas.width;
            let heightLeft = imgHeight;
            
            let position = 0;
            
            // 첫 페이지 추가
            pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
            heightLeft -= pageHeight;
            
            // 여러 페이지가 필요한 경우
            while (heightLeft >= 0) {
                position = heightLeft - imgHeight;
                pdf.addPage();
                pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
                heightLeft -= pageHeight;
            }
            
            // PDF 다운로드
            const pdfFileName = fileName.replace('.html', '.pdf');
            pdf.save(pdfFileName);
            
            console.log(`PDF 다운로드 완료: ${pdfFileName}`);
            console.log(`다운로드 경로: 브라우저 기본 다운로드 폴더`);
            
        }).catch(error => {
            console.error('PDF 변환 오류:', error);
            document.body.removeChild(tempDiv);
            // PDF 변환 실패 시 HTML로 다운로드
            downloadAsHtml(htmlContent, fileName);
        });
        
    } catch (error) {
        console.error('PDF 변환 중 오류:', error);
        // PDF 변환 실패 시 HTML로 다운로드
        downloadAsHtml(htmlContent, fileName);
    }
}

// HTML 파일로 다운로드하는 함수 (fallback) - 자동 인쇄 다이얼로그 열기
function downloadAsHtml(htmlContent, fileName) {
    // HTML에 인쇄 스타일 추가
    const printStyles = `
        <style>
            @media print {
                body { margin: 0; padding: 0; }
                .no-print { display: none !important; }
                @page { margin: 0.5in; size: A4; }
            }
        </style>
    `;
    
    // 인쇄용 HTML 생성
    const printHtml = `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>${fileName}</title>
            ${printStyles}
        </head>
        <body>
            ${htmlContent}
            <script>
                // 페이지 로드 후 자동으로 인쇄 다이얼로그 열기
                window.onload = function() {
                    setTimeout(function() {
                        window.print();
                    }, 500);
                };
            </script>
        </body>
        </html>
    `;
    
    // 새 창에서 HTML 열기
    const printWindow = window.open('', '_blank');
    printWindow.document.write(printHtml);
    printWindow.document.close();
    
    console.log(`HTML 파일을 새 창에서 열고 자동 인쇄 다이얼로그를 표시합니다: ${fileName}`);
    console.log(`인쇄 다이얼로그에서 "PDF로 저장" 또는 "Microsoft Print to PDF"를 선택하세요.`);
}

// PDF 모달 닫기 함수
function closePdfModal() {
    const modal = document.getElementById('pdfModal');
    const modalViewer = document.getElementById('pdfModalViewer');
    
    if (modal) {
        modal.style.display = 'none';
    }
    
    if (modalViewer) {
        modalViewer.src = '';
        modalViewer.style.display = 'none';
    }
    
    // body 스크롤 복원
    document.body.style.overflow = '';
    
    // 전체화면 모드 해제
    const modalContent = document.querySelector('.pdf-modal-content');
    const expandIcon = document.querySelector('#pdfModalExpand i');
    
    if (modalContent) {
        modalContent.classList.remove('fullscreen');
    }
    
    if (modal) {
        modal.classList.remove('fullscreen');
    }
    
    if (expandIcon) {
        expandIcon.className = 'bi bi-arrows-angle-expand';
    }
}

// PDF 모달 전체화면 기능
function initPdfModalFullscreen() {
    const expandBtn = document.getElementById('pdfModalExpand');
    const modalContent = document.querySelector('.pdf-modal-content');
    const modal = document.getElementById('pdfModal');
    const expandIcon = expandBtn?.querySelector('i');
    
    if (!expandBtn || !modalContent || !expandIcon || !modal) return;
    
    let isFullscreen = false;
    
    expandBtn.addEventListener('click', function() {
        isFullscreen = !isFullscreen;
        
        if (isFullscreen) {
            // 전체화면 모드
            modal.classList.add('fullscreen');
            modalContent.classList.add('fullscreen');
            expandIcon.className = 'bi bi-arrows-angle-contract';
            document.body.style.overflow = 'hidden';
        } else {
            // 일반 모드
            modal.classList.remove('fullscreen');
            modalContent.classList.remove('fullscreen');
            expandIcon.className = 'bi bi-arrows-angle-expand';
            document.body.style.overflow = '';
        }
    });
    
    // ESC 키로 전체화면 해제
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && isFullscreen) {
            isFullscreen = false;
            modal.classList.remove('fullscreen');
            modalContent.classList.remove('fullscreen');
            expandIcon.className = 'bi bi-arrows-angle-expand';
            document.body.style.overflow = '';
        }
    });
}

// PDF 모달 초기화
function initPdfModal() {
    initPdfModalFullscreen();
    
    const closeBtn = document.getElementById('pdfModalClose');
    const modal = document.getElementById('pdfModal');
    const overlay = document.querySelector('.pdf-modal-overlay');
    
    if (closeBtn) {
        closeBtn.addEventListener('click', closePdfModal);
    }
    
    if (overlay) {
        overlay.addEventListener('click', closePdfModal);
    }
    
    // ESC 키로 모달 닫기
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.style.display !== 'none') {
            closePdfModal();
        }
    });
}

// DOM 로드 완료 후 초기화
document.addEventListener('DOMContentLoaded', function() {
    initPdfModal();
});

// 전역 함수로 내보내기 (다른 스크립트에서 사용할 수 있도록)
window.openPdfPopup = openPdfPopup;
window.closePdfModal = closePdfModal;
window.initPdfModal = initPdfModal;
window.downloadPdf = downloadPdf;
