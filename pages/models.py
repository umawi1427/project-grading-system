from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sex = models.CharField(max_length=10)
    major = models.CharField(max_length=50)
    is_approved = models.BooleanField(default=False)

def get_upload_path(instance, filename):
    return 'projects/{0}/{1}'.format(instance.teacher.username, filename)

class Project(models.Model):
    name = models.CharField(max_length=200, default='Default name')
    description = models.TextField()
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to=get_upload_path)
    student = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)