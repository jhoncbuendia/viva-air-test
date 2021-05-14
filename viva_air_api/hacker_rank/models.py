from django.db import models
from django.utils import timezone

class Post(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    postId = models.IntegerField()
    details = models.JSONField()