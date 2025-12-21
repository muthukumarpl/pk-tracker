from django.db import models

# --- OLD MODEL ---
class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('Food', 'Food '),
        ('Travel', 'Travel '),
        ('Entertainment', 'Entertainment '),
        ('EMI/Loans', 'EMI/Loans '),
        ('Shopping', 'Shopping '),
        ('Bills', 'Bills '),
        ('Others', 'Others ️'),
    ]

    title = models.CharField(max_length=100)
    amount = models.IntegerField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    date = models.DateField()

    def __str__(self):
        return self.title

# --- 🔥 NEW BUDGET MODEL ---
class Budget(models.Model):
    limit = models.IntegerField(default=0)

    def __str__(self):
        return str(self.limit)





"""
from django.db import models

# Create your models here.
from django.db import models

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('Food', 'Food '),
        ('Travel', 'Travel '),
        ('Entertainment', 'Entertainment '),
        ('EMI/Loans', 'EMI/Loans '),
        ('Shopping', 'Shopping '),
        ('Bills', 'Bills '),
        ('Others', 'Others ️'),
    ]

    title = models.CharField(max_length=100)
    amount = models.IntegerField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    date = models.DateField()

    def __str__(self):
        return self.title
    
    
"""