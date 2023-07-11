from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField


class UserModel(AbstractUser):
    id = models.AutoField(primary_key=True, unique=True,null=False)
    name = models.CharField(max_length=80, null=False, default="XYZ",blank=False)
    username = models.EmailField(
 null=False, default="DUMMY_EMAIL",unique=True,blank=False)
    password = models.CharField(max_length=256, blank=True)
    access_shared_ids = ArrayField(models.IntegerField(blank=True, null=True), size=100, null=True, default=list)

    USERNAME_FIELD = 'username'
    PASSWORD_FIELD = 'password'

    def save(self, *args, **kwargs):
        if self.access_shared_ids is None:
            self.access_shared_ids = []
        super().save(*args, **kwargs)
    def __str__(self):
        return self.username
