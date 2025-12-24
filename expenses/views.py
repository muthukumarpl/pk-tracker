from django.shortcuts import render, redirect, get_object_or_404
from .models import Expense, Budget, Income, ExpenseGroup, GroupExpense, Blog  # GroupExpense சேர்த்துள்ளேன்
from .forms import ExpenseForm, BudgetForm, IncomeForm
from django.db.models import Sum
from django.http import HttpResponse
import csv
import json
from django.core.serializers.json import DjangoJSONEncoder
from datetime import timedelta
from django.utils import timezone

# User Auth imports
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


# --- 1. USER AUTH VIEWS ---

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('expense_list')
    else:
        form = UserCreationForm()
    return render(request, 'expenses/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('expense_list')
    else:
        form = AuthenticationForm()
    return render(request, 'expenses/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


# --- 2. EXPENSE & BUDGET VIEWS ---

def home(request):
    return render(request, 'expenses/home.html')


@login_required
def set_budget(request):
    budget, created = Budget.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = BudgetForm(instance=budget)
    return render(request, 'expenses/set_budget.html', {'form': form})


@login_required
def expense_list(request):
    if request.method == 'POST' and 'add_income' in request.POST:
        income_form = IncomeForm(request.POST)
        if income_form.is_valid():
            income = income_form.save(commit=False)
            income.user = request.user
            income.save()
            return redirect('expense_list')
    else:
        income_form = IncomeForm()

    if request.method == 'POST' and 'add_expense' in request.POST:
        expense_form = ExpenseForm(request.POST)
        if expense_form.is_valid():
            expense = expense_form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('expense_list')
    else:
        expense_form = ExpenseForm()

    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    incomes = Income.objects.filter(user=request.user).order_by('-date')

    search_query = request.GET.get('search')
    if search_query:
        expenses = expenses.filter(title__icontains=search_query)

    total_spent = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    savings = total_income - total_spent

    user_budget = Budget.objects.filter(user=request.user).first()
    budget_limit = user_budget.limit if user_budget else 0
    budget_warning = total_spent > budget_limit if budget_limit > 0 else False

    real_percentage = (total_spent / total_income * 100) if total_income > 0 else 0
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
        'search_query': search_query,
        'budget_limit': budget_limit,
        'budget_warning': budget_warning,
    })


# --- 3. EDIT & DELETE VIEWS ---

@login_required
def edit_expense(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'expenses/edit_expense.html', {'form': form})


@login_required
def delete_expense(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)
    if request.method == 'POST':
        expense.delete()
        return redirect('expense_list')
    return render(request, 'expenses/delete_confirmation.html', {'expense': expense})


@login_required
def delete_income(request, id):
    income = get_object_or_404(Income, id=id, user=request.user)
    if request.method == 'POST':
        income.delete()
    return redirect('expense_list')


# --- 4. REPORTS & EXPORTS ---

@login_required
def charts(request):
    expenses = Expense.objects.filter(user=request.user)
    data = {}
    for expense in expenses:
        data[expense.category] = data.get(expense.category, 0) + expense.amount
    categories = list(data.keys())
    amounts = list(data.values())
    return render(request, 'expenses/charts.html', {'categories': categories, 'amounts': amounts})


@login_required
def expense_history(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    return render(request, 'expenses/history.html', {'expenses': expenses})


@login_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="my_expenses.csv"'
    writer = csv.writer(response)
    writer.writerow(['Title', 'Category', 'Amount', 'Date'])
    for expense in Expense.objects.filter(user=request.user):
        writer.writerow([expense.title, expense.category, expense.amount, expense.date])
    return response


# --- 5. GROUP EXPENSES (NEW FEATURES WITH SPLIT LOGIC) ---

@login_required
def group_list(request):
    groups = request.user.expense_groups.all()
    return render(request, 'expenses/group_list.html', {'groups': groups})


@login_required
def create_group(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        group_type = request.POST.get('group_type')
        group = ExpenseGroup.objects.create(name=name, group_type=group_type, created_by=request.user)
        group.members.add(request.user)
        return redirect('group_list')
    return render(request, 'expenses/create_group.html')


# views.py-ல் group_detail வியூவை இப்படி அப்டேட் செய்யவும்
@login_required
def group_detail(request, group_id):
    group = get_object_or_404(ExpenseGroup, id=group_id, members=request.user)

    # 1. Add Member & Add Expense logic (ஏற்கனவே நீங்கள் வைத்திருப்பது அப்படியே இருக்கட்டும்)
    # ... (உங்களுடைய பழைய POST லாஜிக் இங்கே வர வேண்டும்) ...

    # 2. செட்டில்மென்ட் கணக்கீடு
    group_expenses = group.expenses.all().order_by('-date')
    total_group_spent = group_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    member_count = group.members.count()
    per_person_share = total_group_spent / member_count if member_count > 0 else 0

    # ஒவ்வொரு மெம்பரும் எவ்வளவு செலுத்தியுள்ளனர் என்பதைக் கணக்கிடுதல்
    settlements = []
    for member in group.members.all():
        member_paid = group_expenses.filter(paid_by=member).aggregate(Sum('amount'))['amount__sum'] or 0
        balance = member_paid - per_person_share
        settlements.append({
            'user': member,
            'paid': member_paid,
            'balance': balance
        })

    return render(request, 'expenses/group_detail.html', {
        'group': group,
        'group_expenses': group_expenses,
        'total_spent': total_group_spent,
        'per_person': per_person_share,
        'settlements': settlements
    })


# --- 6. OTHER TOOLS ---

@login_required
def calendar_view(request):
    expenses = Expense.objects.filter(user=request.user)
    incomes = Income.objects.filter(user=request.user)
    events = []
    for exp in expenses:
        events.append(
            {'title': f"Expense: ₹{exp.amount}", 'start': exp.date.strftime("%Y-%m-%d"), 'backgroundColor': '#ff4d4d'})
    for inc in incomes:
        events.append(
            {'title': f"Income: ₹{inc.amount}", 'start': inc.date.strftime("%Y-%m-%d"), 'backgroundColor': '#2ecc71'})
    return render(request, 'expenses/calendar.html', {'events': json.dumps(events, cls=DjangoJSONEncoder)})


@login_required
def forecast_view(request):
    last_30_days = timezone.now() - timedelta(days=30)
    expenses_all = Expense.objects.filter(user=request.user, date__gte=last_30_days)
    total_spent = expenses_all.exclude(category__iexact='Investment').aggregate(Sum('amount'))['amount__sum'] or 0
    daily_avg = total_spent / 30 if total_spent > 0 else 0
    total_income = Income.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
    context = {
        'daily_average': round(daily_avg, 2),
        'predicted_monthly': round(daily_avg * 30, 2),
        'potential_savings': round(total_income - (daily_avg * 30), 2),
        'total_income': total_income,
    }
    return render(request, 'expenses/forecast.html', context)



@login_required
def download(request):
    return render(request, 'expenses/download.html')

def blog_list(request, category_name):
    # குறிப்பிட்ட கேட்டகிரி தொடர்பான பிளாக்குகளை மட்டும் எடுத்தல்
    blogs = Blog.objects.filter(category__iexact=category_name)
    return render(request, 'expenses/blog_list.html', {
        'blogs': blogs,
        'category': category_name
    })
"""
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

"""