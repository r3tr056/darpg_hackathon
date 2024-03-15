from django.db import models
from authentication.models import CustomUser

class Category(models.Model):
    code = models.CharField(max_length=10, unique=True)
    parent_category = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    description = models.TextField()
    org_code = models.CharField(max_length=10)

    def __str__(self):
        return self.description

class GrievanceReport(models.Model):
    PENDING = 'Pending'
    COMPLETED = 'Completed'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
    ]

    classifed = models.BooleanField(default=False)
    reg_no = models.CharField(max_length=256)
    title = models.CharField(max_length=256)
    subject_content = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    submitter = models.ForeignKey(CustomUser, related_name='submitted_reports', on_delete=models.CASCADE)
    reviewer = models.ForeignKey(CustomUser, related_name='reviewed_reports', on_delete=models.CASCADE, null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)

    def __str__(self):
        return self.title