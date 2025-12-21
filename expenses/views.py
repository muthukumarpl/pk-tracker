from django.shortcuts import render, redirect, get_object_or_404
from .models import Expense, Budget, Income
from .forms import ExpenseForm, BudgetForm, IncomeForm
from django.db.models import Sum
from django.http import HttpResponse
import csv


def home(request):
    return render(request, 'expenses/home.html')


def set_budget(request):
    budget = Budget.objects.first()
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = BudgetForm(instance=budget)
    return render(request, 'expenses/set_budget.html', {'form': form})


def expense_list(request):
    # 1. Income Handling
    if request.method == 'POST' and 'add_income' in request.POST:
        income_form = IncomeForm(request.POST)
        if income_form.is_valid():
            income_form.save()
            return redirect('expense_list')
    else:
        income_form = IncomeForm()

    # 2. Expense Handling
    if request.method == 'POST' and 'add_expense' in request.POST:
        expense_form = ExpenseForm(request.POST)
        if expense_form.is_valid():
            expense_form.save()
            return redirect('expense_list')
    else:
        expense_form = ExpenseForm()

    # 3. Data Retrieval
    expenses = Expense.objects.all().order_by('-date')
    incomes = Income.objects.all().order_by('-date')

    # Search Logic
    search_query = request.GET.get('search')
    if search_query:
        expenses = expenses.filter(title__icontains=search_query)

    # 4. Financial Calculations (PostgreSQL compatible)
    total_spent = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    savings = total_income - total_spent

    # 5. Usage Pulse Logic (Income-அடிப்படையிலான சதவீதம்)
    if total_income > 0:
        real_percentage = (total_spent / total_income) * 100
    else:
        real_percentage = 0

    display_percentage = min(real_percentage, 100)  # Progress bar-க்காக

    return render(request, 'expenses/expense_list.html', {
        'expense_form': expense_form,
        'income_form': income_form,
        'expenses': expenses,
        'incomes': incomes,
        'total_amount': total_spent,
        'total_income': total_income,
        'savings': savings,
        'percentage': display_percentage,
        'real_percentage': real_percentage,
        'search_query': search_query
    })


def delete_income(request, id):
    income = get_object_or_404(Income, id=id)
    if request.method == 'POST':
        income.delete()
    return redirect('expense_list')


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


def expense_history(request):
    expenses = Expense.objects.all().order_by('-date')
    return render(request, 'expenses/history.html', {'expenses': expenses})


def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="pk_expenses.csv"'
    writer = csv.writer(response)
    writer.writerow(['Title', 'Category', 'Amount', 'Date'])
    for expense in Expense.objects.all():
        writer.writerow([expense.title, expense.category, expense.amount, expense.date])
    return response


def download(request):
    return render(request, 'expenses/download.html')
