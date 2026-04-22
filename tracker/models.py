from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.

class Category(models.Model):
    TYPE_CHOICES = [
        ('IN', 'Income'),
        ('OUT', 'Expense'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=3, choices=TYPE_CHOICES)

    class Meta:
        ordering = ['name']
        unique_together = ['user', 'name']

    def __str__(self):
        return f'{self.name} ({self.get_type_display()})'
    

class Transaction(models.Model):
    TYPE_CHOICES = [
        ('IN', 'Income'),
        ('OUT', 'Expense'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=3, choices=TYPE_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateField(default=timezone.now)
    note = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f'{self.user.username} - {self.category} - {self.amount}'

class SaldoAwal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        unique_together = ['user', 'month']
        ordering = ['-month']
        
    def __str__(self):
        return f'{self.user.username} - {self.month.strftime("%B %Y")} - {self.amount}'