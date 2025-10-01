// ========================================
// KB국민은행 직원 업무시스템 로그인 페이지 JavaScript
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    // ========================================
    // 1. DOM 요소 선택 (변수 선언)
    // ========================================
    const saveIdCheckbox = document.querySelector('input[name="save_id"]');
    const saveAdminIdCheckbox = document.querySelector('input[name="save_admin_id"]');
    const employeeIdInput = document.querySelector('input[name="employee_id"]');
    const passwordInput = document.querySelector('input[name="password"]');
    const adminIdInput = document.querySelector('input[name="admin_id"]');
    const adminPasswordInput = document.querySelector('input[name="admin_password"]');
    const loginForm = document.querySelector('.login-form');
    const adminLoginForm = document.querySelector('#admin form');

    // ========================================
    // 2. 초기화 함수
    // ========================================
    function clearAllInputs() {
        if (employeeIdInput) employeeIdInput.value = '';
        if (passwordInput) passwordInput.value = '';
        if (adminIdInput) adminIdInput.value = '';
        if (adminPasswordInput) adminPasswordInput.value = '';
        if (saveIdCheckbox) saveIdCheckbox.checked = false;
        if (saveAdminIdCheckbox) saveAdminIdCheckbox.checked = false;
    }
    
    // ========================================
    // 3. 공통 유틸리티 함수들
    // ========================================
    
    // ID 저장/불러오기 설정
    function setupIdStorage(inputElement, checkboxElement, storageKey) {
        // 저장된 ID 불러오기
        if (localStorage.getItem(storageKey)) {
            if (inputElement) inputElement.value = localStorage.getItem(storageKey);
            if (checkboxElement) checkboxElement.checked = true;
        }
        
        // 체크박스 변경 시 저장/삭제
        checkboxElement.addEventListener('change', function() {
            if (this.checked) {
                localStorage.setItem(storageKey, inputElement.value);
            } else {
                localStorage.removeItem(storageKey);
            }
        });

        // 입력 시 자동 저장
        inputElement.addEventListener('input', function() {
            if (checkboxElement.checked) {
                localStorage.setItem(storageKey, this.value);
            }
        });
    }

    // 입력 필드 에러 제거 설정
    function setupInputErrorClear(inputElement, hideErrorFunction) {
        inputElement.addEventListener('input', function() {
            if (this.value.trim() && this.value.length > 0) {
                clearFieldError(this);
                hideErrorFunction();
            }
        });
    }

    // 로딩 상태 표시 (내부 함수)
    function showLoading() {
        const activeTab = document.querySelector('.nav-link.active');
        let loginBtn;
        
        if (activeTab && activeTab.getAttribute('data-bs-target') === '#admin') {
            loginBtn = document.querySelector('#admin button[type="submit"]');
        } else {
            loginBtn = document.querySelector('.login-form button[type="submit"]');
        }
        
        if (loginBtn) {
            loginBtn.disabled = true;
            loginBtn.innerHTML = '<span>로그인 중...</span>';
        }
    }

    // 필드 에러 표시 (내부 함수)
    function showFieldError(message, inputElement, errorElementId = 'loginError', secondInputElement = null) {
        const errorElement = document.getElementById(errorElementId);
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.style.display = 'inline-block';
        }
        
        inputElement.classList.add('error');
        if (secondInputElement) {
            secondInputElement.classList.add('error');
        }
        
        setTimeout(() => {
            inputElement.classList.remove('error');
            if (secondInputElement) {
                secondInputElement.classList.remove('error');
            }
        }, 500);
    }

    // 필드 에러 제거 (내부 함수)
    function clearFieldError(inputElement) {
        inputElement.classList.remove('error');
    }

    // 로그인 폼 검증
    function validateLoginForm(idInput, passwordInput, errorMessages, errorElementId) {
        const idEmpty = !idInput.value.trim();
        const passwordEmpty = !passwordInput.value.trim();
        let hasError = false;
        
        // 에러 메시지 숨기기
        const errorElement = document.getElementById(errorElementId);
        if (errorElement) errorElement.style.display = 'none';
        
        // 검증 로직
        if (idEmpty && passwordEmpty) {
            showFieldError(errorMessages.both, idInput, errorElementId, passwordInput);
            hasError = true;
        } else if (idEmpty) {
            showFieldError(errorMessages.id, idInput, errorElementId);
            clearFieldError(passwordInput);
            hasError = true;
        } else if (passwordEmpty) {
            showFieldError(errorMessages.password, passwordInput, errorElementId);
            clearFieldError(idInput);
            hasError = true;
        } else {
            clearFieldError(idInput);
            clearFieldError(passwordInput);
        }
        
        return hasError;
    }

    // ========================================
    // 4. 초기화 실행
    // ========================================
    clearAllInputs();
    
    // ID 저장 기능 설정
    setupIdStorage(employeeIdInput, saveIdCheckbox, 'savedEmployeeId');
    setupIdStorage(adminIdInput, saveAdminIdCheckbox, 'savedAdminId');

    // 입력 필드 에러 제거 설정
    setupInputErrorClear(employeeIdInput, hideLoginError);
    setupInputErrorClear(passwordInput, hideLoginError);
    setupInputErrorClear(adminIdInput, hideAdminLoginError);
    setupInputErrorClear(adminPasswordInput, hideAdminLoginError);

    // ========================================
    // 5. 이벤트 리스너 설정
    // ========================================
    
    // 직원 로그인 폼 제출
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const hasError = validateLoginForm(
                employeeIdInput, 
                passwordInput, 
                {
                    both: '사번과 비밀번호를 입력하세요.',
                    id: '사번을 입력하세요.',
                    password: '비밀번호를 입력하세요.'
                },
                'loginError'
            );
            
            if (hasError) {
                e.preventDefault();
                return false;
            }
            
            showLoading();
        });
    }

    // 관리자 로그인 폼 제출
    if (adminLoginForm) {
        adminLoginForm.addEventListener('submit', function(e) {
            const hasError = validateLoginForm(
                adminIdInput, 
                adminPasswordInput, 
                {
                    both: '관리자 ID와 비밀번호를 입력하세요.',
                    id: '관리자 ID를 입력하세요.',
                    password: '비밀번호를 입력하세요.'
                },
                'adminLoginError'
            );
            
            if (hasError) {
                e.preventDefault();
                return false;
            }
            
            showLoading();
        });
    }
});

// ========================================
// 전역 함수들 (HTML 템플릿에서 호출 가능)
// ========================================

// ========================================
// 1. 에러 핸들러 관련
// ========================================

// 에러 핸들러 팩토리 함수
function createErrorHandler(errorElementId) {
    return {
        show: function(message) {
            const errorElement = document.getElementById(errorElementId);
            if (errorElement) {
                errorElement.textContent = message;
                errorElement.style.display = 'inline-block';
            }
        },
        hide: function() {
            const errorElement = document.getElementById(errorElementId);
            if (errorElement) {
                errorElement.style.display = 'none';
            }
        }
    };
}

// 에러 핸들러 인스턴스 생성
const loginErrorHandler = createErrorHandler('loginError');
const adminLoginErrorHandler = createErrorHandler('adminLoginError');

// HTML 템플릿 호환성을 위한 래퍼 함수들
function showLoginError(message) {
    loginErrorHandler.show(message);
}

function hideLoginError() {
    loginErrorHandler.hide();
}

function showAdminLoginError(message) {
    adminLoginErrorHandler.show(message);
}

function hideAdminLoginError() {
    adminLoginErrorHandler.hide();
}

// ========================================
// 2. 비밀번호 토글 관련
// ========================================

// 비밀번호 토글 팩토리 함수
function createPasswordToggle(passwordInputId, toggleIconId) {
    return function() {
        const passwordInput = document.getElementById(passwordInputId);
        const toggleIcon = document.getElementById(toggleIconId);
        
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            toggleIcon.className = 'bi bi-eye';
        } else {
            passwordInput.type = 'password';
            toggleIcon.className = 'bi bi-eye-slash';
        }
    };
}

// 비밀번호 토글 함수들 (HTML 템플릿에서 호출)
const togglePassword = createPasswordToggle('password', 'passwordToggleIcon');
const toggleAdminPassword = createPasswordToggle('admin_password', 'adminPasswordToggleIcon');


