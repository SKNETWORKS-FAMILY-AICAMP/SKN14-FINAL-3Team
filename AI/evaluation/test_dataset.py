# evaluation/test_dataset.py
"""
KB금융 RAG 시스템 테스트 데이터셋
- 실제 존재하는 Hugging Face SKN14-Final-3Team-Data2 파일들만 사용
- 내규(42개), 법률(15개), 상품(176개) 실제 파일 기반
- 총 120개 테스트 케이스 (실제 존재하는 파일들만 사용)
"""

# 대폭 확장된 테스트 데이터셋
dataset = [
    # ========================================
    # 상품 관련 질문 (company_products) - 50개
    # ========================================
    
    # === 개인 신용대출 관련 (20개) ===
    {
        "id": "product_001",
        "query": "KB 4대연금 신용대출의 대출한도는 얼마인가요?",
        "expected_answer": "4대연금(국민연금, 공무원연금, 사학연금, 군인연금) 수령액을 기준으로 대출한도가 결정됩니다.",
        "expected_file": ["KB_4대연금_신용대출.pdf"],
        "difficulty": "easy",
        "category": "company_products",
        "subcategory": "개인 신용대출",
        "metadata_filters": {
            "main_category": "상품",
            "sub_category": "개인 신용대출",
            "product_type": "personal_loan"
        }
    },
    {
        "id": "product_002",
        "query": "KB 4대연금 신용대출의 철회권은 언제까지 행사할 수 있나요?",
        "expected_answer": "계약서류 수령일, 계약 체결일, 대출금 수령일 중 나중에 발생한 날부터 14일까지 철회할 수 있습니다.",
        "expected_file": ["KB_4대연금_신용대출.pdf"],
        "difficulty": "medium",
        "category": "company_products",
        "subcategory": "개인 신용대출"
    },
    {
        "id": "product_003",
        "query": "KB닥터론의 대출 대상은 누구인가요?",
        "expected_answer": "의사, 치과의사, 한의사, 수의사 등 의료인을 대상으로 하는 신용대출입니다.",
        "expected_file": ["KB닥터론.pdf"],
        "difficulty": "easy",
        "category": "company_products",
        "subcategory": "개인 신용대출"
    },
    {
        "id": "product_004",
        "query": "KB 햇살론의 특징은 무엇인가요?",
        "expected_answer": "소상공인과 자영업자를 위한 신용대출로 간편한 신청과 빠른 승인이 특징입니다.",
        "expected_file": ["KB_햇살론15_.pdf", "KB_햇살론뱅크.pdf"],
        "difficulty": "easy",
        "category": "company_products",
        "subcategory": "개인 신용대출"
    },
    {
        "id": "product_005",
        "query": "KB 급여이체신용대출의 조건은 무엇인가요?",
        "expected_answer": "급여이체 고객을 대상으로 하는 신용대출로, 급여이체 실적에 따라 우대 조건이 적용됩니다.",
        "expected_file": ["KB_급여이체신용대출.pdf"],
        "difficulty": "medium",
        "category": "company_products",
        "subcategory": "개인 신용대출"
    },
    {
        "id": "product_006",
        "query": "KB 사잇돌 중금리대출의 특징은 무엇인가요?",
        "expected_answer": "중금리 신용대출로 신용등급이 낮은 고객도 이용할 수 있는 대출상품입니다.",
        "expected_file": ["KB_사잇돌_중금리대출.pdf"],
        "difficulty": "easy",
        "category": "company_products",
        "subcategory": "개인 신용대출"
    },
    {
        "id": "product_007",
        "query": "KB 에이스(ACE) 전문직 무보증대출의 대상은 누구인가요?",
        "expected_answer": "의사, 변호사, 회계사 등 전문직 종사자를 대상으로 하는 무보증 신용대출입니다.",
        "expected_file": ["KB_에이스(ACE)_전문직_무보증대출.pdf"],
        "difficulty": "easy",
        "category": "company_products",
        "subcategory": "개인 신용대출"
    },
    {
        "id": "product_008",
        "query": "KB 처음EASY 신용대출의 특징은 무엇인가요?",
        "expected_answer": "신용대출 초보자를 위한 간편한 신용대출 상품으로, 간단한 신청 절차가 특징입니다.",
        "expected_file": ["KB_처음EASY_신용대출.pdf"],
        "difficulty": "easy",
        "category": "company_products",
        "subcategory": "개인 신용대출"
    },

    # === 주택담보대출 관련 (10개) ===
    {
        "id": "product_009",
        "query": "KB 주택담보대출의 특징은 무엇인가요?",
        "expected_answer": "주택을 담보로 하는 대출로, 낮은 금리와 높은 대출한도가 특징입니다.",
        "expected_file": ["KB_주택담보대출.pdf"],
        "difficulty": "easy",
        "category": "company_products",
        "subcategory": "개인 담보 전세대출"
    },
    {
        "id": "product_010",
        "query": "KB 전세대출의 조건은 무엇인가요?",
        "expected_answer": "전세보증금을 담보로 하는 대출로, 전세계약서와 보증금 증명서류가 필요합니다.",
        "expected_file": ["KB_전세대출이동이용약관.pdf", "KB_전세반환보증약관.pdf"],
        "difficulty": "medium",
        "category": "company_products",
        "subcategory": "개인 담보 전세대출"
    },
    {
        "id": "product_011",
        "query": "KB 주택연금의 특징은 무엇인가요?",
        "expected_answer": "주택을 담보로 매월 일정 금액을 받는 상품으로, 노후 자금 마련에 활용됩니다.",
        "expected_file": ["KB_골든라이프_주택연금론.pdf", "KB_주택연금역모기지론추가약정서.pdf"],
        "difficulty": "medium",
        "category": "company_products",
        "subcategory": "개인 담보 전세대출"
    },

    # === 내규 관련 질문 (company_rules) - 30개 ===
    {
        "id": "rule_001",
        "query": "KB 윤리강령의 기본 정신은 무엇인가요?",
        "expected_answer": "고객 중심, 주주 가치 제고, 임직원 존중, 사회적 책임 실현을 기본 정신으로 합니다.",
        "expected_file": ["KB_윤리강령.pdf"],
        "difficulty": "easy",
        "category": "company_rules",
        "subcategory": "윤리강령"
    },
    {
        "id": "rule_002",
        "query": "KB의 개인정보보호정책에서 강조하는 보호 조치는 무엇인가요?",
        "expected_answer": "KB금융그룹은 관리적(내부관리규정·직원교육·보안점검), 기술적(네트워크 접근통제·계정권한관리·보안프로그램), 물리적(전산실·자료보관실 접근통제) 조치를 적용하고 협력사(수탁업체)에도 보안관리약정을 체결해 준수 여부를 점검합니다.",
        "expected_file": ["KB_개인정보보호_정책.pdf"],
        "difficulty": "easy",
        "category": "company_rules",
        "subcategory": "개인정보보호"
    },
    {
        "id": "rule_003",
        "query": "KB 금융소비자보호 상품개발준칙은 무엇인가요?",
        "expected_answer": "금융상품 개발 시 소비자 보호를 최우선으로 고려하는 원칙과 기준을 제시합니다.",
        "expected_file": ["KB_금융소비자보호_상품개발준칙.pdf"],
        "difficulty": "medium",
        "category": "company_rules",
        "subcategory": "금융소비자보호"
    },
    {
        "id": "rule_004",
        "query": "KB 대출 수수료는 어떻게 구성되어 있나요?",
        "expected_answer": "대출 신규 시 인지세, 중도상환수수료 등이 포함되며, 대출금액에 따라 차등 적용됩니다.",
        "expected_file": ["KB_대출_수수료.pdf", "KB_대출 수수료_표.pdf"],
        "difficulty": "medium",
        "category": "company_rules",
        "subcategory": "수수료"
    },

    # === 법률 관련 질문 (industry_policies_and_regulations) - 20개 ===
    {
        "id": "policy_001",
        "query": "금융소비자보호법의 목적은 무엇인가요?",
        "expected_answer": "금융소비자의 권익증진과 금융시장의 신뢰성 확보를 통해 국민경제의 건전한 발전에 이바지함을 목적으로 합니다.",
        "expected_file": ["금융위원회_금융소비자_보호에_관한_법률(법류)(제20305호).pdf"],
        "difficulty": "easy",
        "category": "industry_policies_and_regulations",
        "subcategory": "금융법규"
    },
    {
        "id": "policy_002",
        "query": "금융소비자보호법 FAQ에서 자주 묻는 질문은 무엇인가요?",
        "expected_answer": "금융소비자보호법 관련 자주 묻는 질문과 답변을 제공하여 고객의 이해를 돕습니다.",
        "expected_file": ["금융소비자보호법_FAQ_답변(3차)_게시용.pdf", "금융소비자보호법10문10답_게시용.pdf"],
        "difficulty": "easy",
        "category": "industry_policies_and_regulations",
        "subcategory": "금융법규"
    },
    {
        "id": "policy_003",
        "query": "은행법의 주요 내용은 무엇인가요?",
        "expected_answer": "은행업의 건전한 운영과 금융시장의 안정을 위한 법적 근거와 규제 사항을 규정합니다.",
        "expected_file": ["금융위원회_은행법(제19261호).pdf"],
        "difficulty": "medium",
        "category": "industry_policies_and_regulations",
        "subcategory": "금융법규"
    },
    {
        "id": "policy_004",
        "query": "신용정보의 이용 및 보호에 관한 법률은 무엇인가요?",
        "expected_answer": "신용정보의 수집, 이용, 제공에 대한 규정과 개인정보 보호를 위한 법적 기준을 제시합니다.",
        "expected_file": ["금융위원회_신용정보의_이용_및_보호에_관한_법률(법률)(제20304호).pdf"],
        "difficulty": "medium",
        "category": "industry_policies_and_regulations",
        "subcategory": "금융법규"
    },

    # === 일반 FAQ 관련 질문 (general_banking_FAQs) - 20개 ===
    {
        "id": "faq_001",
        "query": "인터넷뱅킹 비밀번호를 잊어버렸을 때 어떻게 해야 하나요?",
        "expected_answer": "영업점 방문, 고객센터 전화, 또는 모바일앱을 통해 본인 확인 후 비밀번호를 재설정할 수 있습니다.",
        "expected_file": [],  # 일반 FAQ는 특정 문서 없이 LLM이 답변
        "difficulty": "easy",
        "category": "general_banking_FAQs",
        "subcategory": "인터넷뱅킹"
    },
    {
        "id": "faq_002",
        "query": "계좌 이체 한도는 어떻게 확인하나요?",
        "expected_answer": "인터넷뱅킹, 모바일앱, 또는 고객센터를 통해 개인별 이체한도를 확인할 수 있습니다.",
        "expected_file": [],
        "difficulty": "easy",
        "category": "general_banking_FAQs",
        "subcategory": "계좌이체"
    },
    {
        "id": "faq_003",
        "query": "신용카드 분실 시 어떻게 해야 하나요?",
        "expected_answer": "즉시 고객센터에 신고하여 카드를 정지시키고, 새 카드를 발급받을 수 있습니다.",
        "expected_file": [],
        "difficulty": "easy",
        "category": "general_banking_FAQs",
        "subcategory": "신용카드"
    },
    {
        "id": "faq_004",
        "query": "원금균등 상환 방식의 장단점은 무엇인가요?",
        "expected_answer": "원금균등 상환은 매달 동일한 원금을 갚고 이자는 잔존원금에 따라 줄어드는 방식으로 총 이자액이 적지만 초기 상환 부담이 큽니다.",
        "expected_file": ["대출_상환_방식_원금_균등vs.원리금_균등_차이_알아보기.pdf"],
        "difficulty": "medium",
        "category": "general_banking_FAQs",
        "subcategory": "대출상환"
    },
    {
        "id": "faq_005",
        "query": "예금보험은 얼마까지 보장되나요?",
        "expected_answer": "예금자 1인당 원금과 이자를 합하여 5천만원까지 보장됩니다.",
        "expected_file": [],
        "difficulty": "easy",
        "category": "general_banking_FAQs",
        "subcategory": "예금보험"
    }
]

# 추가 테스트 케이스들을 더 추가하여 120개 완성
additional_cases = [
    # === 추가 상품 관련 질문들 ===
    {
        "id": "product_012",
        "query": "KB 매직카대출의 특징은 무엇인가요?",
        "expected_answer": "신차 및 중고차 구매를 위한 자동차 대출로, 차량을 담보로 하는 대출상품입니다.",
        "expected_file": ["KB_매직카대출(신차).pdf", "KB_매직카대출(중고차).pdf"],
        "difficulty": "easy",
        "category": "company_products",
        "subcategory": "개인 자동차 대출"
    },
    {
        "id": "product_013",
        "query": "KB 내집마련디딤돌대출의 조건은 무엇인가요?",
        "expected_answer": "주택도시기금에서 운영하는 주택구입자금 대출로, 특정 조건을 만족하는 가구가 이용할 수 있습니다.",
        "expected_file": ["KB_내집마련디딤돌대출.pdf"],
        "difficulty": "medium",
        "category": "company_products",
        "subcategory": "개인 주택도시기금대출"
    },
    {
        "id": "product_014",
        "query": "KB 버팀목 전세자금대출의 특징은 무엇인가요?",
        "expected_answer": "전세보증금 마련을 위한 대출로, 주택도시기금에서 운영하는 전세자금 대출상품입니다.",
        "expected_file": ["KB_버팀목_전세자금대출.pdf"],
        "difficulty": "medium",
        "category": "company_products",
        "subcategory": "개인 주택도시기금대출"
    },
    {
        "id": "product_015",
        "query": "KB 기업시설자금대출의 대상은 누구인가요?",
        "expected_answer": "기업의 시설투자 및 운영자금 확보를 위한 대출로, 중소기업 및 소상공인이 주 대상입니다.",
        "expected_file": ["KB_시설자금대출.pdf"],
        "difficulty": "medium",
        "category": "company_products",
        "subcategory": "기업 대출"
    },
    {
        "id": "product_016",
        "query": "KB 더드림 소호신용대출의 특징은 무엇인가요?",
        "expected_answer": "소상공인 및 자영업자를 위한 신용대출로, 간편한 신청 절차와 빠른 승인이 특징입니다.",
        "expected_file": ["KB_더드림(The_Dream)_소호신용대출.pdf"],
        "difficulty": "easy",
        "category": "company_products",
        "subcategory": "기업 대출"
    },
    
    # === 추가 내규 관련 질문들 ===
    {
        "id": "rule_005",
        "query": "금리인하요구권은 무엇인가요?",
        "expected_answer": "은행여신약정에서 고객의 신용상태가 객관적으로 개선되었다고 판단되는 경우 고객이 은행에 금리인하를 요구할 수 있는 권리입니다. 은행은 심사에 필요한 자료를 요구할 수 있으며 심사결과에 따라 요구가 수용되지 않을 수 있습니다.",
        "expected_file": ["KB_금리인하요구권.pdf"],
        "difficulty": "medium",
        "category": "company_rules",
        "subcategory": "금리정책"
    },
    {
        "id": "rule_006",
        "query": "KB 민원처리 절차는 어떻게 되나요?",
        "expected_answer": "민원 접수부터 처리 완료까지의 체계적인 절차와 처리 기준을 제시합니다.",
        "expected_file": ["KB_민원의_처리.pdf"],
        "difficulty": "medium",
        "category": "company_rules",
        "subcategory": "민원처리"
    },
    {
        "id": "rule_007",
        "query": "KB 신용회복지원 제도는 무엇인가요?",
        "expected_answer": "신용불량자나 채무부담이 있는 고객을 위한 채무조정 및 신용회복 지원 제도입니다.",
        "expected_file": ["KB_신용회복지원_제도_안내.pdf"],
        "difficulty": "medium",
        "category": "company_rules",
        "subcategory": "신용회복"
    },
    
    # === 추가 법률 관련 질문들 ===
    {
        "id": "policy_005",
        "query": "금융감독원 고령 금융소비자보호 가이드라인은 무엇인가요?",
        "expected_answer": "고령 금융소비자의 특성을 고려한 금융서비스 제공 및 보호를 위한 가이드라인입니다.",
        "expected_file": ["금융감독원_고령_금융소비자보호_가이드라인.pdf"],
        "difficulty": "medium",
        "category": "industry_policies_and_regulations",
        "subcategory": "금융감독"
    },
    {
        "id": "policy_006",
        "query": "여신금융협회 여신심사 선진화 가이드라인은 무엇인가요?",
        "expected_answer": "여신심사의 투명성과 공정성을 높이기 위한 업계 가이드라인입니다.",
        "expected_file": ["여신금융협회_여신심사_선진화를_위한_가이드라인.pdf"],
        "difficulty": "hard",
        "category": "industry_policies_and_regulations",
        "subcategory": "여신심사"
    }
]

# 전체 데이터셋에 추가 케이스들 병합
dataset.extend(additional_cases)

# 120개까지 확장하기 위한 추가 케이스들
more_cases = []

# === 추가 상품 관련 질문들 (더 많은 실제 파일 기반) ===
product_cases = [
    {
        "id": "product_017",
        "query": "KB 로이어론의 특징은 무엇인가요?",
        "expected_answer": "변호사를 대상으로 하는 전문직 신용대출로, 법무업무 관련 자금 조달에 특화되어 있습니다.",
        "expected_file": ["KB로이어론.pdf"],
        "difficulty": "easy",
        "category": "company_products",
        "subcategory": "개인 신용대출"
    },
    {
        "id": "product_018",
        "query": "KB 사립학교교직원우대대출의 조건은 무엇인가요?",
        "expected_answer": "사립학교 교직원을 대상으로 하는 우대 대출로, 교육 관련 자금 조달에 특화되어 있습니다.",
        "expected_file": ["KB사립학교교직원우대대출.pdf"],
        "difficulty": "medium",
        "category": "company_products",
        "subcategory": "개인 신용대출"
    },
    {
        "id": "product_019",
        "query": "KB 새희망홀씨 긴급생계자금의 특징은 무엇인가요?",
        "expected_answer": "긴급한 생계자금이 필요한 고객을 위한 신속한 대출상품으로, 간편한 신청 절차가 특징입니다.",
        "expected_file": ["KB새희망홀씨_긴급생계자금.pdf"],
        "difficulty": "easy",
        "category": "company_products",
        "subcategory": "개인 신용대출"
    },
    {
        "id": "product_020",
        "query": "KB 친환경 매직카대출의 특징은 무엇인가요?",
        "expected_answer": "친환경 자동차 구매를 위한 특별 대출로, 환경 친화적 차량 구매를 지원합니다.",
        "expected_file": ["KB_친환경_매직카대출(신차).pdf"],
        "difficulty": "easy",
        "category": "company_products",
        "subcategory": "개인 자동차 대출"
    },
    {
        "id": "product_021",
        "query": "KB 청년전용 버팀목 전세자금대출의 조건은 무엇인가요?",
        "expected_answer": "청년층을 위한 전세자금 대출로, 특별한 우대 조건과 낮은 금리가 적용됩니다.",
        "expected_file": ["KB_청년전용_버팀목_전월세대출.pdf", "KB_청년전용_버팀목전세자금대출.pdf"],
        "difficulty": "medium",
        "category": "company_products",
        "subcategory": "개인 주택도시기금대출"
    },
    {
        "id": "product_022",
        "query": "KB 청년주택드림 디딤돌대출의 특징은 무엇인가요?",
        "expected_answer": "청년층의 주택 구입을 위한 디딤돌 대출로, 첫 주택 구입자에게 특별한 혜택을 제공합니다.",
        "expected_file": ["KB_청년주택드림_디딤돌대출.pdf"],
        "difficulty": "medium",
        "category": "company_products",
        "subcategory": "개인 주택도시기금대출"
    },
    {
        "id": "product_023",
        "query": "KB 기업시설자금대출의 대상은 누구인가요?",
        "expected_answer": "기업의 시설투자 및 운영자금 확보를 위한 대출로, 중소기업 및 소상공인이 주 대상입니다.",
        "expected_file": ["KB_시설자금대출.pdf"],
        "difficulty": "medium",
        "category": "company_products",
        "subcategory": "기업 대출"
    },
    {
        "id": "product_024",
        "query": "KB 더드림 지식재산 담보대출의 특징은 무엇인가요?",
        "expected_answer": "지식재산권을 담보로 하는 혁신적인 대출상품으로, IP 기반 기업의 자금 조달을 지원합니다.",
        "expected_file": ["KB_더드림_지식재산(IP)_담보대출.pdf"],
        "difficulty": "hard",
        "category": "company_products",
        "subcategory": "기업 대출"
    },
    {
        "id": "product_025",
        "query": "KB 메디칼론의 대상은 누구인가요?",
        "expected_answer": "의료기관 및 의료업계 종사자를 위한 전문 대출로, 의료 관련 시설 투자에 특화되어 있습니다.",
        "expected_file": ["KB_메디칼론.pdf"],
        "difficulty": "medium",
        "category": "company_products",
        "subcategory": "기업 대출"
    },
    {
        "id": "product_026",
        "query": "KB 무역금융의 특징은 무엇인가요?",
        "expected_answer": "수출입 거래를 위한 전문 금융 서비스로, 무역 관련 자금 조달과 리스크 관리를 제공합니다.",
        "expected_file": ["KB_무역금융.pdf"],
        "difficulty": "hard",
        "category": "company_products",
        "subcategory": "기업 대출"
    }
]

# === 추가 내규 관련 질문들 ===
rule_cases = [
    {
        "id": "rule_008",
        "query": "KB 공정한 채권회수를 위한 정책은 무엇인가요?",
        "expected_answer": "채권회수 과정에서 고객의 권익을 보호하고 공정한 절차를 준수하는 정책입니다.",
        "expected_file": ["KB_공정한_채권회수를_위한_정책.pdf"],
        "difficulty": "medium",
        "category": "company_rules",
        "subcategory": "채권회수"
    },
    {
        "id": "rule_009",
        "query": "KB 내부신고자 보호 정책의 내용은 무엇인가요?",
        "expected_answer": "내부 신고자를 보호하고 신고 제도를 안전하게 운영하기 위한 정책입니다.",
        "expected_file": ["KB_내부신고자_보호_정책.pdf"],
        "difficulty": "medium",
        "category": "company_rules",
        "subcategory": "내부신고"
    },
    {
        "id": "rule_010",
        "query": "KB 반부패 뇌물정책은 무엇인가요?",
        "expected_answer": "부패 방지와 청렴한 업무 환경 조성을 위한 정책으로, 뇌물 수수 금지를 명확히 규정합니다.",
        "expected_file": ["KB_반부패_뇌물정책.pdf"],
        "difficulty": "easy",
        "category": "company_rules",
        "subcategory": "반부패"
    },
    {
        "id": "rule_011",
        "query": "KB 범죄예방관련정책의 주요 내용은 무엇인가요?",
        "expected_answer": "금융 범죄 예방과 고객 보호를 위한 종합적인 정책과 절차를 제시합니다.",
        "expected_file": ["KB_범죄예방관련정책.pdf"],
        "difficulty": "medium",
        "category": "company_rules",
        "subcategory": "범죄예방"
    },
    {
        "id": "rule_012",
        "query": "KB 사전채무조정제도는 무엇인가요?",
        "expected_answer": "채무 상환에 어려움을 겪는 고객을 위한 사전 채무조정 제도로, 채무 부담을 완화합니다.",
        "expected_file": ["KB_사전채무조정제도_안내.pdf"],
        "difficulty": "medium",
        "category": "company_rules",
        "subcategory": "채무조정"
    },
    {
        "id": "rule_013",
        "query": "KB 세무정책의 주요 내용은 무엇인가요?",
        "expected_answer": "세무 관련 업무 처리와 고객 지원을 위한 정책과 절차를 제시합니다.",
        "expected_file": ["KB_세무정책.pdf"],
        "difficulty": "hard",
        "category": "company_rules",
        "subcategory": "세무"
    },
    {
        "id": "rule_014",
        "query": "KB 안전보건 목표 및 경영방침은 무엇인가요?",
        "expected_answer": "임직원의 안전과 건강을 보호하기 위한 목표와 경영방침을 제시합니다.",
        "expected_file": ["KB_안전보건_목표 및_경영방침.pdf"],
        "difficulty": "easy",
        "category": "company_rules",
        "subcategory": "안전보건"
    },
    {
        "id": "rule_015",
        "query": "KB 여신기본강령 및 모범규준은 무엇인가요?",
        "expected_answer": "여신 업무의 기본 원칙과 모범 규준을 제시하여 건전한 여신 관리를 위한 가이드라인입니다.",
        "expected_file": ["KB_여신기본강령_및_모범규준.pdf"],
        "difficulty": "hard",
        "category": "company_rules",
        "subcategory": "여신관리"
    }
]

# === 추가 법률 관련 질문들 ===
policy_cases = [
    {
        "id": "policy_007",
        "query": "금융위원회 개인사업자대출 여신심사 가이드라인은 무엇인가요?",
        "expected_answer": "개인사업자 대출 시 여신심사의 투명성과 공정성을 높이기 위한 가이드라인입니다.",
        "expected_file": ["금융위원회_개인사업자대출_여신심사_가이드라인.pdf"],
        "difficulty": "hard",
        "category": "industry_policies_and_regulations",
        "subcategory": "여신심사"
    },
    {
        "id": "policy_008",
        "query": "금융위원회 은행업감독규정의 주요 내용은 무엇인가요?",
        "expected_answer": "은행업의 건전한 운영을 위한 감독 규정과 기준을 제시합니다.",
        "expected_file": ["금융위원회_은행업감독규정(제2025-7호).pdf"],
        "difficulty": "hard",
        "category": "industry_policies_and_regulations",
        "subcategory": "은행감독"
    },
    {
        "id": "policy_009",
        "query": "여신금융협회 여신금융업권 금융사고 예방지침은 무엇인가요?",
        "expected_answer": "여신금융업권에서 발생할 수 있는 금융사고를 예방하기 위한 종합적인 지침입니다.",
        "expected_file": ["여신금융협회_여신금융업권_금융사고_예방지침_전문.pdf"],
        "difficulty": "hard",
        "category": "industry_policies_and_regulations",
        "subcategory": "사고예방"
    },
    {
        "id": "policy_010",
        "query": "여신금융협회 여신금융업권 표준내부통제기준은 무엇인가요?",
        "expected_answer": "여신금융업권의 내부통제 체계 구축을 위한 표준 기준을 제시합니다.",
        "expected_file": ["여신금융협회_여신금융업권_표준내부통제기준.pdf"],
        "difficulty": "hard",
        "category": "industry_policies_and_regulations",
        "subcategory": "내부통제"
    },
    {
        "id": "policy_011",
        "query": "여신전문금융업협회 여신금융상품 공시기준은 무엇인가요?",
        "expected_answer": "여신금융상품의 투명한 공시를 위한 기준과 가이드라인을 제시합니다.",
        "expected_file": ["여신전문금융업협회_여신금융상품_공시기준_개정(안)_전문.pdf"],
        "difficulty": "hard",
        "category": "industry_policies_and_regulations",
        "subcategory": "상품공시"
    },
    {
        "id": "policy_012",
        "query": "여신전문금융회사의 기업여신 심사 및 사후관리 모범규준은 무엇인가요?",
        "expected_answer": "기업여신의 심사와 사후관리를 위한 모범 규준과 가이드라인을 제시합니다.",
        "expected_file": ["여신전문금융회사의_기업여신_심사_및_사후관리_모범규준.pdf"],
        "difficulty": "hard",
        "category": "industry_policies_and_regulations",
        "subcategory": "기업여신"
    }
]

# === 추가 일반 FAQ 관련 질문들 ===
faq_cases = [
    {
        "id": "faq_006",
        "query": "대출 신청 시 필요한 서류는 무엇인가요?",
        "expected_answer": "소득증명서, 재직증명서, 통장사본, 신분증 등이 필요하며, 대출 종류에 따라 추가 서류가 요구될 수 있습니다.",
        "expected_file": [],
        "difficulty": "easy",
        "category": "general_banking_FAQs",
        "subcategory": "대출신청"
    },
    {
        "id": "faq_007",
        "query": "대출 금리는 어떻게 결정되나요?",
        "expected_answer": "기준금리, 신용등급, 소득수준, 거래실적 등을 종합적으로 고려하여 개인별로 차등 적용됩니다.",
        "expected_file": [],
        "difficulty": "medium",
        "category": "general_banking_FAQs",
        "subcategory": "대출금리"
    },
    {
        "id": "faq_008",
        "query": "중도상환수수료란 무엇인가요?",
        "expected_answer": "중도상환수수료는 대출 기간 중 대출금을 조기상환할 때 부과되는 수수료로, 계약 조건에 따라 부과 기간(보통 최초 실행일부터 최장 3년 등)과 계산 방식이 달라집니다.",
        "expected_file": ["중도상환수수료_변경으로_부담이_줄어들어요.pdf"],
        "difficulty": "medium",
        "category": "general_banking_FAQs",
        "subcategory": "중도상환"
    },
    {
        "id": "faq_009",
        "query": "신용등급은 어떻게 관리하나요?",
        "expected_answer": "정기적인 상환, 다양한 금융거래, 신용카드 이용 등을 통해 신용등급을 개선할 수 있습니다.",
        "expected_file": [],
        "difficulty": "easy",
        "category": "general_banking_FAQs",
        "subcategory": "신용관리"
    },
    {
        "id": "faq_010",
        "query": "대출 거절 시 대응 방법은 무엇인가요?",
        "expected_answer": "거절 사유를 확인하고, 신용등급 개선, 소득 증빙 강화, 다른 상품 검토 등의 방법을 고려할 수 있습니다.",
        "expected_file": [],
        "difficulty": "medium",
        "category": "general_banking_FAQs",
        "subcategory": "대출거절"
    }
]

# 모든 추가 케이스들을 병합
more_cases.extend(product_cases)
more_cases.extend(rule_cases)
more_cases.extend(policy_cases)
more_cases.extend(faq_cases)

# 전체 데이터셋에 추가
dataset.extend(more_cases)

# 120개까지 완성하기 위한 최종 추가 케이스들
final_cases = []

# === 더 많은 상품 관련 질문들 ===
more_product_cases = [
    {
        "id": "product_027",
        "query": "KB 모아드림론의 특징은 무엇인가요?",
        "expected_answer": "자녀 교육비 마련을 위한 대출상품으로, 교육 관련 자금 조달에 특화되어 있습니다.",
        "expected_file": ["KB_모아드림론.pdf"],
        "difficulty": "easy",
        "category": "company_products",
        "subcategory": "기업 대출"
    },
    {
        "id": "product_028",
        "query": "KB 미래성장기업 우대대출의 조건은 무엇인가요?",
        "expected_answer": "미래 성장 가능성이 높은 기업을 대상으로 하는 우대 대출로, 혁신 기업의 성장을 지원합니다.",
        "expected_file": ["KB_미래성장기업_우대대출.pdf"],
        "difficulty": "medium",
        "category": "company_products",
        "subcategory": "기업 대출"
    },
    {
        "id": "product_029",
        "query": "KB 사회적경제기업 우대대출의 특징은 무엇인가요?",
        "expected_answer": "사회적경제기업을 위한 특별 대출로, 사회적 가치 창출 기업의 성장을 지원합니다.",
        "expected_file": ["KB_사회적경제기업_우대대출.pdf"],
        "difficulty": "medium",
        "category": "company_products",
        "subcategory": "기업 대출"
    },
    {
        "id": "product_030",
        "query": "KB 수출기업 우대대출의 조건은 무엇인가요?",
        "expected_answer": "수출 기업을 위한 우대 대출로, 수출 관련 자금 조달과 해외 진출을 지원합니다.",
        "expected_file": ["KB_수출기업_우대대출.pdf"],
        "difficulty": "medium",
        "category": "company_products",
        "subcategory": "기업 대출"
    },
    {
        "id": "product_031",
        "query": "KB 우량산업단지기업 우대대출의 특징은 무엇인가요?",
        "expected_answer": "우량 산업단지 입주 기업을 위한 우대 대출로, 산업단지 기업의 성장을 지원합니다.",
        "expected_file": ["KB_우량산업단지기업_우대대출.pdf"],
        "difficulty": "medium",
        "category": "company_products",
        "subcategory": "기업 대출"
    },
    {
        "id": "product_032",
        "query": "KB 우수기술기업 TCB신용대출의 조건은 무엇인가요?",
        "expected_answer": "우수 기술을 보유한 기업을 위한 TCB 신용대출로, 기술 기반 기업의 자금 조달을 지원합니다.",
        "expected_file": ["KB_우수기술기업_TCB신용대출.pdf"],
        "difficulty": "hard",
        "category": "company_products",
        "subcategory": "기업 대출"
    },
    {
        "id": "product_033",
        "query": "KB 유망분야 성장기업 우대대출의 특징은 무엇인가요?",
        "expected_answer": "유망 분야의 성장 기업을 위한 우대 대출로, 미래 성장 동력 기업을 지원합니다.",
        "expected_file": ["KB_유망분야_성장기업_우대대출.pdf"],
        "difficulty": "medium",
        "category": "company_products",
        "subcategory": "기업 대출"
    },
    {
        "id": "product_034",
        "query": "KB 창업기업 장기보증부대출의 조건은 무엇인가요?",
        "expected_answer": "창업 기업을 위한 장기 보증부 대출로, 창업 초기 기업의 안정적인 자금 조달을 지원합니다.",
        "expected_file": ["KB_창업기업_장기보증부대출.pdf"],
        "difficulty": "hard",
        "category": "company_products",
        "subcategory": "기업 대출"
    },
    {
        "id": "product_035",
        "query": "KB 태양광발전사업자 우대대출의 특징은 무엇인가요?",
        "expected_answer": "태양광 발전 사업자를 위한 우대 대출로, 신재생에너지 사업의 발전을 지원합니다.",
        "expected_file": ["KB_태양광발전사업자우대대출.pdf"],
        "difficulty": "medium",
        "category": "company_products",
        "subcategory": "기업 대출"
    },
    {
        "id": "product_036",
        "query": "KB 특화산업단지 입주기업대출의 조건은 무엇인가요?",
        "expected_answer": "특화 산업단지 입주 기업을 위한 대출로, 특정 산업 분야의 기업 성장을 지원합니다.",
        "expected_file": ["KB_특화산업단지_입주기업대출.pdf"],
        "difficulty": "medium",
        "category": "company_products",
        "subcategory": "기업 대출"
    }
]

# === 더 많은 내규 관련 질문들 ===
more_rule_cases = [
    {
        "id": "rule_016",
        "query": "KB 내부통제규정의 주요 내용은 무엇인가요?",
        "expected_answer": "은행의 내부통제 체계 구축과 운영을 위한 규정과 절차를 제시합니다.",
        "expected_file": ["KB_내부통제규정.pdf"],
        "difficulty": "hard",
        "category": "company_rules",
        "subcategory": "내부통제"
    },
    {
        "id": "rule_017",
        "query": "KB 분할상환금 연체시 지연배상금 안내는 무엇인가요?",
        "expected_answer": "분할상환금 연체 시 발생하는 지연배상금에 대한 안내와 계산 방법을 제시합니다.",
        "expected_file": ["KB_분할상환금 연체시 지연배상금 안내.pdf"],
        "difficulty": "medium",
        "category": "company_rules",
        "subcategory": "연체관리"
    },
    {
        "id": "rule_018",
        "query": "KB 신청절차 및 필요서류는 무엇인가요?",
        "expected_answer": "각종 금융 서비스 신청 시 필요한 절차와 서류에 대한 안내를 제공합니다.",
        "expected_file": ["KB_신청절차 및 필요서류.pdf"],
        "difficulty": "easy",
        "category": "company_rules",
        "subcategory": "신청절차"
    },
    {
        "id": "rule_019",
        "query": "KB 원금 연체시 지연배상금 안내는 무엇인가요?",
        "expected_answer": "원금 연체 시 발생하는 지연배상금에 대한 안내와 계산 방법을 제시합니다.",
        "expected_file": ["KB_원금 연체시 지연배상금 안내.pdf"],
        "difficulty": "medium",
        "category": "company_rules",
        "subcategory": "연체관리"
    },
    {
        "id": "rule_020",
        "query": "KB 이자연체시 지연배상금 안내는 무엇인가요?",
        "expected_answer": "이자 연체 시 발생하는 지연배상금에 대한 안내와 계산 방법을 제시합니다.",
        "expected_file": ["KB_이자연체시 지연배상금 안내.pdf"],
        "difficulty": "medium",
        "category": "company_rules",
        "subcategory": "연체관리"
    },
    {
        "id": "rule_021",
        "query": "KB 인권정책의 주요 내용은 무엇인가요?",
        "expected_answer": "인권 보호와 존중을 위한 정책과 가이드라인을 제시합니다.",
        "expected_file": ["KB_인권정책.pdf"],
        "difficulty": "easy",
        "category": "company_rules",
        "subcategory": "인권"
    },
    {
        "id": "rule_022",
        "query": "KB 임직원 법규준수 행동기준은 무엇인가요?",
        "expected_answer": "임직원이 준수해야 할 법규와 행동 기준을 명확히 제시합니다.",
        "expected_file": ["KB_임직원_법규준수_행동기준.pdf"],
        "difficulty": "medium",
        "category": "company_rules",
        "subcategory": "법규준수"
    },
    {
        "id": "rule_023",
        "query": "KB 장애인고객 지원 서비스는 무엇인가요?",
        "expected_answer": "장애인 고객을 위한 특별한 지원 서비스와 편의 시설을 제공합니다.",
        "expected_file": ["KB_장애인고객_지원_서비스.pdf"],
        "difficulty": "easy",
        "category": "company_rules",
        "subcategory": "고객지원"
    },
    {
        "id": "rule_024",
        "query": "KB 직장 내 성희롱·괴롭힘 및 차별 예방 선언서는 무엇인가요?",
        "expected_answer": "직장 내 성희롱, 괴롭힘, 차별을 예방하기 위한 선언서와 정책을 제시합니다.",
        "expected_file": ["KB_직장_내 성희롱·괴롭힘_및_차별_예방_선언서.pdf"],
        "difficulty": "medium",
        "category": "company_rules",
        "subcategory": "인권보호"
    },
    {
        "id": "rule_025",
        "query": "KB 추심관련 권리의무 및 권리구제방법 안내는 무엇인가요?",
        "expected_answer": "채권 추심 과정에서의 권리와 의무, 그리고 권리구제 방법에 대한 안내를 제공합니다.",
        "expected_file": ["KB_추심관련 권리의무 및 권리구제방법 안내.pdf"],
        "difficulty": "hard",
        "category": "company_rules",
        "subcategory": "채권추심"
    }
]

# === 더 많은 법률 관련 질문들 ===
more_policy_cases = [
    {
        "id": "policy_013",
        "query": "금융소비자보호규정의 주요 내용은 무엇인가요?",
        "expected_answer": "금융소비자 보호를 위한 구체적인 규정과 기준을 제시합니다.",
        "expected_file": ["금융소비자보호규정.pdf"],
        "difficulty": "medium",
        "category": "industry_policies_and_regulations",
        "subcategory": "금융법규"
    },
    {
        "id": "policy_014",
        "query": "금융소비자보호에 관한 내부통제규정은 무엇인가요?",
        "expected_answer": "금융소비자 보호를 위한 내부통제 체계와 규정을 제시합니다.",
        "expected_file": ["금융소비자보호에_관한_내부통제규정.pdf"],
        "difficulty": "hard",
        "category": "industry_policies_and_regulations",
        "subcategory": "내부통제"
    }
]

# === 더 많은 일반 FAQ 관련 질문들 ===
more_faq_cases = [
    {
        "id": "faq_011",
        "query": "대출 승인까지 얼마나 걸리나요?",
        "expected_answer": "대출 종류와 금액에 따라 다르지만, 일반적으로 1-3일 정도 소요됩니다.",
        "expected_file": [],
        "difficulty": "easy",
        "category": "general_banking_FAQs",
        "subcategory": "대출승인"
    },
    {
        "id": "faq_012",
        "query": "대출 한도는 어떻게 결정되나요?",
        "expected_answer": "소득, 신용등급, 기존 대출 현황 등을 종합적으로 고려하여 개인별로 결정됩니다.",
        "expected_file": [],
        "difficulty": "medium",
        "category": "general_banking_FAQs",
        "subcategory": "대출한도"
    },
    {
        "id": "faq_013",
        "query": "원리금균등 상환 방식의 장단점은 무엇인가요?",
        "expected_answer": "원리금균등 상환은 원금+이자를 합한 월상환액이 일정해 자금관리가 용이하지만, 총 이자액은 원금균등 방식보다 많을 수 있습니다.",
        "expected_file": ["대출_상환_방식_원금_균등vs.원리금_균등_차이_알아보기.pdf"],
        "difficulty": "easy",
        "category": "general_banking_FAQs",
        "subcategory": "상환방법"
    },
    {
        "id": "faq_014",
        "query": "대출 연장은 가능한가요?",
        "expected_answer": "대출 종류와 조건에 따라 연장이 가능하며, 추가 심사와 수수료가 발생할 수 있습니다.",
        "expected_file": [],
        "difficulty": "medium",
        "category": "general_banking_FAQs",
        "subcategory": "대출연장"
    },
    {
        "id": "faq_015",
        "query": "대출 갈아타기(대환대출)란 무엇인가요?",
        "expected_answer": "대출 갈아타기(대환대출)는 기존 대출을 더 유리한 조건의 대출로 옮기는 서비스로, 모바일로 간편하게 이전 대출을 상환하고 새로운 대출로 전환할 수 있는 제도입니다(정부 주도·비대면 확대 등 문서 설명).",
        "expected_file": ["대출_갈아타기_총정리.pdf"],
        "difficulty": "medium",
        "category": "general_banking_FAQs",
        "subcategory": "조기상환"
    },
    {
        "id": "faq_016",
        "query": "신용등급이 낮아도 대출이 가능한가요?",
        "expected_answer": "신용등급이 낮아도 중금리 대출이나 담보 대출 등을 통해 대출이 가능할 수 있습니다.",
        "expected_file": [],
        "difficulty": "easy",
        "category": "general_banking_FAQs",
        "subcategory": "신용등급"
    },
    {
        "id": "faq_017",
        "query": "대출 거절 사유는 어떻게 확인하나요?",
        "expected_answer": "대출 거절 시 구체적인 사유를 안내받을 수 있으며, 개선 방안도 함께 제시됩니다.",
        "expected_file": [],
        "difficulty": "easy",
        "category": "general_banking_FAQs",
        "subcategory": "대출거절"
    },
    {
        "id": "faq_018",
        "query": "대출 계약서는 어디서 받을 수 있나요?",
        "expected_answer": "대출 승인 후 영업점에서 계약서를 받을 수 있으며, 온라인으로도 확인 가능합니다.",
        "expected_file": [],
        "difficulty": "easy",
        "category": "general_banking_FAQs",
        "subcategory": "계약서"
    },
    {
        "id": "faq_019",
        "query": "중도상환수수료 계산식은 어떻게 되나요?",
        "expected_answer": "중도상환수수료 계산식: '중도에 상환하는 금액 × 수수료율 × 잔존일수 ÷ 대출기간'입니다. 잔존일수는 상환일에서 만기일까지 남은 일수, 대출기간은 최초 대출일부터 만기전날까지의 일수를 뜻합니다.",
        "expected_file": ["중도상환수수료_변경으로_부담이_줄어들어요.pdf"],
        "difficulty": "medium",
        "category": "general_banking_FAQs",
        "subcategory": "이자계산"
    },
    {
        "id": "faq_020",
        "query": "2025년 1월 13일 기준 신용대출 중도상환수수료율은 어떻게 변경되었나요?",
        "expected_answer": "가계 신용대출의 중도상환수수료율은 기존 0.60~0.70% 수준에서 0.02%로 변경되었습니다(2025.01.13 기준, 문서 기준).",
        "expected_file": ["중도상환수수료_변경으로_부담이_줄어들어요.pdf"],
        "difficulty": "easy",
        "category": "general_banking_FAQs",
        "subcategory": "민원접수"
    }
]

# 모든 최종 케이스들을 병합
final_cases.extend(more_product_cases)
final_cases.extend(more_rule_cases)
final_cases.extend(more_policy_cases)
final_cases.extend(more_faq_cases)

# 전체 데이터셋에 최종 추가
dataset.extend(final_cases)

# 120개까지 완성하기 위한 마지막 추가 케이스들
last_cases = []

# === 마지막 상품 관련 질문들 ===
last_product_cases = [
    {
        "id": "product_037",
        "query": "KB 협력회사 윤리행동 기준은 무엇인가요?",
        "expected_answer": "협력회사와의 윤리적 거래를 위한 행동 기준과 가이드라인을 제시합니다.",
        "expected_file": ["KB_협력회사_윤리행동_기준.pdf"],
        "difficulty": "medium",
        "category": "company_rules",
        "subcategory": "협력회사"
    },
    {
        "id": "product_038",
        "query": "KB 은행거래시 유의사항은 무엇인가요?",
        "expected_answer": "은행 거래 시 주의해야 할 사항과 안전한 거래를 위한 가이드라인을 제시합니다.",
        "expected_file": ["KB_은행거래시_유의사항.pdf"],
        "difficulty": "easy",
        "category": "company_rules",
        "subcategory": "거래안전"
    },
    {
        "id": "product_039",
        "query": "은행여신거래기본약관은 어떤 거래에 적용되나요?",
        "expected_answer": "이 약관은 어음대출·어음할인·증서대출·당좌대출·지급보증·유가증권대여·외국환 기타의 여신에 관한 모든 거래에 적용됩니다.",
        "expected_file": ["KB_은행여신거래기본약관.pdf"],
        "difficulty": "hard",
        "category": "company_rules",
        "subcategory": "여신약관"
    },
    {
        "id": "product_040",
        "query": "KB 은행여신거래기본약관 가계용의 특징은 무엇인가요?",
        "expected_answer": "가계용 여신거래를 위한 특별 약관으로, 개인 고객에게 맞춤화된 조건을 제공합니다.",
        "expected_file": ["KB_은행여신거래기본약관가계용.pdf"],
        "difficulty": "medium",
        "category": "company_rules",
        "subcategory": "여신약관"
    },
    {
        "id": "product_041",
        "query": "KB 은행여신거래기본약관 기업용의 특징은 무엇인가요?",
        "expected_answer": "기업용 여신거래를 위한 특별 약관으로, 기업 고객에게 맞춤화된 조건을 제공합니다.",
        "expected_file": ["KB_은행여신거래기본약관기업용.pdf"],
        "difficulty": "medium",
        "category": "company_rules",
        "subcategory": "여신약관"
    }
]

# === 마지막 일반 FAQ 관련 질문들 ===
last_faq_cases = [
    {
        "id": "faq_021",
        "query": "대출 신청 전 준비사항은 무엇인가요?",
        "expected_answer": "소득증명서, 재직증명서, 통장사본 등 필요한 서류를 미리 준비하고, 신용등급을 확인하는 것이 좋습니다.",
        "expected_file": [],
        "difficulty": "easy",
        "category": "general_banking_FAQs",
        "subcategory": "대출준비"
    },
    {
        "id": "faq_022",
        "query": "대출 심사 기준은 무엇인가요?",
        "expected_answer": "신용등급, 소득수준, 기존 대출 현황, 거래실적 등을 종합적으로 평가하여 심사합니다.",
        "expected_file": [],
        "difficulty": "medium",
        "category": "general_banking_FAQs",
        "subcategory": "대출심사"
    },
    {
        "id": "faq_023",
        "query": "대출 상환 일정은 어떻게 확인하나요?",
        "expected_answer": "인터넷뱅킹, 모바일앱, 또는 고객센터를 통해 대출 상환 일정과 잔액을 확인할 수 있습니다.",
        "expected_file": [],
        "difficulty": "easy",
        "category": "general_banking_FAQs",
        "subcategory": "상환일정"
    },
    {
        "id": "faq_024",
        "query": "대출 연체 시 대응 방법은 무엇인가요?",
        "expected_answer": "즉시 은행에 연락하여 연체 사유를 설명하고, 상환 계획을 수립하여 연체 기간을 최소화해야 합니다.",
        "expected_file": [],
        "difficulty": "medium",
        "category": "general_banking_FAQs",
        "subcategory": "연체대응"
    },
    {
        "id": "faq_025",
        "query": "대출 담보물은 무엇인가요?",
        "expected_answer": "부동산, 자동차, 예금, 유가증권 등 대출금 상환을 보장하기 위한 담보물을 말합니다.",
        "expected_file": [],
        "difficulty": "easy",
        "category": "general_banking_FAQs",
        "subcategory": "담보물"
    },
    {
        "id": "faq_026",
        "query": "대출 보증인은 누가 될 수 있나요?",
        "expected_answer": "신용이 양호한 가족, 친지, 또는 제3자가 보증인이 될 수 있으며, 보증인의 소득과 신용도가 중요합니다.",
        "expected_file": [],
        "difficulty": "medium",
        "category": "general_banking_FAQs",
        "subcategory": "보증인"
    },
    {
        "id": "faq_027",
        "query": "대출 계약 해지는 언제 가능한가요?",
        "expected_answer": "대출 계약 해지는 상환 완료 시, 또는 특별한 사유가 있을 때 가능하며, 해지 수수료가 발생할 수 있습니다.",
        "expected_file": [],
        "difficulty": "medium",
        "category": "general_banking_FAQs",
        "subcategory": "계약해지"
    },
    {
        "id": "faq_028",
        "query": "대출 조건 변경은 가능한가요?",
        "expected_answer": "대출 조건 변경은 상환 방식, 금리, 기간 등에 따라 가능하며, 추가 심사와 수수료가 발생할 수 있습니다.",
        "expected_file": [],
        "difficulty": "medium",
        "category": "general_banking_FAQs",
        "subcategory": "조건변경"
    },
    {
        "id": "faq_029",
        "query": "대출 관련 세금 혜택은 있나요?",
        "expected_answer": "주택담보대출 이자 상환액에 대한 소득공제 등 일부 대출에 대해 세금 혜택이 있습니다.",
        "expected_file": [],
        "difficulty": "hard",
        "category": "general_banking_FAQs",
        "subcategory": "세금혜택"
    },
    {
        "id": "faq_030",
        "query": "대출 관련 보험은 필요한가요?",
        "expected_answer": "대출 상환 보장을 위한 신용보험, 생명보험 등이 있으며, 대출 종류와 조건에 따라 필요할 수 있습니다.",
        "expected_file": [],
        "difficulty": "medium",
        "category": "general_banking_FAQs",
        "subcategory": "대출보험"
    },
    {
        "id": "faq_031",
        "query": "대출 관련 사기 예방 방법은 무엇인가요?",
        "expected_answer": "정식 은행 채널을 통한 신청, 개인정보 보호, 의심스러운 제안 거절 등을 통해 사기를 예방할 수 있습니다.",
        "expected_file": [],
        "difficulty": "easy",
        "category": "general_banking_FAQs",
        "subcategory": "사기예방"
    },
    {
        "id": "faq_032",
        "query": "대출 관련 고객센터 연락처는 무엇인가요?",
        "expected_answer": "KB국민은행 고객센터 1588-9999 또는 1599-9999로 연락하여 대출 관련 문의를 할 수 있습니다.",
        "expected_file": [],
        "difficulty": "easy",
        "category": "general_banking_FAQs",
        "subcategory": "고객센터"
    },
    {
        "id": "faq_033",
        "query": "대출 관련 온라인 신청은 어떻게 하나요?",
        "expected_answer": "KB국민은행 인터넷뱅킹이나 모바일앱을 통해 온라인으로 대출을 신청할 수 있습니다.",
        "expected_file": [],
        "difficulty": "easy",
        "category": "general_banking_FAQs",
        "subcategory": "온라인신청"
    },
    {
        "id": "faq_034",
        "query": "대출 관련 영업점 방문은 언제 하나요?",
        "expected_answer": "온라인 신청이 어려운 경우나 상담이 필요한 경우 영업점을 방문하여 대출을 신청할 수 있습니다.",
        "expected_file": [],
        "difficulty": "easy",
        "category": "general_banking_FAQs",
        "subcategory": "영업점방문"
    },
    {
        "id": "faq_035",
        "query": "대출 관련 상담은 어디서 받을 수 있나요?",
        "expected_answer": "고객센터, 영업점, 온라인 상담 서비스를 통해 대출 관련 상담을 받을 수 있습니다.",
        "expected_file": [],
        "difficulty": "easy",
        "category": "general_banking_FAQs",
        "subcategory": "상담서비스"
    }
]

# 모든 마지막 케이스들을 병합
last_cases.extend(last_product_cases)
last_cases.extend(last_faq_cases)

# 전체 데이터셋에 마지막 추가
dataset.extend(last_cases)

# 120개까지 완성하기 위한 최종 5개 케이스
final_5_cases = [
    {
        "id": "faq_036",
        "query": "대출 관련 모바일앱 사용법은 어떻게 되나요?",
        "expected_answer": "KB국민은행 모바일앱에서 대출 신청, 상환, 잔액 조회 등 모든 대출 관련 서비스를 이용할 수 있습니다.",
        "expected_file": [],
        "difficulty": "easy",
        "category": "general_banking_FAQs",
        "subcategory": "모바일앱"
    },
    {
        "id": "faq_037",
        "query": "대출 관련 인터넷뱅킹 사용법은 어떻게 되나요?",
        "expected_answer": "KB국민은행 인터넷뱅킹에서 대출 신청, 상환, 잔액 조회 등 모든 대출 관련 서비스를 이용할 수 있습니다.",
        "expected_file": [],
        "difficulty": "easy",
        "category": "general_banking_FAQs",
        "subcategory": "인터넷뱅킹"
    },
    {
        "id": "faq_038",
        "query": "대출 관련 자동이체 설정은 어떻게 하나요?",
        "expected_answer": "인터넷뱅킹이나 모바일앱에서 대출 상환 자동이체를 설정하여 매월 자동으로 상환할 수 있습니다.",
        "expected_file": [],
        "difficulty": "easy",
        "category": "general_banking_FAQs",
        "subcategory": "자동이체"
    },
    {
        "id": "faq_039",
        "query": "대출 관련 알림 서비스는 어떻게 이용하나요?",
        "expected_answer": "대출 상환일 알림, 잔액 알림 등 다양한 알림 서비스를 통해 대출 관련 정보를 받을 수 있습니다.",
        "expected_file": [],
        "difficulty": "easy",
        "category": "general_banking_FAQs",
        "subcategory": "알림서비스"
    },
    {
        "id": "faq_040",
        "query": "대출 관련 보안은 어떻게 관리하나요?",
        "expected_answer": "정기적인 비밀번호 변경, 개인정보 보호, 의심스러운 접근 차단 등을 통해 대출 관련 보안을 관리할 수 있습니다.",
        "expected_file": [],
        "difficulty": "medium",
        "category": "general_banking_FAQs",
        "subcategory": "보안관리"
    }
]

# 최종 5개 케이스 추가
dataset.extend(final_5_cases)

def get_dataset_stats():
    """데이터셋 통계 정보 반환"""
    total_cases = len(dataset)
    
    # 카테고리별 분포
    category_count = {}
    for case in dataset:
        category = case.get("category", "unknown")
        category_count[category] = category_count.get(category, 0) + 1
    
    # 난이도별 분포
    difficulty_count = {}
    for case in dataset:
        difficulty = case.get("difficulty", "unknown")
        difficulty_count[difficulty] = difficulty_count.get(difficulty, 0) + 1
    
    return {
        "total_cases": total_cases,
        "category_distribution": category_count,
        "difficulty_distribution": difficulty_count,
        "categories": list(category_count.keys()),
        "difficulties": list(difficulty_count.keys())
    }

def get_test_cases_by_category(category: str):
    """특정 카테고리의 테스트 케이스만 반환"""
    return [case for case in dataset if case.get("category") == category]

def get_test_cases_by_difficulty(difficulty: str):
    """특정 난이도의 테스트 케이스만 반환"""
    return [case for case in dataset if case.get("difficulty") == difficulty]

# 테스트용 실행
if __name__ == "__main__":
    stats = get_dataset_stats()
    print("KB금융 RAG 테스트 데이터셋 통계")
    print("=" * 40)
    print(f"총 테스트 케이스: {stats['total_cases']}개")
    print(f"카테고리별 분포: {stats['category_distribution']}")
    print(f"난이도별 분포: {stats['difficulty_distribution']}")
    
    # 샘플 케이스 출력
    print(f"\n샘플 테스트 케이스:")
    for i, case in enumerate(dataset[:3], 1):
        print(f"{i}. [{case['category']}] {case['query']}")
        print(f"   예상 답변: {case['expected_answer'][:50]}...")
        print(f"   예상 파일: {case['expected_file']}")
        print()
