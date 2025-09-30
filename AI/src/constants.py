# 카테고리/라벨 상수 및 정규화 유틸

# 메인 카테고리
MAIN_LAW = "법률"
MAIN_RULE = "내규"
MAIN_PRODUCT = "상품"

# 서브 카테고리(표준 표기: 공백 포함)
SUB_COMMON = "공통"
SUB_RULE_BANK = "국민은행"

# 상품 서브(요청 사양: 밑줄 대신 공백)
SUB_PRODUCT_MORTGAGE = "개인 담보 전세대출"
SUB_PRODUCT_PERSONAL = "개인 신용대출"
SUB_PRODUCT_AUTO = "개인 자동차 대출"
SUB_PRODUCT_HOUSING_FUND = "개인 주택도시기금대출"
SUB_PRODUCT_CORP = "기업 대출"

# 라벨 정규화(밑줄/공백 혼용 수용)
ALIASES = {
    "개인_담보_전세대출": SUB_PRODUCT_MORTGAGE,
    "개인_신용대출": SUB_PRODUCT_PERSONAL,
    "개인_자동차_대출": SUB_PRODUCT_AUTO,
    "개인_자동차대출": SUB_PRODUCT_AUTO,
    "개인_주택도시기금대출": SUB_PRODUCT_HOUSING_FUND,
    "기업_대출": SUB_PRODUCT_CORP,
    "기업대출": SUB_PRODUCT_CORP,
}

def normalize_sub_label(label: str) -> str:
    if not label:
        return SUB_COMMON
    label = label.strip()
    return ALIASES.get(label, label)


# API 응답 상태
STATUS_SUCCESS = "successful"
STATUS_FAIL = "fail"


# 메타데이터 키워드 (컨텐츠 기반 태그)
KEYWORDS_INTEREST_RATE = ["금리", "이자"]
KEYWORDS_CONDITIONS = ["조건", "요건"]
KEYWORDS_APPLICATION = ["신청", "접수"]
KEYWORDS_POLICY = ["정책", "규정"]
KEYWORDS_ETHICS = ["윤리", "준수"]

# 파일 확장자
ALLOWED_EXTENSIONS = {".pdf", ".csv"}
PDF_EXT = ".pdf"
CSV_EXT = ".csv"


# 데이터 폴더 관련
DATA_FOLDER_NAME = "SKN14-Final-3Team-Data"

# 메타데이터 기본값
METADATA_DOCUMENT_CATEGORY_REGULATION = "regulation"
METADATA_DOCUMENT_CATEGORY_PRODUCT = "product"
METADATA_DOCUMENT_CATEGORY_UPLOADED = "uploaded"

METADATA_SUBCATEGORY_LAW = "law"
METADATA_SUBCATEGORY_CREDIT_POLICY = "credit_policy"
METADATA_SUBCATEGORY_BANKING_PRODUCT = "banking_product"
METADATA_SUBCATEGORY_USER_UPLOAD = "user_upload"

METADATA_BUSINESS_UNIT_COMPLIANCE = "compliance"
METADATA_BUSINESS_UNIT_CREDIT = "credit"
METADATA_BUSINESS_UNIT_RETAIL_BANKING = "retail_banking"
METADATA_BUSINESS_UNIT_GENERAL = "general"

METADATA_PRODUCT_TYPE_MORTGAGE = "mortgage"
METADATA_PRODUCT_TYPE_PERSONAL_LOAN = "personal_loan"
METADATA_PRODUCT_TYPE_AUTO_LOAN = "auto_loan"
METADATA_PRODUCT_TYPE_HOUSING_FUND = "housing_fund"
METADATA_PRODUCT_TYPE_BUSINESS_LOAN = "business_loan"

METADATA_TARGET_CUSTOMER_INDIVIDUAL = "individual"
METADATA_TARGET_CUSTOMER_CORPORATE = "corporate"

# 텍스트 스플리터 설정
TEXT_SPLITTER_SEPARATORS = ["\n\n", "\n", ".", "!", "?"]


# Orchestrator 관련 상수
GENERAL_FAQ_CATEGORY = "general_banking_FAQs"
COMPANY_PRODUCTS_CATEGORY = "company_products"
COMPANY_RULES_CATEGORY = "company_rules"
INDUSTRY_POLICY_CATEGORY = "industry_policies_and_regulations"

NO_ANSWER_MSG = "해당 정보를 찾을 수 없습니다."
