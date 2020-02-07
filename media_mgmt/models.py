from django.db import models

from user_mgmt.models import UserMaster


class GalleryMaster(models.Model):
    user = models.ForeignKey(UserMaster, on_delete=models.CASCADE)
    original_url = models.TextField()
    thumbnail_key = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()




