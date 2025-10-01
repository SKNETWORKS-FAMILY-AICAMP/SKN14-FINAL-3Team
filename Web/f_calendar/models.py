from django.db import models
from f_user.models import User

class UCalendarEvent(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = "CONFIRMED"
        TENTATIVE = "TENTATIVE"
        CANCELLED = "CANCELLED"

    class Visibility(models.TextChoices):
        PUBLIC = "PUBLIC"
        PRIVATE = "PRIVATE"

    seq_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events")
    organizer = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="organized_events")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255)
    content = models.CharField(max_length=1000, null=True, blank=True)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.CONFIRMED)
    visibility = models.CharField(max_length=8, choices=Visibility.choices, default=Visibility.PUBLIC)

    class Meta:
        db_table = "u_calendar_event"

class UEventAttendees(models.Model):
    class ResponseStatus(models.TextChoices):
        NEEDS_ACTION = "NEEDS_ACTION"
        ACCEPTED = "ACCEPTED"
        DECLINED = "DECLINED"
        TENTATIVE = "TENTATIVE"

    seq_id = models.BigAutoField(primary_key=True)
    event = models.ForeignKey(UCalendarEvent, on_delete=models.CASCADE, related_name="attendees")
    attendee_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="attending_events")
    attendee_email = models.EmailField(null=True, blank=True)
    response_status = models.CharField(max_length=16, choices=ResponseStatus.choices, default=ResponseStatus.NEEDS_ACTION)
    is_optional = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "u_event_attendees"
