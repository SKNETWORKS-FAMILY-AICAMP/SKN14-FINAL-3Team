import os
import json
import joblib
import numpy as np
import pandas as pd
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# -----------------------------
# 공통 상수
# -----------------------------
KRW_UNIT_CONVERSION_FACTOR = 10_000  # 원 → 만원 변환 (개인 피처 가공 시에만 사용)

# 개인 가드레일/한도
MAX_LOAN_LIMIT_PERSONAL = 300_000_000      # 3억원
MAX_LTI_RATIO_PERSONAL  = 3.0              # LTI ≤ 3

# 기업 가드레일/한도
MAX_LOAN_LIMIT_CORPORATE  = 2_000_000_000  # 20억원
MAX_LOAN_TO_ASSETS_CORP   = 0.5            # 요청액 ≤ 총자산의 50% (예시)
CORP_FEATURE_JSON_DEFAULT = 'ml_models/corporate_loan_features.json'


# -----------------------------
# Base Model
# -----------------------------
class BaseApprovalModel:
    def __init__(self) -> None:
        pass

    # ----- 공통 유틸 -----
    @staticmethod
    def _parse_number(x, default: float = 0.0) -> float:
        try:
            if x is None:
                return float(default)
            if isinstance(x, (int, float, np.integer, np.floating)):
                return float(x)
            s = str(x).replace(',', '').strip()
            if s == '':
                return float(default)
            return float(s)
        except Exception:
            return float(default)

    @staticmethod
    def get_credit_rating_by_probability(probability: float) -> str:
        if probability >= 0.9:
            return '최우수'
        elif probability >= 0.8:
            return '우수'
        elif probability >= 0.7:
            return '양호'
        elif probability >= 0.6:
            return '보통'
        else:
            return '위험'

    @staticmethod
    def get_credit_rating(score: int) -> str:
        if score >= 900: return 'AAA'
        if score >= 800: return 'AA'
        if score >= 700: return 'A'
        if score >= 600: return 'B'
        if score >= 500: return 'C'
        return 'D'

    @staticmethod
    def _prob_to_score(prob: float) -> int:
        # 부도 확률(prob)이 아닌, 생존 확률(1-prob)을 점수화
        return max(0, min(1000, int((1.0 - float(prob)) * 1000)))

    # 하위 클래스에서 오버라이드
    def predict(self, customer_data: Dict[str, Any], loan_data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


# -----------------------------
# Personal Loan Model
# -----------------------------
class PersonalLoanApprovalModel(BaseApprovalModel):
    def __init__(
        self,
        model_path: str = 'ml_models/personal_loan_lgbm.pkl',
        scaler_path: str = 'ml_models/personal_loan_scaler.pkl',
    ) -> None:
        super().__init__()
        self._model = None
        self._scaler = None
        self.model_path = model_path
        self.scaler_path = scaler_path
        self._ensure_loaded()

        # 학습 시 사용한 컬럼(원핫 포함, drop_first=True 기준)
        self.model_columns: List[str] = [
            'person_age', 'person_income', 'person_emp_exp', 'loan_amnt', 'loan_int_rate',
            'loan_percent_income', 'cb_person_cred_hist_length', 'credit_score',
            'previous_loan_defaults_on_file', 'person_gender_male',
            'person_education_Bachelor', 'person_education_Doctorate', 'person_education_High School',
            'person_education_Master',
            'person_home_ownership_OTHER', 'person_home_ownership_OWN',
            'person_home_ownership_RENT', 'loan_intent_EDUCATION',
            'loan_intent_HOMEIMPROVEMENT', 'loan_intent_MEDICAL', 'loan_intent_PERSONAL',
            'loan_intent_VENTURE'
        ]

    def _ensure_loaded(self) -> None:
        try:
            self._model = joblib.load(self.model_path)
            self._scaler = joblib.load(self.scaler_path)
            logger.info("[Personal] 모델/스케일러 로딩 성공")
        except Exception as e:
            logger.error(f"[Personal] 모델 로드 실패: {e}")
            self._model = None
            self._scaler = None

    def _guardrails(self, customer_data: Dict[str, Any], loan_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        requested_amount = self._parse_number(loan_data.get('amount', 0), default=0.0)

        # 최대 한도
        if requested_amount > MAX_LOAN_LIMIT_PERSONAL:
            logger.warning(f"[개인] 최대 대출 한도 초과: {requested_amount} > {MAX_LOAN_LIMIT_PERSONAL}")
            return {'credit_score': 450, 'credit_rating': 'D', 'approval_status': 'rejected', 'recommended_limit': 0}

        # LTI 가드
        annual_income_raw = self._parse_number(customer_data.get('annual_income', 0))
        if annual_income_raw > 0:
            lti = requested_amount / annual_income_raw
            if lti > MAX_LTI_RATIO_PERSONAL:
                logger.warning(f"[개인] LTI 초과: {lti:.2f} > {MAX_LTI_RATIO_PERSONAL}")
                return {'credit_score': 480, 'credit_rating': 'D', 'approval_status': 'rejected', 'recommended_limit': 0}
        return None

    @staticmethod
    def _calc_recommended_limit(score: int, requested_amount: float) -> float:
        if score >= 800:
            return min(requested_amount * 1.2, 100_000_000)
        elif score >= 700:
            return min(requested_amount * 1.1, 80_000_000)
        elif score >= 600:
            return min(requested_amount * 1.0, 50_000_000)
        else:
            return min(requested_amount * 0.8, 30_000_000)

    def _prepare_features(self, customer_data: Dict[str, Any], loan_data: Dict[str, Any]) -> pd.DataFrame:
        requested_amount = self._parse_number(loan_data.get('amount', 0))
        annual_income = self._parse_number(customer_data.get('annual_income', 25_000_000)) / KRW_UNIT_CONVERSION_FACTOR
        loan_amount_mwan = requested_amount / KRW_UNIT_CONVERSION_FACTOR

        gender_raw = str(customer_data.get('gender', '')).strip()
        if gender_raw in ['남', '남성', 'M', 'male', 'Male']:
            gender = 'male'
        else:
            gender = 'female'

        input_data = {
            'person_age': float(self._parse_number(customer_data.get('age', 30))),
            'person_gender': gender,
            'person_education': customer_data.get('education_level', 'Bachelor'),
            'person_income': float(annual_income),
            'person_emp_exp': int(self._parse_number(customer_data.get('years_of_service', 0))),
            'person_home_ownership': customer_data.get('housing_status', 'RENT'),
            'loan_amnt': float(loan_amount_mwan),
            'loan_intent': loan_data.get('purpose', 'PERSONAL'),
            'loan_int_rate': float(self._parse_number(loan_data.get('interest_rate', 5.0))),
            'loan_percent_income': float((loan_amount_mwan / annual_income) if annual_income > 0 else 0.0),
            'cb_person_cred_hist_length': float(self._parse_number(customer_data.get('credit_history_length', 5))),
            'previous_loan_defaults_on_file': 1 if customer_data.get('has_delinquency', False) else 0
        }
        df = pd.DataFrame([input_data])

        # 신용점수 → (A~G) 1~7 구간으로 인코딩
        raw_score = int(self._parse_number(customer_data.get('credit_score', 750)))
        credit_letter = self.get_credit_rating(raw_score)  # 'AAA','AA','A','B',...
        map_letter = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7}
        df['credit_score'] = map_letter.get(credit_letter[0], 3)

        # 로그 변환
        df['person_income'] = np.log1p(df['person_income'])

        # 원핫
        cat_cols = ['person_gender', 'person_education', 'person_home_ownership', 'loan_intent']
        df_enc = pd.get_dummies(df, columns=cat_cols, drop_first=True)

        # 누락 컬럼 0 채우기 + 순서 정렬
        for col in self.model_columns:
            if col not in df_enc.columns:
                df_enc[col] = 0.0
        df_enc = df_enc[self.model_columns]
        return df_enc

    def predict(self, customer_data: Dict[str, Any], loan_data: Dict[str, Any]) -> Dict[str, Any]:
        # 가드레일
        early = self._guardrails(customer_data, loan_data)
        if early is not None:
            return early

        requested_amount = self._parse_number(loan_data.get('amount', 0))
        try:
            if self._model is None or self._scaler is None:
                prob = 0.75
            else:
                feats = self._prepare_features(customer_data, loan_data)
                scaled = self._scaler.transform(feats)
                prob = float(self._model.predict_proba(scaled)[0][1])

            score = self._prob_to_score(prob)
            return {
                'credit_score': score,
                'credit_rating': self.get_credit_rating(score),
                'approval_status': 'approved' if score >= 600 else 'rejected',
                'recommended_limit': self._calc_recommended_limit(score, requested_amount)
            }
        except Exception as e:
            logger.error(f"[개인] 예측 오류: {e}")
            return {
                'credit_score': 750,
                'credit_rating': 'B',
                'approval_status': 'approved',
                'recommended_limit': requested_amount if requested_amount else 30_000_000
            }


# -----------------------------
# Corporate Loan Model
# -----------------------------
class CorporateLoanApprovalModel(BaseApprovalModel):
    def __init__(
        self,
        model_path: str = 'ml_models/corporate_loan_lgbm.pkl',
        scaler_path: str = 'ml_models/corporate_loan_scaler.pkl',
        feature_json_path: str = CORP_FEATURE_JSON_DEFAULT,
    ) -> None:
        super().__init__()
        self._model = None
        self._scaler = None
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.feature_json_path = feature_json_path
        self._ensure_loaded()

    def _ensure_loaded(self) -> None:
        try:
            self._model = joblib.load(self.model_path)
            self._scaler = joblib.load(self.scaler_path)
            logger.info("[Corporate] 모델/스케일러 로딩 성공")
        except Exception as e:
            logger.error(f"[Corporate] 모델 로드 실패: {e}")
            self._model = None
            self._scaler = None

    # ----- 재무 점수 -----
    def _compute_financial_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        def g(col): return pd.to_numeric(out.get(col, np.nan), errors='coerce')

        # Altman Z
        CA = g("Current assets")
        CL = g("Total Current Liabilities")
        RE = g("Retained Earnings")
        EBIT = g("EBIT")
        NS = g("Net sales")
        TA = g("Total assets")
        TL = g("Total Liabilities")
        MV = g("Market value")

        working_capital = CA - CL
        with np.errstate(divide='ignore', invalid='ignore'):
            out["Altman_Z"] = (
                1.2 * (working_capital / TA) +
                1.4 * (RE / TA) +
                3.3 * (EBIT / TA) +
                0.6 * (MV / TL) +
                1.0 * (NS / TA)
            )

        # Ohlson O (간이)
        NI = g("Net Income")
        with np.errstate(divide='ignore', invalid='ignore'):
            out["Ohlson_O"] = (
                -1.32
                - 0.407 * np.log(TA.replace(0, np.nan))
                + 6.03 * (TL / TA)
                - 1.43 * ((CA - CL) / TA)
                + 0.0757 * (CL / TL)
                - 2.37 * (NI < 0).astype(float)
            )

        # Piotroski F (간이: ROA/CFO/Accrual)
        EBITDA = g("EBITDA")
        roa_pos = ((NI / TA) > 0).astype(float)
        cfo_pos = (EBITDA.where(~EBITDA.isna(), NI) > 0).astype(float)
        accrual = (EBITDA.where(~EBITDA.isna(), NI) > NI).astype(float)
        out["Piotroski_F"] = (roa_pos + cfo_pos + accrual).fillna(0)

        return out

    def _prepare_dataframe(self, company: Dict[str, Any]) -> pd.DataFrame:
        mapping = {
            'current_assets': "Current assets",
            'current_liabilities': "Total Current Liabilities",
            'retained_earnings': "Retained Earnings",
            'ebit': "EBIT",
            'net_sales': "Net sales",
            'total_assets': "Total assets",
            'total_liabilities': "Total Liabilities",
            'net_income': "Net Income",
            'ebitda': "EBITDA",
            'inventory': "Inventory",
            'total_receivables': "Total Receivables",
            'market_value': "Market value",
            'gross_profit': "Gross Profit",
            'long_term_debt': "Total Long-term debt",
            'total_revenue': "Total Revenue",
        }

        values = {}
        for skey, std in mapping.items():
            val = company.get(std, None)
            if val is None:
                val = company.get(skey, None)
            values[std] = self._parse_number(val, default=np.nan)

        df = pd.DataFrame([values])

        # 파생 비율
        CA = df["Current assets"]
        CL = df["Total Current Liabilities"]
        TA = df["Total assets"].replace(0, np.nan)
        TL = df["Total Liabilities"]
        NI = df["Net Income"]
        NS = df["Net sales"]
        GP = df["Gross Profit"]
        INV = df["Inventory"]

        with np.errstate(divide='ignore', invalid='ignore'):
            df["Net Profit Margin"] = NI / df.get("Total Revenue", NS.replace(0, np.nan))
            df["Gross Profit Margin"] = GP / NS
            df["ROA"] = NI / TA
            df["ROS"] = NI / NS
            df["Current Ratio"] = CA / CL
            df["Quick Ratio"] = (CA - INV) / CL
            df["Debt to asset ratio"] = TL / TA
            
            # 이전 년도 데이터가 없으므로, 성장률/회전율은 임의의 값으로 근사
            # 실제 시스템에서는 이전 재무 데이터와 비교해야 함
            # 매출액 증가율 (Sales Growth) - 여기서는 순이익률을 기반으로 근사
            df["Sales Growth"] = df["Net Profit Margin"] * 0.5 + 0.05 # 5% 기본 성장률 + a
            
            # 총자산 회전율 (Asset Turnover)
            df["Asset Turnover"] = NS / TA

        # 점수계산
        df = self._compute_financial_scores(df)

        # 숫자화/결측 0
        df = df.apply(pd.to_numeric, errors='coerce').fillna(0.0)
        return df

    def _resolve_feature_order(self, base_df: pd.DataFrame) -> List[str]:
        # 1) LightGBM feature_name_ 우선
        if self._model is not None and hasattr(self._model, "feature_name_"):
            names = list(getattr(self._model, "feature_name_") or [])
            if names and not str(names[0]).lower().startswith('feature_'):
                return names

        # 2) JSON 파일
        try:
            if self.feature_json_path and os.path.exists(self.feature_json_path):
                with open(self.feature_json_path, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                cols = meta.get('feature_columns') or meta.get('columns')
                if isinstance(cols, list) and cols:
                    return cols
        except Exception as e:
            logger.warning(f"[Corporate] 피처 JSON 로드 실패: {e}")

        # 3) 기본 피처셋
        return [
            "Current assets","Total Current Liabilities","Retained Earnings","EBIT","Net sales",
            "Total assets","Total Liabilities","Net Income","EBITDA","Inventory",
            "Total Receivables","Market value","Gross Profit","Total Long-term debt","Total Revenue",
            "Net Profit Margin","Gross Profit Margin","ROA","ROS",
            "Current Ratio","Quick Ratio","Debt to asset ratio",
            "Altman_Z","Ohlson_O","Piotroski_F",
        ]

    def _guardrails(self, company: Dict[str, Any], loan_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        requested_amount = self._parse_number(loan_data.get('amount', 0), default=0.0)

        # 최대 한도
        if requested_amount > MAX_LOAN_LIMIT_CORPORATE:
            logger.warning(f"[기업] 최대 대출 한도 초과: {requested_amount} > {MAX_LOAN_LIMIT_CORPORATE}")
            return {'credit_score': 450, 'credit_rating': 'D', 'approval_status': 'rejected', 'recommended_limit': 0}

        # 총자산 대비 요청액
        total_assets = self._parse_number(company.get('Total assets') or company.get('total_assets'), default=0.0)
        if total_assets > 0:
            ratio = requested_amount / total_assets
            if ratio > MAX_LOAN_TO_ASSETS_CORP:
                logger.warning(f"[기업] 총자산 대비 과도: {ratio:.2f} > {MAX_LOAN_TO_ASSETS_CORP}")
                return {'credit_score': 480, 'credit_rating': 'D', 'approval_status': 'rejected', 'recommended_limit': 0}
        return None

    def _calc_recommended_limit(self, score: int, requested_amount: float, company_data: Dict[str, Any]) -> float:
        """ 기업 재무상태 기반 추천 한도 산출 """
        # 1. 재무 지표 기반 기본 한도(Capacity Limit) 설정
        # EBITDA의 2배, 총자산의 20%, 순매출의 10% 중 가장 보수적인(낮은) 금액을 기준 한도로 설정
        ebitda = self._parse_number(company_data.get('ebitda', 0))
        total_assets = self._parse_number(company_data.get('total_assets', 0))
        net_sales = self._parse_number(company_data.get('net_sales', 0))

        limit_by_ebitda = ebitda * 2.0
        limit_by_assets = total_assets * 0.2
        limit_by_sales = net_sales * 0.1

        # 모든 한도 후보가 0 이상이 되도록 보장
        capacity_limit = min(
            limit_by_ebitda if limit_by_ebitda > 0 else float('inf'),
            limit_by_assets if limit_by_assets > 0 else float('inf'),
            limit_by_sales if limit_by_sales > 0 else float('inf')
        )
        if capacity_limit == float('inf'): capacity_limit = 0 # 모든 지표가 0 이하인 경우

        # 2. 신용점수에 따라 한도 조정
        score_multiplier = 0.7 + (score / 1000) * 0.5  # 700점일 때 약 1.05, 900점일 때 약 1.15
        adjusted_limit = capacity_limit * score_multiplier

        # 3. 최종 한도 결정: (조정된 한도 vs 신청금액) 중 낮은 금액을 선택하되, 최대 한도를 넘지 않도록 함
        final_limit = min(adjusted_limit, requested_amount, MAX_LOAN_LIMIT_CORPORATE)
        return max(0, final_limit) # 최종 한도가 음수가 되지 않도록 보장

    def predict(self, customer_data: Dict[str, Any], loan_data: Dict[str, Any]) -> Dict[str, Any]:
        # company == customer_data (기업 맥락)
        early = self._guardrails(customer_data, loan_data)
        if early is not None:
            return early

        requested_amount = self._parse_number(loan_data.get('amount', 0))
        try:
            if self._model is None or self._scaler is None:
                prob = 0.75
                base_df = self._prepare_dataframe(customer_data)
            else:
                base_df = self._prepare_dataframe(customer_data)
                cols = self._resolve_feature_order(base_df)
                # 누락 0 채우고 정렬
                for c in cols:
                    if c not in base_df.columns:
                        base_df[c] = 0.0
                feats = base_df[cols]
                scaled_values = self._scaler.transform(feats.values)
                scaled_df = pd.DataFrame(scaled_values, columns=cols)
                prob = float(self._model.predict_proba(scaled_df)[0][1])

            score = self._prob_to_score(prob)
            result = {
                'credit_score': score,
                'credit_rating': self.get_credit_rating(score),
                'approval_status': 'approved' if prob <= 0.5 else 'rejected',
                'recommended_limit': self._calc_recommended_limit(score, requested_amount, customer_data),
                'diagnostics': {
                    'probability': round(prob, 6), # 부도 확률
                    'survival_probability': round(1.0 - prob, 6), # 생존 확률
                }
            }
            # 진단지표(가능 시)
            for k in ['Altman_Z', 'Ohlson_O', 'Piotroski_F']:
                if k in base_df.columns:
                    result['diagnostics'][k.lower()] = float(base_df[k].iloc[0])
            # 파생 비율 진단지표에 추가
            for k in ["Current Ratio", "Quick Ratio", "Net Profit Margin", "Debt to asset ratio", "ROA", "ROS", "Sales Growth", "Asset Turnover"]:
                 if k in base_df.columns:
                    result['diagnostics'][k.lower().replace(" ", "_")] = float(base_df[k].iloc[0])
            return result

        except Exception as e:
            logger.error(f"[기업] 예측 오류: {e}")
            return {
                'credit_score': 750,
                'credit_rating': 'B',
                'approval_status': 'approved',
                'recommended_limit': requested_amount if requested_amount else 30_000_000
            }


# -----------------------------
# 하위 호환 디스패처 (기존 함수 유지)
# -----------------------------
# 전역 인스턴스 생성(1회 로드 캐시)
_PERSONAL_MODEL_SINGLETON = PersonalLoanApprovalModel()
_CORPORATE_MODEL_SINGLETON = CorporateLoanApprovalModel()

def predict_credit_score(customer_data: Dict[str, Any], loan_data: Dict[str, Any], customer_type: str = 'personal') -> Dict[str, Any]:
    """
    기존 코드와 같은 시그니처.
    내부적으로 클래스 인스턴스를 호출하도록 변경.
    """
    try:
        if customer_type == 'corporate':
            return _CORPORATE_MODEL_SINGLETON.predict(customer_data, loan_data)
        else:
            return _PERSONAL_MODEL_SINGLETON.predict(customer_data, loan_data)
    except Exception as e:
        logger.error(f"[공통] 예측 디스패치 오류: {e}")
        requested_amount = BaseApprovalModel._parse_number(loan_data.get('amount', 0))
        return {
            'credit_score': 750,
            'credit_rating': 'B',
            'approval_status': 'approved',
            'recommended_limit': requested_amount if requested_amount else 30_000_000
        }
