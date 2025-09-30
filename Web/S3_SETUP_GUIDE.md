# S3 설정 가이드

챗봇에서 PDF 파일을 S3에서 가져오도록 설정하는 방법입니다.

## 1. AWS S3 버킷 생성

1. AWS 콘솔에 로그인
2. S3 서비스로 이동
3. "버킷 만들기" 클릭
4. 버킷 이름 설정 (예: `kb-finaissist-pdfs`)
5. 리전 선택 (권장: `ap-northeast-2` - 서울)
6. 버킷 생성

## 2. AWS IAM 사용자 생성 및 권한 설정

1. AWS 콘솔에서 IAM 서비스로 이동
2. "사용자" → "사용자 추가" 클릭
3. 사용자 이름 입력 (예: `kb-finaissist-s3-user`)
4. "프로그래밍 방식 액세스" 선택
5. 권한 정책 연결:
   - `AmazonS3FullAccess` (또는 필요한 권한만)
6. 사용자 생성 후 액세스 키 ID와 시크릿 액세스 키 저장

## 3. 환경변수 설정

### 방법 1: .env 파일 생성 (권장)

프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 추가:

```env
# AWS S3 설정
AWS_ACCESS_KEY_ID=your_actual_access_key_id
AWS_SECRET_ACCESS_KEY=your_actual_secret_access_key
AWS_STORAGE_BUCKET_NAME=your_bucket_name
AWS_S3_REGION_NAME=ap-northeast-2
```

### 방법 2: 시스템 환경변수 설정

Windows:
```cmd
set AWS_ACCESS_KEY_ID=your_actual_access_key_id
set AWS_SECRET_ACCESS_KEY=your_actual_secret_access_key
set AWS_STORAGE_BUCKET_NAME=your_bucket_name
set AWS_S3_REGION_NAME=ap-northeast-2
```

Linux/Mac:
```bash
export AWS_ACCESS_KEY_ID=your_actual_access_key_id
export AWS_SECRET_ACCESS_KEY=your_actual_secret_access_key
export AWS_STORAGE_BUCKET_NAME=your_bucket_name
export AWS_S3_REGION_NAME=ap-northeast-2
```

## 4. PDF 파일을 S3에 업로드

기존 로컬 PDF 파일들을 S3 버킷에 업로드해야 합니다.

### AWS CLI 사용 (권장)

1. AWS CLI 설치
2. `aws configure` 실행하여 자격 증명 설정
3. PDF 파일 업로드:

```bash
# 단일 파일 업로드
aws s3 cp "로컬파일경로" "s3://버킷명/대상경로"

# 예시
aws s3 cp "C:\Workspaces\SKN14-Final-3Team\SKN14-Final-3Team-Data\법률\공통\여신금융협회_여신심사_선진화를_위한_가이드라인.pdf" "s3://kb-finaissist-pdfs/법률/공통/여신금융협회_여신심사_선진화를_위한_가이드라인.pdf"

# 전체 디렉토리 업로드
aws s3 sync "C:\Workspaces\SKN14-Final-3Team\SKN14-Final-3Team-Data" "s3://kb-finaissist-pdfs"
```

### AWS 콘솔 사용

1. S3 버킷으로 이동
2. "업로드" 버튼 클릭
3. 파일 또는 폴더 선택하여 업로드

## 5. 설정 확인

```bash
python s3_config.py
```

성공적으로 설정되었다면 "✅ S3 설정이 올바르게 구성되었습니다." 메시지가 표시됩니다.

## 6. 테스트

1. Django 서버 실행
2. 챗봇 페이지로 이동
3. PDF 관련 질문을 하여 PDF 모달이 정상적으로 열리는지 확인

## 주의사항

- AWS 자격 증명은 안전하게 보관하세요
- `.env` 파일은 `.gitignore`에 추가하여 버전 관리에서 제외하세요
- S3 버킷의 권한 설정을 적절히 구성하세요
- 비용을 고려하여 불필요한 파일은 정리하세요
