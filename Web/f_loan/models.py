from django.db import models
from f_user.models import User
from f_customer.models import Customer


class LoanProduct(models.Model):
    class ProductType(models.TextChoices):
        CREDIT_LOAN = "CREDIT_LOAN"
        MORTGAGE_LOAN    = "MORTGAGE_LOAN"
        CAR_LOAN      = "CAR_LOAN"
        HOUSING_LOAN      = "HOUSING_LOAN"
        BUSINESS_LOAN   = "BUSINESS_LOAN"
    seq_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=200)
    product_type = models.CharField(max_length=32, choices=ProductType.choices, default=ProductType.CREDIT_LOAN)
    min_rate_bp = models.IntegerField()
    max_rate_bp = models.IntegerField()
    min_limit_krw = models.DecimalField(max_digits=18, decimal_places=0)
    max_limit_krw = models.DecimalField(max_digits=18, decimal_places=0)
    max_term_months = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LoanAssessment(models.Model):
    class LoanPurpose(models.TextChoices):
        Education = "EDUCATION"
        Medical = "MEDICAL"
        Venture = "VENTURE"
        Personal = "PERSONAL"
        Debt   = "DEBTCONSOLIDATION"
    seq_id = models.BigAutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    customer_type = models.CharField(max_length=16, default="INDIVIDUAL")
    product_type = models.CharField(max_length=16, default="CREDIT_LOAN")
    requested_amount = models.DecimalField(max_digits=18, decimal_places=2)
    requested_term = models.IntegerField()
    purpose = models.CharField(max_length=32, choices=LoanPurpose.choices, default=LoanPurpose.Personal)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    approval = models.PositiveSmallIntegerField(default=0)  # 0=거절, 1=심사중, 2=승인

    class Meta:
        db_table = "loan_assessment"

class LoanAssessmentStep(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = "SUBMITTED"
        IN_REVIEW = "IN_REVIEW"
        APPROVED  = "APPROVED"
        REJECTED  = "REJECTED"
        CANCELLED = "CANCELLED"
        DISBURSED = "DISBURSED"

    class Decision(models.IntegerChoices):
        REJECTED = 0
        APPROVED = 1
        OTHER    = 2

    seq_id = models.BigAutoField(primary_key=True)
    application = models.ForeignKey(LoanAssessment, on_delete=models.CASCADE)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.SUBMITTED)
    decision = models.PositiveSmallIntegerField(choices=Decision.choices, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "loan_assessment_steps"