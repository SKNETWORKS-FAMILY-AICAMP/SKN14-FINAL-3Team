from django.core.management.base import BaseCommand
from faker import Faker
from django.utils import timezone
import random

# ==== Import Models ====
from f_user.models import User, UDepartment, UPosition
from f_customer.models import (
    Customer, CustomerPerson, CustomerCorporate,
    CIndustryCode, CEducationLevel, CHousingStatus
)
from f_common.models import UncBankLocation, UncEmploymentType
from f_document.models import Document, DocumentBinding
from f_chatbot.models import (
    UChatbotHistory, UChatbotSession,
    ChatbotRetrivalEvent, ChatbotRetrievedChunk
)
from f_calendar.models import UCalendarEvent, UEventAttendees
from f_todo.models import UTodoList
from f_loan.models import LoanAssessment


class Command(BaseCommand):
    help = "Seed all dummy data for development"

    def handle(self, *args, **kwargs):
        fake = Faker("ko_KR")

        # ========== 1. 공통 테이블 ==========
        dept, _ = UDepartment.objects.get_or_create(
            code="SALES",
            defaults={"name": "영업부"}
        )

        pos, _ = UPosition.objects.get_or_create(
            code="MGR",
            defaults={"name": "Manager"}
        )

        bank, _ = UncBankLocation.objects.get_or_create(
            branch_code="SEOUL001",
            defaults={
                "name": "서울중앙지점",
                "address": fake.address(),
                "phone": fake.phone_number(),
            }
        )

        emp_type, _ = UncEmploymentType.objects.get_or_create(
            code="FT",
            defaults={"name": "정규직", "description": "주 5일, 정규직 근무"}
        )

        edu, _ = CEducationLevel.objects.get_or_create(
            code="UNI",
            defaults={"name": "대학교", "description": "4년제 대학"}
        )

        house, _ = CHousingStatus.objects.get_or_create(
            code="OWNED",
            defaults={"name": "자가", "description": "자가 주택 보유"}
        )

        industry, _ = CIndustryCode.objects.get_or_create(
            code="IT01",
            defaults={"name": "정보기술 서비스"}
        )

        # ========== 2. User ==========
        users = []
        for i in range(10):
            user, _ = User.objects.get_or_create(
                employee_id=f"S23{i:04d}",
                defaults={
                    "email": fake.unique.email(),
                    "password": "test1234",  # TODO: 실제 환경에서는 해싱 필요
                    "name": fake.name(),
                    "position": pos,
                    "department": dept,
                    "manager": None,
                    "bank_location": bank,
                    "hire_date": fake.date_between(start_date="-5y", end_date="today"),
                    "mobile": fake.phone_number(),
                    "birthdate": fake.date_of_birth(minimum_age=20, maximum_age=60),
                    "employment_status": "ON_DUTY",
                    "employment_type": emp_type,
                    "is_active": True,
                    "created_at": timezone.now(),
                    "updated_at": timezone.now(),
                }
            )
            users.append(user)

        # ========== 3. Customer ==========
        for i in range(5):
            customer, _ = Customer.objects.get_or_create(
                display_name=fake.name(),
                customer_type="INDIVIDUAL",
                bank_location=bank,
                defaults={
                    "status": "ACTIVE",
                    "risk_segment": "RETAIL",
                }
            )
            CustomerPerson.objects.get_or_create(
                customer=customer,
                defaults={
                    "first_name": fake.last_name(),
                    "last_name": fake.first_name(),
                    "gender": random.choice([0, 1]),
                    "rrn": fake.ssn(),
                    "mobile": fake.phone_number(),
                    "email": fake.unique.email(),
                    "account_number": fake.iban(),
                    "account_amount": fake.pydecimal(left_digits=7, right_digits=2),
                    "education_level": edu,
                    "housing_status": house,
                    "income_annual": fake.pydecimal(left_digits=6, right_digits=0),
                    "work_experience_years": random.randint(0, 20),
                    "employment_type": emp_type,
                    "industry_code": industry,
                    "has_delinquency": random.choice([0, 1]),
                    "credit_history_length": random.randint(0, 20),
                    "credit_rating": random.randint(1, 10),
                }
            )

        for i in range(3):
            customer, _ = Customer.objects.get_or_create(
                display_name=fake.company(),
                customer_type="CORPORATE",
                bank_location=bank,
                defaults={
                    "status": "ACTIVE",
                    "risk_segment": "SME",
                }
            )
            CustomerCorporate.objects.get_or_create(
                customer=customer,
                defaults={
                    "industry_code": industry,
                    "legal_name": fake.company(),
                    "biz_reg_no_masked": fake.bothify("##########"),
                    "incorporation_date": fake.date_between(start_date="-30y", end_date="today"),
                    "employees_count": random.randint(10, 500),
                    "mobile": fake.phone_number(),
                    "roa": fake.pydecimal(left_digits=2, right_digits=2),
                    "net_profit_margin": fake.pydecimal(left_digits=2, right_digits=2),
                    "operating_roa": fake.pydecimal(left_digits=2, right_digits=2),
                    "operating_margin": fake.pydecimal(left_digits=2, right_digits=2),
                    "current_ratio": fake.pydecimal(left_digits=3, right_digits=2),
                    "quick_ratio": fake.pydecimal(left_digits=3, right_digits=2),
                    "debt_ratio": fake.pydecimal(left_digits=3, right_digits=2),
                    "equity_ratio": fake.pydecimal(left_digits=3, right_digits=2),
                    "equity_to_debt_ratio": fake.pydecimal(left_digits=3, right_digits=2),
                    "long_term_debt_to_equity_ratio": fake.pydecimal(left_digits=3, right_digits=2),
                    "asset_turnover": fake.pydecimal(left_digits=2, right_digits=2),
                }
            )

        # ========== 4. LoanAssessment ==========
        for i in range(5):
            LoanAssessment.objects.get_or_create(
                customer_id=random.randint(1, Customer.objects.count()),
                defaults={
                    "customer_type": random.choice(["INDIVIDUAL", "CORPORATE"]),
                    "product_type": random.choice(["MORTGAGE", "CREDIT_LOAN", "CARD", "BIZ_LOAN"]),
                    "requested_amount": fake.pydecimal(left_digits=7, right_digits=0),
                    "requested_term": random.randint(6, 60),
                    "purpose": fake.sentence(),
                    "created_by": random.choice(users),
                    "approval": random.choice([0, 1, 2]),
                }
            )

        # ========== 5. Document ==========
        for i in range(5):
            doc, _ = Document.objects.get_or_create(
                file_name=f"report{i+1}.pdf",
                defaults={
                    "title": f"문서 {i+1}",
                    "storage_path": f"/docs/report{i+1}.pdf",
                    "created_by": random.choice(users),
                }
            )
            DocumentBinding.objects.get_or_create(
                document=doc,
                defaults={
                    "bind_type": random.choice(["CHAT", "REVIEW"]),
                    "bind_id": random.randint(100, 200),
                }
            )
