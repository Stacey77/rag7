from django.db import models


class Candidate(models.Model):
    """Model representing a job candidate."""
    
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    applied_role = models.CharField(max_length=255, blank=True, default='')
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.applied_role}"
