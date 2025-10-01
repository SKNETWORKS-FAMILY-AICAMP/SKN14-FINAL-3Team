# KB FinAIssist 프로젝트 설정 가이드

## 🚀 다른 환경에서 프로젝트 설정 순서

### 1. **프로젝트 클론/다운로드**
```bash
# Git에서 클론하는 경우
git clone [저장소 URL]
cd SKN14-Final-3Team-Web

# 또는 압축 파일로 다운로드한 경우
# 압축 해제 후 해당 폴더로 이동
```

### 2. **Python 가상환경 설정**
```bash
# 가상환경 생성
python -m venv .venv

# 가상환경 활성화
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

### 3. **Python 패키지 설치**
```bash
# Django 및 기타 패키지 설치
pip install -r requirements.txt
```

### 4. **Node.js 및 Sass 설치**
```bash
# Node.js가 설치되어 있지 않은 경우
# https://nodejs.org/ 에서 Node.js 다운로드 및 설치

# npm 패키지 설치 (Sass 포함)
npm install
```

### 5. **데이터베이스 설정**
```bash
# 만들어진 DB가 없는 경우
# 마이그레이션 실행
python manage.py makemigrations
python manage.py migrate f_user
python manage.py migrate

# 이미 만들어진 DB가 있는 경우
# setup.sql에서 아래 코드 먼저 실행
# DB 초기화(setup.sql 코드)
DROP DATABASE finaissistdb;

# DB안에 table 하나도 없는 것 확인(setup.sql 코드)
use finaissistdb;
show tables;

# f_user 보다 먼저 들어간 게 있으면 삭제(setup.sql 코드)
DELETE FROM django_migrations WHERE app='f_chatbot';
DELETE FROM django_migrations WHERE app='f_calendar';
DELETE FROM django_migrations WHERE app='f_todo';
DELETE FROM django_migrations WHERE app='f_document';

# DB안에 아무것도 없는거 확인한 후 아래 코드 실행
python manage.py makemigrations
python manage.py migrate f_user
python manage.py migrate

```

## 📝 환경 변수 설정 (선택사항)

MySQL을 사용하려면 `.env` 파일 생성:
```env
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
```
# 더미 데이터 만들기
```
python manage.py seed_all2
```

### 6. **SCSS 자동 컴파일 설정**

#### 방법 1: 터미널에서 직접 실행 (권장)
```bash
# 새 터미널에서 실행 (가상환경 활성화 후)
npx sass static/scss:static/css --watch --style=expanded
```

#### 방법 2: VS Code/Cursor Live Sass Compiler 확장 사용
1. **"Live Sass Compiler" 확장 설치**
2. **설정 추가** (`Ctrl + Shift + P` → "Preferences: Open Settings (JSON)"):
```json
{
    "liveSassCompile.settings.formats": [
        {
            "format": "expanded",
            "extensionName": ".css",
            "savePath": "~/../css/"
        }
    ],
    "liveSassCompile.settings.generateMap": true,
    "liveSassCompile.settings.includeItems": [
        "/scss/**/*.scss"
    ],
    "liveSassCompile.settings.excludeList": [
        "/node_modules/**",
        "/.vscode/**"
    ]
}
```
3. **SCSS 파일 열기 후 "Watch Sass" 버튼 클릭**

#### 방법 3: npm 스크립트 사용
```bash
# package.json에 정의된 스크립트 실행
npm run sass-watch
```

### 7. **Django 서버 실행**
```bash
# 또 다른 새 터미널에서 실행 (가상환경 활성화 후)
python manage.py runserver
```

## 📋 필요한 사전 설치 항목

### 필수:
- **Python 3.8+**
- **Node.js 14+** (SCSS 컴파일용)
- **Git** (클론용)

### 선택사항:
- **MySQL** (프로덕션용, 개발환경에서는 SQLite 사용)

## 🔧 환경별 차이점

### Windows:
```bash
# 가상환경 활성화
.venv\Scripts\activate

# PowerShell 실행 정책 문제 시
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 배치 파일 실행 시
.\filename.bat
```

### macOS/Linux:
```bash
# 가상환경 활성화
source .venv/bin/activate

# 권한 문제 시
chmod +x .venv/bin/activate
```



## 🎯 최종 확인

모든 설정이 완료되면:
1. **브라우저에서** `http://127.0.0.1:8000/login/` 접속
2. **KB국민은행 로그인 페이지** 확인
3. **SCSS 수정 시 자동 컴파일** 확인

## 🛠️ 개발 워크플로우

### SCSS 개발:
1. **SCSS 파일 수정** (`static/scss/` 폴더)
2. **자동 컴파일 확인** (`static/css/` 폴더에 CSS 파일 생성)
3. **브라우저에서 실시간 확인**

**주의사항:**
- SCSS 파일 수정 시 watching이 활성화되어 있는지 확인
- CSS 파일이 `static/scss/` 폴더에 생성되면 설정 오류
- 올바른 경로: `static/css/` 폴더에 생성되어야 함

### Django 개발:
1. `templates/` 폴더에서 HTML 파일 수정
2. `f_*/views.py`에서 뷰 로직 수정
3. `f_*/urls.py`에서 URL 패턴 수정

## 📁 프로젝트 구조

```
SKN14-Final-3Team-Web/
├── static/
│   ├── scss/              # SCSS 소스 파일
│   │   ├── _variables.scss
│   │   ├── _mixins.scss
│   │   └── login.scss
│   ├── css/               # 컴파일된 CSS 파일
│   │   ├── login.css
│   │   └── login.css.map
│   └── js/                # JavaScript 파일
├── templates/             # HTML 템플릿
│   └── login/
│       └── login.html
├── f_login/              # 로그인 앱
├── f_user/               # 사용자 앱
├── f_common/             # 공통 앱
├── KB_FinAIssist/        # Django 프로젝트 설정
├── requirements.txt      # Python 패키지 목록
├── package.json          # Node.js 패키지 목록
└── manage.py            # Django 관리 스크립트
```

## 🚨 문제 해결

### Django 모듈을 찾을 수 없는 경우:
```bash
# 가상환경이 활성화되었는지 확인
# Windows: (.venv)가 프롬프트 앞에 표시되어야 함
# macOS/Linux: (.venv)가 프롬프트 앞에 표시되어야 함

# 가상환경 재활성화
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
```

### Sass 컴파일 오류:
```bash
# Node.js 버전 확인
node --version

# npm 패키지 재설치
rm -rf node_modules package-lock.json
npm install

# PowerShell 실행 정책 문제 시 (Windows)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 수동 컴파일 테스트
npx sass static/scss/login.scss static/css/login.css --style=expanded
```

### Live Sass Compiler 확장 문제:
1. **"Watch Sass" 버튼이 보이지 않는 경우:**
   - `Ctrl + Shift + P` → "Live Sass: Watch Sass" 검색
   - 확장이 설치되어 있는지 확인

2. **설정 오류 시:**
   - `settings.json`에서 경로 구분자 확인 (`/`로 시작해야 함)
   - VS Code/Cursor 재시작

3. **CSS 파일이 scss 폴더에 생성되는 경우:**
   - `savePath` 설정 확인: `"~/../css/"`
   - 올바른 경로로 수정 후 재시작

### 데이터베이스 오류:
```bash
# SQLite 사용 (기본 설정)
# MySQL 사용 시 .env 파일 설정 확인
```

## 📚 추가 리소스

- [Django 공식 문서](https://docs.djangoproject.com/)
- [Sass 공식 문서](https://sass-lang.com/)
- [Node.js 공식 문서](https://nodejs.org/docs/)

---

이 가이드를 따라하면 어떤 환경에서든 프로젝트를 성공적으로 설정할 수 있습니다! 🎉
