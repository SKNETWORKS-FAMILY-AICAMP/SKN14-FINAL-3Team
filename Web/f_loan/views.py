from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.template.loader import render_to_string
import json
import logging
import plotly.graph_objects as go
import plotly.express as px
import plotly.utils
from datetime import datetime

from f_customer.models import Customer, CustomerPerson, CustomerCorporate
from .models import LoanProduct
from .ml import inference # ML 모듈 임포트

logger = logging.getLogger(__name__)

def create_credit_score_chart(score):
    """고급 신용점수 원형 차트 생성"""
    try:
        # score가 문자열일 경우를 대비해 숫자형으로 변환
        numeric_score = int(score)
    except (ValueError, TypeError):
        numeric_score = 0 # 변환 실패 시 기본값

    percentage = numeric_score / 1000 * 100
    
    fig = go.Figure(go.Pie(
        values=[percentage, 100 - percentage],
        hole=0.65,
        marker=dict(
            colors=[
                'rgba(16, 185, 129, 0.9)',  # 메인 색상
                'rgba(243, 244, 246, 0.3)'  # 배경 색상
            ],
            line=dict(
                color='rgba(255, 255, 255, 0.8)',
                width=3
            )
        ),
        textinfo='none',
        hoverinfo='none',
        showlegend=False,
        rotation=90,
        direction='clockwise'
    ))
    
    # 점수 텍스트
    fig.add_annotation(
        text=f"{numeric_score}",
        x=0.5, y=0.55,
        font=dict(
            size=20,
            color='#1f2937',
            family='Arial, sans-serif'
        ),
        showarrow=False
    )
    
    # "점" 텍스트
    fig.add_annotation(
        text="점",
        x=0.5, y=0.4,
        font=dict(
            size=12,
            color='#6b7280',
            family='Arial, sans-serif'
        ),
        showarrow=False
    )
    
    fig.update_layout(
        width=140,
        height=140,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return plotly.utils.PlotlyJSONEncoder().encode(fig)

def create_progress_chart(data):
    """프로그레스 바 차트 생성"""
    labels = list(data.keys())
    values = list(data.values())
    
    # 색상 매핑
    colors = []
    for value in values:
        if value >= 80:
            colors.append('#10b981')  # 녹색
        elif value >= 50:
            colors.append('#f59e0b')  # 주황색
        else:
            colors.append('#ef4444')  # 빨간색
    
    fig = go.Figure(data=[
        go.Bar(
            x=labels,
            y=values,
            marker_color=colors,
            text=[f"{v}%" for v in values],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        height=200,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False, range=[0, 100])
    )
    
    return plotly.utils.PlotlyJSONEncoder().encode(fig)

def create_risk_analysis_chart(customer_data, loan_data, prediction_result):
    """DB 데이터 기반 위험도 분석 레이더 차트 생성"""
    
    # 1. 데이터 정규화 (0-100점 척도로 변환)
    def normalize(value, min_val, max_val, invert=False):
        # 0으로 나누는 경우 방지
        if (max_val - min_val) == 0:
            return 50.0
        score = max(0, min(100, ((value - min_val) / (max_val - min_val)) * 100))
        return 100 - score if invert else score

    # 2. 지표별 점수 계산
    # 모든 입력을 안전하게 숫자형으로 변환하고 기본값 설정
    try:
        annual_income = float(customer_data.get('annual_income', 0))
    except (ValueError, TypeError):
        annual_income = 0.0
    
    try:
        requested_amount = float(loan_data.get('amount', 0))
    except (ValueError, TypeError):
        requested_amount = 0.0

    try:
        # 'loan_data'에서 'interest_rate'를 가져오도록 수정
        interest_rate = float(loan_data.get('interest_rate', 10.0)) # 기본값 10%
    except (ValueError, TypeError):
        interest_rate = 10.0

    # 신용점수: 1000점 만점
    try:
        raw_credit_score = int(prediction_result.get('credit_score', 0))
    except (ValueError, TypeError):
        raw_credit_score = 0

    # 수입 대비 대출률 계산
    loan_to_income_ratio = (requested_amount / annual_income) if annual_income > 0 else 999.0

    # 각 변수를 0-100점 척도로 정규화
    # 값이 클수록 좋은 경우: normalize(value, min, max)
    # 값이 작을수록 좋은 경우: normalize(value, min, max, invert=True)
    income_score = normalize(annual_income, 20000000, 150000000) # 연소득 2천만원 ~ 1.5억원 기준
    loan_amount_score = normalize(requested_amount, 1000000, 500000000, invert=True) # 대출 신청 금액 1백만원 ~ 5억원 기준 (적을수록 좋음)
    interest_rate_score = normalize(interest_rate, 2.5, 15.0, invert=True) # 대출 금리 2.5% ~ 15% 기준 (낮을수록 좋음)
    loan_to_income_score = normalize(loan_to_income_ratio, 0.1, 2.0, invert=True) # 수입 대비 대출률 10% ~ 200% 기준 (낮을수록 좋음)
    credit_score_normalized = normalize(raw_credit_score, 300, 1000) # 신용점수 300점 ~ 1000점 기준

    # 요청하신 변수명으로 카테고리 설정
    categories = ['수입', '요청 대출금', '대출 금리', '수입 대비 대출률', '신용 점수']
    values = [income_score, loan_amount_score, interest_rate_score, loan_to_income_score, credit_score_normalized]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=[0, 72, 144, 216, 288],
        fill='toself',
        name='위험도 분석',
        fillcolor='rgba(16,185,129,0.25)',
        line=dict(color='rgba(16,185,129,0.8)', width=2)
    ))

    fig.update_layout(
        polar=dict(
            bgcolor='white',
            gridshape='linear',
            radialaxis=dict(
                visible=True, range=[0, 100],
                linecolor='black', linewidth=1,
                gridcolor='lightgray'
            ),
            angularaxis=dict(
                tickmode='array',
                tickvals=[0, 72, 144, 216, 288],
                ticktext=categories,
                tickfont=dict(size=11, color='rgba(0,0,0,0.8)'),
                linecolor='black',
                gridcolor='lightgray',
                layer="above traces"
            )
        ),
        showlegend=False,
        margin=dict(l=60, r=60, t=60, b=60),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        width=300,
        height=250,
        font=dict(size=12)
    )
    return plotly.utils.PlotlyJSONEncoder().encode(fig)

def create_corporate_risk_analysis_chart(diagnostics):
    """기업 진단 데이터 기반 위험도 분석 레이더 차트 생성 (Plotly)"""
    
    # 1. 데이터 정규화 함수 (JS와 동일한 로직)
    def clamp(v, a, b): return max(a, min(b, v))
    def scaleZ(z): 
        if z <= 1.0: return 10
        if z <= 1.81: return 10 + 40 * (z - 1.0) / 0.81
        if z <= 2.99: return 50 + 40 * (z - 1.81) / 1.18
        return min(100, 90 + 10 * (z - 2.99))
    def scaleCurrent(x):
        if x <= 0.8: return 20 * (x / 0.8)
        if x <= 1.0: return 20 + 40 * (x - 0.8) / 0.2
        if x <= 2.0: return 60 + 40 * (x - 1.0) / 1.0
        return 100
    def scaleQuick(x):
        if x <= 0.5: return 30 * (x / 0.5)
        if x <= 1.0: return 30 + 40 * (x - 0.5) / 0.5
        if x <= 1.5: return 70 + 30 * (x - 1.0) / 0.5
        return 100
    def scaleROA(x): return clamp((x * 100 + 5) * 5, 0, 100) # 15%일 때 100점
    def scaleSalesGrowth(x): return clamp(x * 100 * 2, 0, 100) # 50% 성장시 100점
    def scaleAssetTurnover(x): return clamp(x * 50, 0, 100) # 2.0일 때 100점

    # 2. 지표별 점수 계산
    z_score = float(diagnostics.get('altman_z', 0))
    current_ratio = float(diagnostics.get('current_ratio', 0))
    debt_to_asset = float(diagnostics.get('debt_to_asset_ratio', 0))
    roa = float(diagnostics.get('roa', 0))
    sales_growth = float(diagnostics.get('sales_growth', 0))
    asset_turnover = float(diagnostics.get('asset_turnover', 0))

    # 수익성, 안정성, 유동성, 성장성, 활동성, 종합건전성
    roa_score = scaleROA(roa)
    solvency_score = 100 * (1 - clamp(debt_to_asset, 0, 1))
    liquidity_score = scaleCurrent(current_ratio)
    growth_score = scaleSalesGrowth(sales_growth)
    activity_score = scaleAssetTurnover(asset_turnover)
    z_score_normalized = scaleZ(z_score)

    categories = ['수익성', '안정성', '유동성', '성장성', '활동성', '종합건전성']
    values = [
        roa_score, 
        solvency_score, 
        liquidity_score, 
        growth_score, 
        activity_score, 
        z_score_normalized
    ]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='위험도 분석'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        showlegend=False,
        width=340,
        height=320,
        margin=dict(l=60, r=60, t=60, b=60),
    )
    return plotly.utils.PlotlyJSONEncoder().encode(fig)

def credit_assessment_view(request):
    """여신 심사 페이지"""
    return render(request, 'credit_assessment/credit_assessment.html')

@csrf_exempt
@require_http_methods(["POST"])
def check_customer(request):
    """개인 고객 정보 확인 API"""
    try:
        data = json.loads(request.body)
        customer_name = data.get('customer_name', '').strip()
        customer_rrn = data.get('customer_rrn', '').strip()
        customer_phone = data.get('customer_phone', '').strip()
        
        logger.info(f"개인 고객 정보 조회 요청: 이름={customer_name}, 주민번호={customer_rrn}, 연락처={customer_phone}")

        if not customer_name or not customer_rrn or not customer_phone:
            return JsonResponse({'success': False, 'message': '고객명, 주민번호, 연락처는 필수 입력 항목입니다.'})

        cleaned_customer_name = customer_name.replace(' ', '')
        if len(cleaned_customer_name) > 1:
            # NOTE: DB에는 성이 first_name, 이름이 last_name으로 저장되어 있음
            parsed_first_name = cleaned_customer_name[0]
            parsed_last_name = cleaned_customer_name[1:]
        else:
            logger.warning(f"유효하지 않은 고객명 형식: {customer_name}")
            return JsonResponse({'success': False, 'customer_found': False, 'message': '올바른 고객명을 입력해주세요.'})

        try:
            customer = Customer.objects.select_related('person').get(
                person__first_name=parsed_first_name,
                person__last_name=parsed_last_name,
                person__rrn=customer_rrn.replace('-', ''),
                person__mobile=customer_phone.replace('-', '')
            )
            person = customer.person
            logger.info(f"✅ [DB] 개인 고객 정보 발견: {person.first_name}{person.last_name} (ID: {customer.seq_id})")
        except (Customer.DoesNotExist, CustomerPerson.DoesNotExist):
            logger.warning(f"❌ [DB] 일치하는 개인 고객 정보 없음: 이름={customer_name}, 주민번호={customer_rrn}")
            return JsonResponse({'success': False, 'customer_found': False, 'message': '일치하는 고객 정보가 없습니다.'})

        from datetime import date # 나이 계산
        today = date.today()
        birth_year_prefix = '19'
        if person.rrn[6] in ['3', '4', '7', '8']:
            birth_year_prefix = '20'
        birth_year = int(birth_year_prefix + person.rrn[:2])
        age = today.year - birth_year - ((today.month, today.day) < (int(person.rrn[2:4]), int(person.rrn[4:6])))

        customer_data = {
            'id': customer.seq_id,
            'full_name': f"{person.first_name}{person.last_name}",
            'first_name': person.first_name,
            'last_name': person.last_name,
            'rrn': f"{person.rrn[:6]}-{person.rrn[6:]}" if person.rrn else '정보 없음',
            'phone': f"{person.mobile[:3]}-{person.mobile[3:7]}-{person.mobile[7:]}" if person.mobile and len(person.mobile) == 11 else person.mobile or '정보 없음',
            'email': person.email or '',
            'age': age,
            'gender': '남성' if person.gender == 0 else '여성',
            'education_level': person.education_level.name if person.education_level else '정보 없음',
            'company_name': person.industry_code.name if person.industry_code else '정보 없음',  # 실제 직종 정보
            'job_title': person.industry_code.name if person.industry_code else '정보 없음',
            'years_of_service': int(person.work_experience_years) if person.work_experience_years is not None else 0,
            'housing_status': person.housing_status.name if person.housing_status else '정보 없음',
            'annual_income': person.income_annual if person.income_annual is not None else 0,
            'account_number': person.account_number,
        }
        
        return JsonResponse({'success': True, 'customer_found': True, 'customer': customer_data})
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': '잘못된 요청 데이터입니다.'
        })
    except Exception as e:
        logger.error(f"고객 정보 조회 중 오류 발생: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': '고객 정보 조회 중 오류가 발생했습니다.'
        })

@csrf_exempt
@require_http_methods(["POST"])
def check_corporate_customer(request):
    """기업 고객 정보 확인 API"""
    try:
        data = json.loads(request.body)
        legal_name = data.get('legal_name', '').strip()
        biz_reg_no_masked = data.get('biz_reg_no_masked', '').strip()
        mobile = data.get('mobile', '').strip()

        logger.info(f"기업 고객 정보 조회 요청: 법인명(대표자명)={legal_name}, 사업자번호={biz_reg_no_masked}, 대표연락처={mobile}")

        if not legal_name or not biz_reg_no_masked or not mobile:
            return JsonResponse({'success': False, 'message': '대표자명, 사업자등록번호, 대표 연락처는 필수 입력 항목입니다.'})

        try:
            # 1. 입력값 정제
            import re
            def clean_company_name(name):
                # (주), (유) 등과 공백, 특수문자 제거
                return re.sub(r'[\s\(\)（）주유사재법]', '', name, flags=re.IGNORECASE)

            clean_biz_reg_no = biz_reg_no_masked.replace('-', '')

            # 2. DB에서 조회 (사업자번호 또는 정제된 법인명으로)
            # 사업자번호가 고유하므로 우선적으로 조회
            corp = CustomerCorporate.objects.filter(biz_reg_no_masked=clean_biz_reg_no).first()

            if not corp:
                # 사업자번호로 못찾으면, 정제된 법인명으로 재시도
                # 이 방식은 동명이 회사가 있을 수 있어 완벽하지 않지만, 조회 성공률을 높임
                # DB의 모든 legal_name을 가져와서 파이썬에서 정제 후 비교
                clean_legal_name = clean_company_name(legal_name)
                all_corps = CustomerCorporate.objects.all()
                corp = next((c for c in all_corps if clean_company_name(c.legal_name) == clean_legal_name), None)

            if not corp:
                raise CustomerCorporate.DoesNotExist

            customer = corp.customer
            logger.info(f"✅ [DB] 기업 고객 정보 발견: {corp.customer.display_name} (ID: {customer.seq_id})")

            customer_data = {
                'id': customer.seq_id,
                'full_name': corp.customer.display_name,
                'ceo_name': corp.legal_name, # 조회된 legal_name을 ceo_name으로 매핑
                'brn': f"{corp.biz_reg_no_masked[:3]}-{corp.biz_reg_no_masked[3:5]}-{corp.biz_reg_no_masked[5:]}" if corp.biz_reg_no_masked else '정보 없음',
                'phone': f"{corp.mobile[:3]}-{corp.mobile[3:7]}-{corp.mobile[7:]}" if corp.mobile and len(corp.mobile) == 11 else corp.mobile or '정보 없음',
                'email': getattr(corp, 'email', '') or '', # email 필드가 없을 수 있으므로 getattr 사용
                'industry_type': corp.industry_code.name if corp.industry_code else '정보 없음',
                'company_name': corp.customer.display_name,
                'job_title': '대표',
                'total_assets': corp.total_assets,
                'total_liabilities': corp.total_liabilities,
                'net_income': corp.net_income,
                'ebit': corp.ebit,
                'net_sales': corp.net_sales,
                'retained_earnings': corp.retained_earnings,
                'current_assets': corp.current_assets,
                'current_liabilities': corp.total_current_liabilities,
            }
            return JsonResponse({'success': True, 'customer_found': True, 'customer': customer_data})

        except CustomerCorporate.DoesNotExist:
            logger.warning(f"❌ [DB] 일치하는 기업 고객 정보 없음: 법인명(대표자명)={legal_name}, 사업자번호={biz_reg_no_masked}")
            return JsonResponse({'success': False, 'customer_found': False, 'message': '일치하는 기업 고객 정보가 없습니다.'})

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': '잘못된 요청 데이터입니다.'
        })
    except Exception as e:
        logger.error(f"기업 고객 정보 조회 중 오류 발생: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': '기업 고객 정보 조회 중 오류가 발생했습니다.'
        })

@csrf_exempt
@require_http_methods(["POST"])
def get_loan_products(request):
    """대출 목적에 따른 대출 상품 조회 API"""
    try:
        data = json.loads(request.body)
        loan_purpose = data.get('loan_purpose', '')
        
        if not loan_purpose:
            return JsonResponse({
                'success': False,
                'message': '대출 목적을 선택해주세요.'
            })
        
        # 해당 목적의 활성화된 대출 상품 조회
        products = LoanProduct.objects.filter(
            purpose=loan_purpose,
            is_active=True
        ).order_by('name')
        
        products_data = []
        for product in products:
            products_data.append({
                'id': product.id,
                'name': product.name,
                'purpose': product.purpose,
                'min_amount': product.min_amount,
                'max_amount': product.max_amount,
                'min_period': product.min_period,
                'max_period': product.max_period,
                'interest_rate': float(product.interest_rate),
                'description': product.description,
            })
        
        return JsonResponse({
            'success': True,
            'products': products_data
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': '잘못된 요청 데이터입니다.'
        })
    except Exception as e:
        logger.error(f"대출 상품 조회 중 오류 발생: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': '대출 상품 조회 중 오류가 발생했습니다.'
        })

@csrf_exempt
@require_http_methods(["POST"])
def assess_personal_credit(request):
    """개인 고객 신용평가 API"""
    try:
        data = json.loads(request.body)
        customer_data = data.get('customer_data', {})
        loan_data = data.get('loan_data', {})
        
        logger.info(f"개인 신용평가 요청: {customer_data.get('full_name', 'Unknown')}")
        
        # ML 모델로 신용점수 예측
        prediction_result = inference.predict_credit_score(customer_data, loan_data, customer_type='personal')
        
        credit_score = prediction_result.get('credit_score', 750)
        
        # 개인용 차트 및 분석 데이터 생성
        credit_score_chart = create_credit_score_chart(credit_score)
        financial_indicators = {'부채비율': 50, '소득 안정성': 70, '상환능력': 80, '신용이력': 90, '현금보유비율': 60, '자산증가율': 75}
        progress_chart = create_progress_chart(financial_indicators)
        risk_analysis_chart = create_risk_analysis_chart(customer_data, loan_data, prediction_result)
        risk_matrix = generate_risk_matrix(credit_score)
        ai_report = generate_recommendation(prediction_result, customer_data, loan_data)
        
        response_data = {
            'success': True,
            'assessment_result': {
                'approval_status': prediction_result['approval_status'],
                'credit_score': prediction_result['credit_score'],
                'credit_rating': prediction_result['credit_rating'],
                'recommended_limit': prediction_result['recommended_limit'],
                'credit_score_chart': credit_score_chart,
                'progress_chart': progress_chart,
                'risk_analysis_chart': risk_analysis_chart,
                'financial_indicators': financial_indicators,
                'risk_matrix': risk_matrix,
                'ai_report': ai_report,
                'diagnostics': prediction_result.get('diagnostics', {})
            }
        }
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': '잘못된 요청 데이터입니다.'})
    except Exception as e:
        logger.error(f"개인 신용평가 중 오류 발생: {str(e)}")
        return JsonResponse({'success': False, 'message': '개인 신용평가 중 오류가 발생했습니다.'})

@csrf_exempt
@require_http_methods(["POST"])
def assess_corporate_credit(request):
    """기업 고객 신용평가 API"""
    try:
        data = json.loads(request.body)
        customer_data = data.get('customer_data', {})
        loan_data = data.get('loan_data', {})
        
        logger.info(f"기업 신용평가 요청: {customer_data.get('full_name', 'Unknown')}")
        
        # ML 모델로 신용점수 예측
        prediction_result = inference.predict_credit_score(customer_data, loan_data, customer_type='corporate')
        
        credit_score = prediction_result.get('credit_score', 750)
        
        # 기업용 차트 및 분석 데이터 생성 (JS에서 대부분 처리하므로 필요한 최소 데이터만 전달)
        # ECharts를 JS에서 사용하므로, Plotly 차트 데이터는 생성하지 않음
        credit_score_chart = create_credit_score_chart(credit_score)
        
        response_data = {
            'success': True,
            'assessment_result': {
                'approval_status': prediction_result['approval_status'],
                'credit_score': prediction_result['credit_score'],
                'credit_score_chart': credit_score_chart, # JS fallback을 위해 추가
                'credit_rating': prediction_result['credit_rating'],
                'recommended_limit': prediction_result['recommended_limit'],
                'diagnostics': prediction_result.get('diagnostics', {})
            }
        }
        
        # JS에서 Plotly fallback을 위해 기업용 레이더 차트 데이터 추가
        response_data['assessment_result']['risk_analysis_chart'] = create_corporate_risk_analysis_chart(prediction_result.get('diagnostics', {}))
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': '잘못된 요청 데이터입니다.'})
    except Exception as e:
        logger.error(f"기업 신용평가 중 오류 발생: {str(e)}")
        return JsonResponse({'success': False, 'message': '기업 신용평가 중 오류가 발생했습니다.'})

def generate_risk_matrix(credit_score):
    """신용점수 기반 리스크 매트릭스 생성"""
    try:
        # credit_score가 문자열일 경우를 대비해 숫자형으로 변환
        numeric_score = int(credit_score)
    except (ValueError, TypeError):
        numeric_score = 0 # 변환 실패 시 기본값

    if numeric_score >= 800:
        return [
            {'level': 'low', 'type': '신용위험'},
            {'level': 'low', 'type': '시장위험'},
            {'level': 'low', 'type': '유동성위험'},
            {'level': 'low', 'type': '운영위험'},
            {'level': 'low', 'type': '법률위험'},
            {'level': 'low', 'type': '평판위험'}
        ]
    elif numeric_score >= 600:
        return [
            {'level': 'low', 'type': '신용위험'},
            {'level': 'medium', 'type': '시장위험'},
            {'level': 'low', 'type': '유동성위험'},
            {'level': 'low', 'type': '운영위험'},
            {'level': 'medium', 'type': '법률위험'},
            {'level': 'low', 'type': '평판위험'}
        ]
    else:
        return [
            {'level': 'high', 'type': '신용위험'},
            {'level': 'high', 'type': '시장위험'},
            {'level': 'high', 'type': '유동성위험'},
            {'level': 'medium', 'type': '운영위험'},
            {'level': 'high', 'type': '법률위험'},
            {'level': 'medium', 'type': '평판위험'}
        ]

def generate_recommendation(prediction_result, customer_data, loan_data):
    """AI 추천사항 생성"""
    # prediction_result에서 값을 안전하게 가져오고, credit_score를 정수형으로 변환
    try:
        credit_score = int(prediction_result.get('credit_score', 0))
    except (ValueError, TypeError):
        credit_score = 0  # 변환 실패 시 기본값

    approval_status = prediction_result.get('approval_status', 'rejected')
    credit_rating = prediction_result.get('credit_rating', 'D')
    
    # 분석 상세 내용 생성
    analysis_details = [
        {'label': '신용점수 분석', 'value': f"{credit_score}점", 'description': f"상위 {100 - (credit_score // 10)}% 내 {credit_rating} 등급"},
        {'label': '상환능력 평가', 'value': "양호" if customer_data.get('age', 30) < 50 else "보통", 'description': f"고객 연령({customer_data.get('age', 0)}세) 고려 시 안정적"},
        {'label': '소득 안정성', 'value': "우수" if customer_data.get('years_of_service', 0) >= 5 else "보통", 'description': f"근속년수({customer_data.get('years_of_service', 0)}년) 기반"},
        {'label': '신용 이력', 'value': "양호", 'description': "과거 대출 연체 이력 없음 (가정)"}
    ]
    
    if approval_status == 'approved':
        summary_title = "대출 승인 권장"
        summary_description = f"AI 기반 머신러닝 모델 분석 결과, <strong>신용점수 {credit_score}점({credit_rating} 등급)</strong>으로 안정적인 상환 능력이 확인되었습니다. " \
                              f"고객의 연령, 근속년수, 주택상태 등 주요 지표가 양호하여 대출 승인을 권장합니다."
        
        recommendations = [
            f"신청 금액 {loan_data.get('amount', 0):,}원 승인 권장 (요청 대비 100% 승인)",
            "우대 금리 적용 가능 (기준금리 + 1.5%p)",
            "담보 제출 불필요 (신용 대출 기준 충족)"
        ]
        warnings = []
        
        if credit_score >= 800:
            recommendations.append("빠른 승인 처리 예상 (1-2일 내)")
        else:
            warnings.append("신용점수 추가 관리를 통해 향후 더 나은 금리 조건 가능")

        if customer_data.get('housing_status') != '자가':
            warnings.append(f"주택 상태({customer_data.get('housing_status')}) 고려, 안정성 확보 필요")
        
    else:
        summary_title = "대출 승인 주의"
        summary_description = f"현재 신용상태를 고려할 때 대출 승인에 신중한 검토가 필요합니다. " \
                              f"<strong>신용점수 {credit_score}점</strong>으로, 일부 리스크 요인이 발견되었습니다. " \
                              f"고객과의 심층 면담을 통해 리스크 요인을 상세히 파악하는 것을 권장합니다."
        recommendations = [
            "추가 서류(소득 증빙, 재직 증명) 요청",
            "보증인 또는 담보 설정 조건부 승인 고려"
        ]
        warnings = [
            "대출 한도 하향 조정 필요",
            "연체 이력 또는 과다 부채 여부 재확인"
        ]

    return {
        'summary_title': summary_title,
        'summary_description': summary_description,
        'analysis_details': analysis_details,
        'recommendations': recommendations,
        'warnings': warnings
    }

@require_http_methods(["POST"])
def generate_pdf_report(request):
    """PDF 보고서 생성 API"""
    try:
        logger.info("PDF 보고서 생성 요청 시작")
        
        data = json.loads(request.body)
        customer_name = data.get('customer_name', '')
        third_column_html = data.get('third_column_html', '')
        
        logger.info(f"요청 데이터 - 고객명: {customer_name}, HTML 길이: {len(third_column_html) if third_column_html else 0}")
        
        if not customer_name or not third_column_html:
            logger.warning("필수 데이터 누락")
            return JsonResponse({
                'success': False,
                'message': '고객명과 심사 결과 데이터가 필요합니다.'
            })
        
        # 현재 날짜 생성
        report_date = datetime.now().strftime('%Y년 %m월 %d일')
        logger.info(f"보고서 생성일: {report_date}")
        
        # 세션에서 사용자 정보 가져오기
        logger.info(f"세션 키: {request.session.session_key}")
        logger.info(f"세션 데이터: {dict(request.session)}")
        
        # 세션에서 사용자 정보 확인
        user_id = request.session.get('user_id')
        user_name = request.session.get('user_name')
        employee_id = request.session.get('employee_id')
        
        logger.info(f"세션 사용자 ID: {user_id}")
        logger.info(f"세션 사용자명: {user_name}")
        logger.info(f"세션 사번: {employee_id}")
        
        if user_id and user_name:
            # 세션에서 사용자 정보가 있으면 DB에서 상세 정보 조회
            try:
                from f_user.models import User
                user = User.objects.get(seq_id=user_id)
                logger.info(f"DB에서 사용자 조회 성공: {user.name}")
                
                # 부서와 직급 정보 가져오기
                department_name = user.department.name if user.department else '여신심사부'
                position_name = user.position.name if user.position else '과장'
                phone = user.mobile if user.mobile else '02-1234-5678'
                
                officer_info = {
                    'name': user.name,
                    'department': department_name,
                    'position': position_name,
                    'phone': phone
                }
                logger.info("DB에서 사용자 정보를 성공적으로 가져왔습니다")
                
            except Exception as e:
                logger.error(f"DB에서 사용자 정보 조회 실패: {str(e)}")
                # DB 조회 실패 시 세션 정보만 사용
                officer_info = {
                    'name': user_name,
                    'department': '여신심사부',
                    'position': '과장',
                    'phone': '02-1234-5678'
                }
                logger.info("세션 정보로 사용자 정보를 설정했습니다")
        else:
            # 세션에 사용자 정보가 없으면 기본값 사용
            officer_info = {
                'name': '시스템 관리자',
                'department': '여신심사부',
                'position': '과장',
                'phone': '02-1234-5678'
            }
            logger.info("세션에 사용자 정보가 없어 기본값을 사용합니다")
        
        logger.info(f"담당자 정보: {officer_info}")
        
        # PDF 템플릿 렌더링
        logger.info("PDF 템플릿 렌더링 시작")
        pdf_html = render_to_string('credit_assessment/pdf_report.html', {
            'customer_name': customer_name,
            'report_date': report_date,
            'content': third_column_html,
            'officer_info': officer_info
        })
        
        logger.info(f"PDF 템플릿 렌더링 완료, HTML 길이: {len(pdf_html)}")
        
        return JsonResponse({
            'success': True,
            'pdf_html': pdf_html
        })
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON 디코딩 오류: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': '잘못된 요청 데이터입니다.'
        })
    except Exception as e:
        logger.error(f"PDF 보고서 생성 중 오류 발생: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'message': f'PDF 보고서 생성 중 오류가 발생했습니다: {str(e)}'
        })