from django.db import models
from f_common.models import CIndustryCode, CEducationLevel, CHousingStatus, UncBankLocation, UncEmploymentType

class Customer(models.Model):
    class CustomerType(models.TextChoices):
        INDIVIDUAL = "INDIVIDUAL"
        CORPORATE = "CORPORATE"
    
    class Status(models.TextChoices):
        ONLINE = "ONLINE"
        OFFLINE = "OFFLINE"
        AWAY = "AWAY"
        ON_MEETING = "ON_MEETING"

    class Segment(models.TextChoices):
        RETAIL = "RETAIL"
        SME = "SME"
        CORP = "CORP"
        MVP = "MVP"

    seq_id = models.BigAutoField(primary_key=True)
    customer_type = models.CharField(max_length=16, choices=CustomerType.choices, default=CustomerType.INDIVIDUAL)
    display_name = models.CharField(max_length=255)
    bank_location = models.ForeignKey(UncBankLocation, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=16, default="ACTIVE")
    risk_segment = models.CharField(max_length=16, default="RETAIL")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "customer"

class CustomerPerson(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, primary_key=True, related_name="person")
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    gender = models.PositiveSmallIntegerField()  # 0=남, 1=여
    rrn = models.CharField(max_length=64, unique=True)
    mobile = models.CharField(max_length=32, unique=True)
    email = models.EmailField(unique=True)
    account_number = models.CharField(max_length=64)
    account_amount = models.DecimalField(max_digits=18, decimal_places=2)
    education_level = models.ForeignKey(CEducationLevel, null=True, on_delete=models.SET_NULL)
    housing_status = models.ForeignKey(CHousingStatus, null=True, on_delete=models.SET_NULL)
    income_annual = models.DecimalField(max_digits=18, decimal_places=2)
    work_experience_years = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    employment_type = models.ForeignKey(UncEmploymentType, null=True, on_delete=models.SET_NULL)
    industry_code = models.ForeignKey(CIndustryCode, null=True, on_delete=models.SET_NULL)
    has_delinquency = models.BooleanField(default=False)
    credit_history_length = models.IntegerField(default=0)  # 연수
    credit_rating = models.PositiveSmallIntegerField()

    class Meta:
        db_table = "customer_person"

class CustomerCorporate(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, primary_key=True, related_name="corporate")
    industry_code = models.ForeignKey(CIndustryCode, null=True, on_delete=models.SET_NULL)
    legal_name = models.CharField(max_length=255, unique=True) # ceo_name 필드 제거
    biz_reg_no_masked = models.CharField(max_length=64, unique=True)
    incorporation_date = models.DateField()
    employees_count = models.IntegerField()
    mobile = models.CharField(max_length=32) # email 필드 및 mobile unique=True 제거

    # 재무 숫자 (NUMERIC(20,2))
    current_assets = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    cost_of_goods_sold = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    depreciation_amortization = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    ebitda = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    inventory = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    net_income = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    total_receivables = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    market_value = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)          # "Market value"
    net_sales = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    total_assets = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    total_long_term_debt = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    ebit = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    gross_profit = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    total_current_liabilities = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    retained_earnings = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    total_revenue = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    total_liabilities = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    total_operating_expenses = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
