from django import forms
from .models import Expense, Budget, Income

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'category', 'date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'செலவு தலைப்பு'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'தொகை'}),
            'category': forms.Select(attrs={'class': 'form-select rounded-pill'}),
            'date': forms.DateInput(attrs={'class': 'form-control rounded-pill', 'type': 'date'}),
        }

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['source', 'amount', 'date']
        widgets = {
            'source': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'வருமான ஆதாரம்'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'தொகை'}),
            'date': forms.DateInput(attrs={'class': 'form-control rounded-pill', 'type': 'date'}),
        }

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['limit']
        widgets = {
            'limit': forms.NumberInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'பட்ஜெட் இலக்கு'}),
        }