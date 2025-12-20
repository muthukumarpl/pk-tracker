from django.shortcuts import render, redirect, get_object_or_404
from .models import Expense, Budget  # Budget Import
from .forms import ExpenseForm, BudgetForm  # BudgetForm Import
from django.db.models import Sum
from django.http import HttpResponse
import csv


# 1. HOME
def home(request):
    return render(request, 'expenses/home.html')


# 2. SET BUDGET (NEW)
def set_budget(request):
    # ஏற்கனவே பட்ஜெட் இருந்தால் அதை எடு, இல்லாவிட்டால் புதிதாக உருவாக்கு
    budget = Budget.objects.first()
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = BudgetForm(instance=budget)
    return render(request, 'expenses/set_budget.html', {'form': form})


# 3. EXPENSE LIST (UPDATED WITH ALERT)
def expense_list(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm()

    # எல்லா செலவுகளையும் எடுப்போம்
    expenses = Expense.objects.all().order_by('-date')

    # 🔥 SEARCH LOGIC: பயனர் எதையாவது தேடுகிறாரா?
    search_query = request.GET.get('search')
    if search_query:
        expenses = expenses.filter(title__icontains=search_query)  # தலைப்பில் தேடும்

    total_amount = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    budget_obj = Budget.objects.first()
    budget_limit = budget_obj.limit if budget_obj else 0
    is_over_budget = (budget_limit > 0 and total_amount > budget_limit)

    return render(request, 'expenses/expense_list.html', {
        'form': form,
        'expenses': expenses,
        'total_amount': total_amount,
        'budget_limit': budget_limit,
        'is_over_budget': is_over_budget,
        'search_query': search_query  # தேடிய வார்த்தையை மீண்டும் காட்ட
    })


# ... (மற்ற Edit, Delete, Charts, Download வியூகள் பழையபடியே இருக்கட்டும்) ...
# (Edit, Delete, Charts, Download Logic கீழே அப்படியே இருக்க வேண்டும்)
def edit_expense(request, id):
    expense = get_object_or_404(Expense, id=id)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'expenses/edit_expense.html', {'form': form})


def delete_expense(request, id):
    expense = get_object_or_404(Expense, id=id)
    if request.method == 'POST':
        expense.delete()
        return redirect('expense_list')
    return render(request, 'expenses/delete_confirmation.html', {'expense': expense})


def charts(request):
    expenses = Expense.objects.all()
    data = {}
    for expense in expenses:
        if expense.category in data:
            data[expense.category] += expense.amount
        else:
            data[expense.category] = expense.amount
    categories = list(data.keys())
    amounts = list(data.values())
    return render(request, 'expenses/charts.html', {'categories': categories, 'amounts': amounts})


def download(request):
    return render(request, 'expenses/download.html')


def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="pk_expenses.csv"'
    writer = csv.writer(response)
    writer.writerow(['Title', 'Category', 'Amount', 'Date'])
    for expense in Expense.objects.all():
        writer.writerow([expense.title, expense.category, expense.amount, expense.date])
    return response