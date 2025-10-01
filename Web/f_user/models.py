from django.db import models
from f_common.models import UncBankLocation, UncEmploymentType

class UPosition(models.Model):
    seq_id = models.BigAutoField(primary_key=True)
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "u_position"

class UDepartment(models.Model):
    seq_id = models.BigAutoField(primary_key=True)
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "u_department"

class User(models.Model):
    class EmploymentStatus(models.TextChoices):
        ON_DUTY = "ON_DUTY"
        ON_LEAVE = "ON_LEAVE"
        RESIGNED = "RESIGNED"

    seq_id = models.BigAutoField(primary_key=True)
    employee_id = models.CharField(max_length=32, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    name = models.CharField(max_length=100)
    position = models.ForeignKey(UPosition, null=True, on_delete=models.SET_NULL)
    department = models.ForeignKey(UDepartment, null=True, on_delete=models.SET_NULL)
    manager = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="subordinates")
    bank_location = models.ForeignKey(UncBankLocation, null=True, on_delete=models.SET_NULL)
    hire_date = models.DateField()

    ext_number = models.CharField(max_length=32, null=True, blank=True, unique=True)
    mobile = models.CharField(max_length=32, null=True, blank=True, db_index=True)
    birthdate = models.DateField(null=True, blank=True)

    employment_status = models.CharField(max_length=16, choices=EmploymentStatus.choices, default=EmploymentStatus.ON_DUTY)
    employment_type = models.ForeignKey(UncEmploymentType, null=True, on_delete=models.SET_NULL)

    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    password_changed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user"
