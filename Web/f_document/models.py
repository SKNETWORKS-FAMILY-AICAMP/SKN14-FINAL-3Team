from django.db import models
from f_user.models import User

class Document(models.Model):
    class DocType(models.TextChoices):
        PDF = "PDF"
        REPORT = "REPORT"

    seq_id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255)
    storage_path = models.CharField(max_length=512)
    mime_type = models.CharField(max_length=100, default="application/pdf")
    doc_type = models.CharField(max_length=16, choices=DocType.choices, default=DocType.PDF)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "document"

class DocumentBinding(models.Model):
    class BindType(models.TextChoices):
        CHAT = "CHAT"
        REVIEW = "REVIEW"

    seq_id = models.BigAutoField(primary_key=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="bindings")
    bind_type = models.CharField(max_length=16, choices=BindType.choices)
    bind_id = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "document_binding"
