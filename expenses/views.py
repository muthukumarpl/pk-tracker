from django.shortcuts import render, redirect, get_object_or_404
from .models import Expense, Budget, Income
from .forms import ExpenseForm, BudgetForm, IncomeForm
from django.db.models import Sum
from django.http import HttpResponse
import csv
import json
from django.core.serializers.json import DjangoJSONEncoder
from datetime import timedelta  # புதிய இறக்குமதி
from django.utils import timezone  # புதிய இறக்குமதி


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
    if request.method == 'POST' and 'add_income' in request.POST:
        income_form = IncomeForm(request.POST)
        if income_form.is_valid():
            income_form.save()
            return redirect('expense_list')
    else:
        income_form = IncomeForm()

    if request.method == 'POST' and 'add_expense' in request.POST:
        expense_form = ExpenseForm(request.POST)
        if expense_form.is_valid():
            expense_form.save()
            return redirect('expense_list')
    else:
        expense_form = ExpenseForm()

    expenses = Expense.objects.all().order_by('-date')
    incomes = Income.objects.all().order_by('-date')

    search_query = request.GET.get('search')
    if search_query:
        expenses = expenses.filter(title__icontains=search_query)

    total_spent = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    savings = total_income - total_spent

    if total_income > 0:
        real_percentage = (total_spent / total_income) * 100
    else:
        real_percentage = 0
    display_percentage = min(real_percentage, 100)

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


def calendar_view(request):
    expenses = Expense.objects.all()
    incomes = Income.objects.all()
    events = []

    for expense in expenses:
        events.append({
            'id': expense.id,
            'title': f"🔻 {expense.title}: ₹{expense.amount}",
            'start': expense.date.strftime("%Y-%m-%d"),
            'backgroundColor': '#f64f59',
            'borderColor': '#f64f59',
            'textColor': '#fff',
            'extendedProps': {'type': 'expense'}
        })

    for income in incomes:
        income_name = getattr(income, 'source', getattr(income, 'title', 'Income'))
        events.append({
            'id': income.id,
            'title': f"🔹 {income_name}: ₹{income.amount}",
            'start': income.date.strftime("%Y-%m-%d"),
            'backgroundColor': '#28a745',
            'borderColor': '#28a745',
            'textColor': '#fff',
            'extendedProps': {'type': 'income'}
        })

    events_json = json.dumps(events, cls=DjangoJSONEncoder)
    return render(request, 'expenses/calendar.html', {'events': events_json})


# --- புதிய Forecast View ---
def forecast_view(request):
    # கடந்த 30 நாட்களின் தரவுகள்
    last_30_days = timezone.now() - timedelta(days=30)
    expenses_all = Expense.objects.filter(date__gte=last_30_days)

    # Investment மட்டும் தனியாக
    total_investment = expenses_all.filter(category__iexact='Investment').aggregate(Sum('amount'))['amount__sum'] or 0
    # மற்ற செலவுகள் மட்டும்
    total_spent = expenses_all.exclude(category__iexact='Investment').aggregate(Sum('amount'))['amount__sum'] or 0

    daily_average = total_spent / 30
    predicted_monthly_expense = daily_average * 30
    total_income = Income.objects.all().aggregate(Sum('amount'))['amount__sum'] or 0
    potential_savings = total_income - predicted_monthly_expense

    # Spent vs Investment சதவீதம்
    total_action = total_spent + total_investment
    invest_ratio = (total_investment / total_action * 100) if total_action > 0 else 0

    context = {
        'daily_average': round(daily_average, 2),
        'predicted_monthly': round(predicted_monthly_expense, 2),
        'potential_savings': round(potential_savings, 2),
        'total_income': total_income,
        'total_investment': total_investment,
        'invest_ratio': round(invest_ratio, 1),
    }
    return render(request, 'expenses/forecast.html', context)
