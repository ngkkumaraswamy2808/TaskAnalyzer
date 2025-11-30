from django.db import models

# Create your models here.
class Task(models.Model):
    title = models.CharField(max_length=200)
    due_date = models.DateField(null=True, blank=True)
    importance = models.IntegerField(default=5)  # 1-10
    estimated_hours = models.IntegerField(default=1)
    # list of task IDs that this task depends on
    dependencies = models.JSONField(default=list, blank=True)

    def _str_(self):
        return self.title