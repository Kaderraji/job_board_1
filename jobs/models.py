from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    ROLE_CHOICES = [
        ( "employer", "Employer"),
        ("candidate","Candidate")
    ]
    user= models.OneToOneField(User, on_delete=models.CASCADE , related_name="profile")
    role= models.CharField( max_length= 10, choices=ROLE_CHOICES, default="employer")
    bio= models.TextField(blank=True, null= True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

class Jobs(models.Model):
    profile= models.ForeignKey(Profile , on_delete= models.CASCADE, related_name="jobs")
    title= models.CharField(max_length= 100)
    description = models.TextField()
    location = models.CharField(max_length=25)
    salary= models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at= models.DateTimeField(auto_now_add=True)

class Application(models.Model):
    STATUS=[
        ("applied", "Applied"),
        ("reviewed", "Reviewed"),
        ("rejected", "Rejected"),
        ("accepted", "Accepted"),
    ]
    profile= models.ForeignKey(Profile, on_delete=models.CASCADE)
    job= models.ForeignKey(Jobs, on_delete=models.CASCADE)
    cover_letter= models.TextField(blank=True, null=True)
    cv= models.FileField(upload_to='cvs/', blank=True, null=True)

    status= models.CharField(max_length=10, choices=STATUS, default="applied")
    applied_at= models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together= [['profile', 'job']]

    def is_actionable(self):
        return self.status == "applied"