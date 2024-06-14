
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
import os

def user_directory_path(instance, filename):
    extension = filename.split('.')[-1]
    student_full_name = f"{instance.student.first_name}_{instance.student.last_name}".replace(' ', '_')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{student_full_name}_{instance.title.replace(' ', '_')}_{timestamp}.{extension}"
    return os.path.join(filename)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sex = models.CharField(max_length=10)
    major = models.CharField(max_length=50)
    is_approved = models.BooleanField(default=False)

    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

class NewClassName(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to=user_directory_path, blank=True)
    student = models.ForeignKey(User, related_name='projects', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    grade = models.PositiveIntegerField(null=True, blank=True)
    file_path = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.title} - {self.student.get_full_name()}"

    def save(self, *args, **kwargs):
        if not self.id:
            self.file.name = user_directory_path(self, self.file.name)
            self.file_path = self.file.name
            print(f"File path: {self.file_path}")

        super().save(*args, **kwargs)