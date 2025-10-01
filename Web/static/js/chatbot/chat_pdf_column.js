/**
 * Chat PDF Column JavaScript
 * PDF 참조 컬럼의 상호작용 기능을 담당
 */

class ChatPDFColumn {
    constructor() {
        this.currentPDFs = [];
        this.activePDFId = null;
        this.references = [];
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadSampleData();
    }

    bindEvents() {
        // PDF 업로드 섹션 클릭
        const pdfUploadSection = document.querySelector('.pdf_upload_section');
        if (pdfUploadSection) {
            pdfUploadSection.addEventListener('click', () => {
                this.openPDFUpload();
            });
        }

        // PDF 검색 섹션 클릭
        const pdfSearchSection = document.querySelector('.pdf_search_section');
        if (pdfSearchSection) {
            pdfSearchSection.addEventListener('click', () => {
                this.openPDFSearch();
            });
        }

        // 현재 PDF 닫기 버튼들
        const pdfCloseBtns = document.querySelectorAll('.pdf_actions .action_icon');
        pdfCloseBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const pdfItem = e.target.closest('.current_pdf_item');
                const pdfId = pdfItem.dataset.pdfId;
                this.closePDF(pdfId);
            });
        });

        // PDF 항목 클릭 (활성화)
        const pdfItems = document.querySelectorAll('.current_pdf_item');
        pdfItems.forEach(item => {
            item.addEventListener('click', (e) => {
                // 닫기 버튼 클릭이 아닌 경우에만 활성화
                if (!e.target.closest('.pdf_actions')) {
                    const pdfId = item.dataset.pdfId;
                    this.setActivePDF(pdfId);
                }
            });
        });

        // 참조 항목 클릭
        const referenceItems = document.querySelectorAll('.reference_item');
        referenceItems.forEach(item => {
            item.addEventListener('click', () => {
                this.selectReference(item);
                
                // 메시지 ID가 있으면 해당 메시지로 스크롤
                const messageId = item.getAttribute('data-message-id');
                if (messageId && window.scrollToMessage) {
                    window.scrollToMessage(messageId);
                }
            });
        });

        // 참조 항목 액션 버튼
        const referenceActions = document.querySelectorAll('.reference_actions .action_icon');
        referenceActions.forEach(action => {
            action.addEventListener('click', (e) => {
                e.stopPropagation();
                this.viewReferencePage(action.closest('.reference_item'));
            });
        });

        // PDF 뷰어 열기
        const pdfViewerSection = document.querySelector('.pdf_viewer_section');
        if (pdfViewerSection) {
            pdfViewerSection.addEventListener('click', () => {
                this.openPDFViewer();
            });
        }

        // 문서 관리
        const pdfManagementSection = document.querySelector('.pdf_management_section');
        if (pdfManagementSection) {
            pdfManagementSection.addEventListener('click', () => {
                this.openPDFManagement();
            });
        }

        // 키보드 단축키
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey) {
                switch (e.key) {
                    case 'u':
                        e.preventDefault();
                        this.openPDFUpload();
                        break;
                    case 'f':
                        e.preventDefault();
                        this.openPDFSearch();
                        break;
                }
            }
        });
    }

    loadSampleData() {
        // 샘플 데이터 로드 (실제 구현에서는 API 호출)
        this.currentPDFs = [
            {
                id: 'pdf_001',
                name: 'KB국민은행 대출상품 가이드.pdf',
                pages: 24,
                active: true
            },
            {
                id: 'pdf_002',
                name: 'KB국민은행 신용카드 상품안내.pdf',
                pages: 18,
                active: false
            }
        ];

        this.activePDFId = 'pdf_001';
    }

    setActivePDF(pdfId) {
        // 활성 PDF 설정
        console.log('활성 PDF 설정:', pdfId);
        
        this.activePDFId = pdfId;
        
        // 모든 PDF 아이템에서 active 클래스 제거
        const allPDFItems = document.querySelectorAll('.current_pdf_item');
        allPDFItems.forEach(item => {
            item.classList.remove('active');
        });
        
        // 선택된 PDF 아이템에 active 클래스 추가
        const selectedItem = document.querySelector(`[data-pdf-id="${pdfId}"]`);
        if (selectedItem) {
            selectedItem.classList.add('active');
        }
        
        // 데이터 업데이트
        this.currentPDFs.forEach(pdf => {
            pdf.active = pdf.id === pdfId;
        });
    }

    closePDF(pdfId) {
        // 특정 PDF 닫기
        console.log('PDF 닫기:', pdfId);
        
        const pdfItem = document.querySelector(`[data-pdf-id="${pdfId}"]`);
        if (pdfItem) {
            pdfItem.remove();
        }
        
        // PDF 목록에서 제거
        this.currentPDFs = this.currentPDFs.filter(pdf => pdf.id !== pdfId);
        
        // PDF 개수 업데이트
        this.updatePdfCount();
        
        // 활성 PDF가 닫힌 경우 다른 PDF를 활성화
        if (this.activePDFId === pdfId) {
            if (this.currentPDFs.length > 0) {
                this.setActivePDF(this.currentPDFs[0].id);
            } else {
                this.activePDFId = null;
            }
        }
    }
    
    updatePdfCount() {
        const currentPdfsList = document.querySelector('.current_pdfs_list');
        const pdfCountElement = document.querySelector('.pdf_count');
        
        if (currentPdfsList && pdfCountElement) {
            const pdfItems = currentPdfsList.querySelectorAll('.current_pdf_item');
            const count = pdfItems.length;
            pdfCountElement.textContent = `${count}개`;
            console.log('PDF 개수 업데이트:', count);
        }
    }

    selectReference(item) {
        // 참조 항목 선택
        const referenceId = item.dataset.referenceId;
        console.log('참조 항목 선택:', referenceId);
        
        // 모든 참조 항목에서 active 클래스 제거
        document.querySelectorAll('.reference_item').forEach(ref => {
            ref.classList.remove('active');
        });
        
        // 선택된 항목에 active 클래스 추가
        item.classList.add('active');
    }

    viewReferencePage(item) {
        // 참조 페이지 보기
        const referenceId = item.dataset.referenceId;
        console.log('페이지 보기:', referenceId);
        
        // 실제 구현에서는 PDF 뷰어에서 해당 페이지를 표시
        this.openPDFViewer();
    }

    openPDFUpload() {
        // PDF 업로드 모달 또는 파일 선택 다이얼로그 열기
        console.log('PDF 업로드 열기');
        
        // 실제 구현에서는 파일 업로드 다이얼로그를 열거나 모달을 표시
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.pdf';
        input.onchange = (e) => {
            const file = e.target.files[0];
            if (file) {
                this.uploadPDF(file);
            }
        };
        input.click();
    }

    openPDFSearch() {
        // PDF 검색 기능 열기
        console.log('PDF 검색 열기');
        
        // 실제 구현에서는 검색 모달이나 인라인 검색을 표시
        const searchTerm = prompt('검색할 내용을 입력하세요:');
        if (searchTerm) {
            this.searchInPDF(searchTerm);
        }
    }

    openPDFViewer(pageNumber = null) {
        // PDF 뷰어 열기
        console.log('PDF 뷰어 열기', pageNumber ? `페이지 ${pageNumber}` : '');
        
        // 실제 구현에서는 PDF 뷰어 모달이나 새 창을 열고
        // 지정된 페이지로 이동
        if (pageNumber) {
            // 특정 페이지로 이동
            console.log(`페이지 ${pageNumber}로 이동`);
        }
    }

    openPDFManagement() {
        // 문서 관리 열기
        console.log('문서 관리 열기');
        
        // 실제 구현에서는 문서 관리 모달이나 페이지를 열기
    }

    async uploadPDF(file) {
        console.log('PDF 업로드 시작:', file.name);
        
        // 파일 검증
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            alert('PDF 파일만 업로드 가능합니다.');
            return;
        }
        
        if (file.size > 10 * 1024 * 1024) { // 10MB 제한
            alert('파일 크기는 10MB를 초과할 수 없습니다.');
            return;
        }
        
        // FormData 생성
        const formData = new FormData();
        formData.append('document', file);
        
        try {
            // 업로드 진행 상태 표시
            this.showUploadProgress(file.name);
            
            // 서버에 파일 업로드
            const response = await fetch('/kb_bank/document/api/upload/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                console.log('PDF 업로드 성공:', result);
                
                // 업로드된 PDF를 UI에 추가
                this.addUploadedPDF({
                    name: result.file_name,
                    url: result.file_url,
                    size: result.file_size,
                    uploadDate: new Date().toISOString()
                });
                
                // 성공 메시지 표시
                this.showUploadSuccess(file.name);
                
            } else {
                console.error('PDF 업로드 실패:', result.message);
                alert('PDF 업로드 실패: ' + result.message);
            }
            
        } catch (error) {
            console.error('PDF 업로드 오류:', error);
            alert('PDF 업로드 중 오류가 발생했습니다: ' + error.message);
        } finally {
            // 업로드 진행 상태 숨기기
            this.hideUploadProgress();
        }
    }
    
    showUploadProgress(fileName) {
        // 업로드 진행 상태 표시 로직
        const progressContainer = document.querySelector('.upload_progress_container');
        if (progressContainer) {
            progressContainer.style.display = 'block';
            const progressText = progressContainer.querySelector('.upload_progress_text');
            if (progressText) {
                progressText.textContent = `${fileName} 업로드 중...`;
            }
        }
    }
    
    hideUploadProgress() {
        // 업로드 진행 상태 숨기기
        const progressContainer = document.querySelector('.upload_progress_container');
        if (progressContainer) {
            progressContainer.style.display = 'none';
        }
    }
    
    showUploadSuccess(fileName) {
        // 성공 메시지 표시
        const successMessage = document.createElement('div');
        successMessage.className = 'upload_success_message';
        successMessage.textContent = `${fileName} 업로드 완료!`;
        successMessage.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #10b981;
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
        `;
        
        document.body.appendChild(successMessage);
        
        // 3초 후 자동 제거
        setTimeout(() => {
            successMessage.remove();
        }, 3000);
    }
    
    addUploadedPDF(pdfInfo) {
        // 업로드된 PDF를 UI에 추가
        const currentPdfsList = document.querySelector('.current_pdfs_list');
        if (currentPdfsList) {
            const newPdfItem = document.createElement('div');
            newPdfItem.className = 'current_pdf_item uploaded_pdf';
            newPdfItem.setAttribute('data-pdf-url', pdfInfo.url);
            newPdfItem.innerHTML = `
                <div class="pdf_thumbnail">
                    <i class="bi bi-file-earmark-pdf"></i>
                </div>
                <div class="pdf_info">
                    <div class="pdf_name">${pdfInfo.name}</div>
                    <div class="pdf_pages">업로드됨</div>
                </div>
                <div class="pdf_actions">
                    <div class="action_icon">
                        <i class="bi bi-x"></i>
                    </div>
                </div>
            `;
            
            // PDF 아이템 클릭 이벤트 추가
            newPdfItem.addEventListener('click', function(e) {
                if (!e.target.closest('.pdf_actions')) {
                    const filePath = this.getAttribute('data-pdf-url');
                    if (filePath) {
                        // S3 URL에서 파일 경로 추출
                        const urlParts = filePath.split('/');
                        const fileName = urlParts[urlParts.length - 1];
                        openPdfPopup(fileName, pdfInfo.name);
                    }
                }
            });
            
            // X 버튼 클릭 이벤트 추가
            const closeButton = newPdfItem.querySelector('.action_icon');
            closeButton.addEventListener('click', function(e) {
                e.stopPropagation();
                newPdfItem.remove();
            });
            
            currentPdfsList.appendChild(newPdfItem);
        }
    }
    
    getCSRFToken() {
        // CSRF 토큰 가져오기
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfToken ? csrfToken.value : '';
    }

    searchInPDF(searchTerm) {
        console.log('PDF 검색:', searchTerm);
        
        // 실제 구현에서는 서버에 검색 요청을 보내고
        // 결과를 받아와서 UI에 표시
    }
}

// DOM이 로드된 후 초기화
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing Chat PDF Column');
    window.chatPDFColumn = new ChatPDFColumn();
});

// 전역에서 접근 가능하도록 export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChatPDFColumn;
}
