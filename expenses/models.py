from django.db import models
from django.contrib.auth.models import User

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    CATEGORY_CHOICES = [
        ('Food', 'Food 🍔'),
        ('Travel', 'Travel 🚗'),
        ('Entertainment', 'Entertainment 🍿'),
        ('EMI/Loans', 'EMI/Loans 🏦'),
        ('Shopping', 'Shopping 🛍️'),
        ('Bills', 'Bills 📜'),
        ('Investment', 'Investment 📈'),
        ('Others', 'Others ⚙️'),
    ]
    title = models.CharField(max_length=100)
    amount = models.IntegerField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    date = models.DateField()

    def __str__(self):
        return f"{self.user.username} - {self.title}"

class Budget(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    limit = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.limit}"

class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source = models.CharField(max_length=100)
    amount = models.FloatField()
    date = models.DateField()

    def __str__(self):
        return f"{self.user.username} - {self.source}"

# models.py-ன் இறுதியில் இதைச் சேர்க்கவும்
class ExpenseGroup(models.Model):
    GROUP_TYPES = [
        ('Roommates', 'Roommates 🏠'),
        ('Couples', 'Couples 💑'),
        ('Family', 'Family 👨‍👩‍👧‍👦'),
        ('Office', 'Office 🏢'),
        ('Friends', 'Friends 🤝'),
    ]
    name = models.CharField(max_length=100)
    group_type = models.CharField(max_length=20, choices=GROUP_TYPES)
    members = models.ManyToManyField(User, related_name='expense_groups')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_groups')

    def __str__(self):
        return f"{self.name} ({self.group_type})"

class GroupExpense(models.Model):
    group = models.ForeignKey(ExpenseGroup, on_delete=models.CASCADE, related_name='expenses')
    paid_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def split_amount(self):
        # Oru member-ku evlo selavu nu calculate pannum
        count = self.group.members.count()
        return self.amount / count if count > 0 else self.amount

    def __str__(self):
        return f"{self.title} - {self.amount}"

class Blog(models.Model):
    category = models.CharField(max_length=50) # எ.கா: Food, Travel
    title = models.CharField(max_length=200)
    content = models.TextField()
    image_url = models.URLField(blank=True) # ஒருவேளை படம் வைக்க விரும்பினால்
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title