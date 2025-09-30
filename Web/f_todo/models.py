from django.db import models
from f_user.models import User

class UTodoList(models.Model):
    seq_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255)
    content = models.TextField(null=True, blank=True)
    is_done = models.BooleanField(default=False)

    class Meta:
        db_table = "u_todo_list"
