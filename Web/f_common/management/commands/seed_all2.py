import random
from django.core.management.base import BaseCommand
from faker import Faker
from django.utils import timezone

from f_user.models import User, UDepartment, UPosition
from f_customer.models import Customer, CustomerPerson, CustomerCorporate
from f_common.models import (
    UncBankLocation,
    UncEmploymentType,
    CIndustryCode,
    CEducationLevel,
    CHousingStatus,
)
from f_document.models import Document, DocumentBinding
from f_chatbot.models import UChatbotHistory, UChatbotSession
from f_calendar.models import UCalendarEvent, UEventAttendees
from f_todo.models import UTodoList
from f_loan.models import LoanAssessment, LoanProduct


class Command(BaseCommand):
    help = "Seed all dummy data for development with increased volume and variety."

    def handle(self, *args, **kwargs):
        fake = Faker("ko_KR")

        # 1) Lookup Tables
        # Departments
        departments_data = [
            {"code": "SALES", "name": "영업부"},
            {"code": "HR", "name": "인사부"},
            {"code": "IT", "name": "IT개발부"},
            {"code": "FINANCE", "name": "재무부"},
            {"code": "MARKETING", "name": "마케팅부"},
        ]
        departments = []
        for data in departments_data:
            dept, _ = UDepartment.objects.get_or_create(code=data["code"], defaults={"name": data["name"]})
            departments.append(dept)

        # Positions
        positions_data = [
            {"code": "STAFF", "name": "사원"},
            {"code": "SENIOR", "name": "대리"},
            {"code": "MGR", "name": "과장"},
            {"code": "DIRECTOR", "name": "부장"},
        ]
        positions = []
        for data in positions_data:
            pos, _ = UPosition.objects.get_or_create(code=data["code"], defaults={"name": data["name"]})
            positions.append(pos)

        # Bank Locations
        locations_data = [
            {"branch_code": "SEOUL001", "name": "서울중앙지점"},
            {"branch_code": "BUSAN001", "name": "부산지점"},
            {"branch_code": "INCHEON01", "name": "인천공항지점"},
            {"branch_code": "DAEGU001", "name": "대구지점"},
            {"branch_code": "JEJU001", "name": "제주지점"},
        ]
        banks = []
        for data in locations_data:
            bank, _ = UncBankLocation.objects.get_or_create(
                branch_code=data["branch_code"],
                defaults={"name": data["name"], "address": fake.address(), "phone": fake.phone_number()}
            )
            banks.append(bank)

        # Employment Types
        employment_types_data = [
            {"code": "FT", "name": "정규직", "description": "Full-time position"},
            {"code": "PT", "name": "계약직", "description": "Part-time position"},
            {"code": "INTERN", "name": "인턴", "description": "Internship position"},
        ]
        employment_types = []
        for data in employment_types_data:
            emp_type, _ = UncEmploymentType.objects.get_or_create(
                code=data["code"],
                defaults={"name": data["name"], "description": data["description"]}
            )
            employment_types.append(emp_type)

        # 2) f_user
        users = []
        for i in range(30):
            user, created = User.objects.get_or_create(
                employee_id=f"KB25{i:04d}",
                defaults={
                    "email": f"user{i}@example.com",
                    "password": "test1234",  # 비밀번호를 평문으로 직접 저장
                    "name": fake.name(),
                    "position": random.choice(positions),
                    "department": random.choice(departments),
                    "manager": None,
                    "bank_location": random.choice(banks),
                    "hire_date": fake.date_between(start_date="-5y", end_date="today"),
                    "mobile": fake.phone_number(),
                    "birthdate": fake.date_of_birth(minimum_age=20, maximum_age=60),
                    "employment_status": User.EmploymentStatus.ON_DUTY,
                    "employment_type": random.choice(employment_types),
                    "is_active": True,
                },
            )
            users.append(user)

        # More common lookup tables
        education_levels = []
        for code, name in CEducationLevel.Education.choices:
            edu, _ = CEducationLevel.objects.get_or_create(code=code, defaults={"name": name})
            education_levels.append(edu)

        housing_statuses = []
        for code, name in CHousingStatus.Housing.choices:
            house, _ = CHousingStatus.objects.get_or_create(code=code, defaults={"name": name})
            housing_statuses.append(house)

        # Industry Codes
        industries_data = [
            {"code": "IT01", "name": "정보기술"},
            {"code": "FIN01", "name": "금융 및 보험업"},
            {"code": "MANU01", "name": "제조업"},
            {"code": "SVC01", "name": "서비스업"},
            {"code": "EDU01", "name": "교육 서비스업"},
        ]
        industries = []
        for data in industries_data:
            industry, _ = CIndustryCode.objects.get_or_create(code=data["code"], defaults={"name": data["name"]})
            industries.append(industry)

        # 3) f_customer
        customers = []
        for i in range(30):
            customer, _ = Customer.objects.get_or_create(
                display_name=fake.unique.name(),
                customer_type=Customer.CustomerType.INDIVIDUAL,
                defaults={
                    "bank_location": random.choice(banks),
                    "status": "ACTIVE",
                    "risk_segment": "RETAIL",
                },
            )
            CustomerPerson.objects.get_or_create(
                customer=customer,
                defaults={
                    "first_name": fake.last_name(),
                    "last_name": fake.first_name(),
                    "gender": random.choice([0, 1]),
                    "rrn": fake.unique.ssn(),
                    "mobile": fake.unique.phone_number(),
                    "email": fake.unique.email(),
                    "account_number": f"110-{random.randint(1000,9999)}-{random.randint(100000,999999)}",
                    "account_amount": fake.pydecimal(left_digits=7, right_digits=2),
                    "education_level": random.choice(education_levels),
                    "housing_status": random.choice(housing_statuses),
                    "income_annual": fake.pydecimal(left_digits=6, right_digits=0),
                    "work_experience_years": random.randint(0, 20),
                    "employment_type": random.choice(employment_types),
                    "industry_code": random.choice(industries),
                    "has_delinquency": random.choice([True, False]),
                    "credit_history_length": random.randint(0, 20),
                    "credit_rating": random.randint(1, 10),
                },
            )
            customers.append(customer)

        corp_customers = []
        for i in range(15):
            corp_customer, _ = Customer.objects.get_or_create(
                display_name=fake.unique.company(),
                customer_type=Customer.CustomerType.CORPORATE,
                defaults={
                    "bank_location": random.choice(banks),
                    "status": "ACTIVE",
                    "risk_segment": "SME",
                },
            )
            CustomerCorporate.objects.get_or_create(
                customer=corp_customer,
                defaults={
                    "industry_code": random.choice(industries),
                    "legal_name": fake.unique.company(), # ceo_name 제거
                    "biz_reg_no_masked": f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10000, 99999)}",
                    "incorporation_date": fake.date_between(start_date="-30y", end_date="today"),
                    "employees_count": fake.random_int(min=10, max=500),
                    "mobile": "010-0000-0000", # email 제거
                    "current_assets": fake.pydecimal(left_digits=9, right_digits=2, positive=True),
                    "cost_of_goods_sold": fake.pydecimal(left_digits=9, right_digits=2, positive=True),
                    "ebitda": fake.pydecimal(left_digits=8, right_digits=2),
                    "inventory": fake.pydecimal(left_digits=8, right_digits=2, positive=True),
                    "net_income": fake.pydecimal(left_digits=8, right_digits=2),
                    "net_sales": fake.pydecimal(left_digits=9, right_digits=2, positive=True),
                    "total_assets": fake.pydecimal(left_digits=10, right_digits=2, positive=True),
                    "ebit": fake.pydecimal(left_digits=8, right_digits=2),
                    "gross_profit": fake.pydecimal(left_digits=9, right_digits=2),
                    "total_liabilities": fake.pydecimal(left_digits=10, right_digits=2, positive=True),
                    "total_operating_expenses": fake.pydecimal(left_digits=9, right_digits=2, positive=True),
                },
            )
            corp_customers.append(corp_customer)

        # 4) f_loan
        loan_products = []
        product_specs = [
            {"name": "Standard Credit Loan", "product_type": "CREDIT_LOAN", "min_rate_bp": 300, "max_rate_bp": 900, "min_limit_krw": 1_000_000, "max_limit_krw": 50_000_000, "max_term_months": 60},
            {"name": "Prime Mortgage Loan", "product_type": "MORTGAGE_LOAN", "min_rate_bp": 250, "max_rate_bp": 500, "min_limit_krw": 50_000_000, "max_limit_krw": 1_000_000_000, "max_term_months": 360},
            {"name": "Business Starter Loan", "product_type": "BUSINESS_LOAN", "min_rate_bp": 400, "max_rate_bp": 1200, "min_limit_krw": 10_000_000, "max_limit_krw": 200_000_000, "max_term_months": 120},
            {"name": "New Car Loan", "product_type": "CAR_LOAN", "min_rate_bp": 350, "max_rate_bp": 700, "min_limit_krw": 5_000_000, "max_limit_krw": 100_000_000, "max_term_months": 72},
        ]
        for spec in product_specs:
            product, _ = LoanProduct.objects.get_or_create(
                name=spec["name"],
                defaults={**spec, "is_active": True}
            )
            loan_products.append(product)

        all_customers = customers + corp_customers
        for _ in range(50):
            # LoanAssessment에 정의된 choices 중 하나의 값(코드)을 무작위로 선택
            purpose_value = random.choice([c[0] for c in LoanAssessment.LoanPurpose.choices])
            customer = random.choice(all_customers)
            product = random.choice(loan_products)
            LoanAssessment.objects.create(
                customer=customer,
                customer_type=customer.customer_type,
                product_type=product.product_type,
                requested_amount=fake.pydecimal(left_digits=7, right_digits=2, positive=True),
                requested_term=random.randint(6, product.max_term_months),
                purpose=purpose_value,
                created_by=random.choice(users),
                approval=random.choice([0, 1, 2]),
            )

        # 5) f_document
        for i in range(20):
            doc, _ = Document.objects.get_or_create(
                file_name=f"report{i+1}.pdf",
                defaults={
                    "title": f"Document {i+1}",
                    "storage_path": f"/docs/report{i+1}.pdf",
                    "created_by": random.choice(users),
                },
            )
            DocumentBinding.objects.get_or_create(
                document=doc,
                defaults={
                    "bind_type": random.choice(["CHAT", "REVIEW"]),
                    "bind_id": random.randint(1, 50),
                },
            )

        # 6) f_chatbot
        for user in users[:5]:
            for j in range(random.randint(1, 3)):
                history, _ = UChatbotHistory.objects.get_or_create(
                    user=user, title=f"Conversation {j+1} for {user.name}"
                )
                for k in range(random.randint(2, 5)):
                    UChatbotSession.objects.create(
                        chatbot_history=history,
                        content_from="USER",
                        content=fake.sentence(),
                        sent_at=timezone.now() - timezone.timedelta(minutes=(5-k)*2)
                    )
                    UChatbotSession.objects.create(
                        chatbot_history=history,
                        content_from="AI",
                        content=fake.sentence(),
                        sent_at=timezone.now() - timezone.timedelta(minutes=(5-k)*2, seconds=-30)
                    )

        # 7) f_calendar
        for user in users[:10]:
            for _ in range(random.randint(2, 5)):
                start = timezone.now() + timezone.timedelta(days=random.randint(-7, 7), hours=random.randint(-12, 12))
                end = start + timezone.timedelta(hours=random.choice([1, 2]))
                cal_event, _ = UCalendarEvent.objects.get_or_create(
                    title=fake.bs(),
                    user=user,
                    start_at=start,
                    end_at=end,
                    defaults={
                        "organizer": user,
                        "content": fake.sentence(),
                        "status": "CONFIRMED",
                        "visibility": "PUBLIC",
                    },
                )
                attendees = random.sample(users, k=random.randint(1, 5))
                for attendee in attendees:
                    UEventAttendees.objects.get_or_create(
                        event=cal_event,
                        attendee_user=attendee,
                        defaults={"response_status": random.choice(["ACCEPTED", "TENTATIVE", "DECLINED"])}
                    )

        # 8) f_todo
        for user in users:
            for _ in range(random.randint(1, 8)):
                UTodoList.objects.create(
                    user=user,
                    title=fake.catch_phrase(),
                    content=fake.sentence(),
                    is_done=random.choice([True, False]),
                )

        self.stdout.write(self.style.SUCCESS("All dummy data seeded!"))
