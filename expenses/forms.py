from django import forms
from .models import Expense, Budget

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'category', 'date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control rounded-pill',
                'placeholder': 'எதற்காக செலவு செய்தீர்கள்?'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control rounded-pill',
                'placeholder': 'தொகை (Amount)'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select rounded-pill'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control rounded-pill',
                'type': 'date'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(ExpenseForm, self).__init__(*args, **kwargs)
        # இங்கே 'Food' என்பதை default ஆக செட் செய்கிறோம்
        # உங்கள் Model-ல் உள்ள தேர்வுகளில் இது சரியாக இருப்பதை உறுதி செய்யவும்
        self.fields['category'].initial = 'Food'


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['limit']
        widgets = {
            'limit': forms.NumberInput(attrs={
                'class': 'form-control rounded-pill',
                'placeholder': 'உங்கள் பட்ஜெட் இலக்கு (e.g. 5000)'
            }),
        }