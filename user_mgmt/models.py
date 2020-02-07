from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class UserMaster(AbstractUser):
    mobile = models.CharField(max_length=10, unique=True, blank=True, default=None, null=True)
    address = models.TextField(blank=True, default=None, null=True)
    state = models.CharField(max_length=50, null=True, blank=True, default=None)
    country = models.CharField(max_length=50, null=True, blank=True, default=None)
    pincode = models.CharField(max_length=10, null=True, blank=True, default=None)

    is_verified = models.BooleanField(default=False)

    updated_at = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return "%s) %s %s" % (self.id, self.first_name, self.last_name)
