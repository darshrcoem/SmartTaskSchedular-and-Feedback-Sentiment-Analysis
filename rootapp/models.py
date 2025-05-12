from django.db import models

class Task(models.Model):
    CREATED_BY_CHOICES = [('admin', 'Admin'), ('user', 'User')]
    STATUS_CHOICES = [('pending', 'Pending'), ('completed', 'Completed')]
    batch = models.IntegerField(choices=[(1, "Batch 1"), (2, "Batch 2"), (3, "Batch 3")])
    date = models.DateField()
    time = models.TimeField()
    priority = models.CharField(max_length=10, choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')])
    task_description = models.TextField()
    deadline = models.DateField()
    created_by = models.CharField(max_length=10, choices=CREATED_BY_CHOICES, default='admin')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    feedback = models.TextField(null=True, blank=True) 
    emotion = models.CharField(max_length=50, null=True, blank=True)
    
    def __str__(self):
        return f"{self.created_by} - Batch {self.batch}: {self.task_description}"

class Emotion(models.Model):
    name=models.CharField(max_length=50,unique=True)
    count=models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.count}"