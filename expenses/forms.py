from django import forms
from .models import Expense, Budget  # Budget-ஐ import செய்யவும்

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'category', 'date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'செலவு விவரம்'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount ₹'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

# --- 🔥 NEW BUDGET FORM ---
class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['limit']
        widgets = {
            'limit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Set your monthly limit ₹'})
        }