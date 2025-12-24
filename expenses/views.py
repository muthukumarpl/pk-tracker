from django.shortcuts import render, redirect, get_object_or_404
from .models import Expense, Budget, Income, ExpenseGroup, GroupExpense, Blog
from .forms import ExpenseForm, BudgetForm, IncomeForm
from django.db.models import Sum
from django.http import HttpResponse, Http404
import csv
import json
from django.core.serializers.json import DjangoJSONEncoder
from datetime import timedelta
from django.utils import timezone
from django.contrib import messages

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
            messages.success(request, f"Account created successfully for {user.username}! Please login.")
            return redirect('login')
        else:
            # பாஸ்வேர்ட் விதிகள் தவறினால் எரர் மெசேஜ் காட்ட
            messages.error(request, "Registration failed. Please follow the password requirements.")
    else:
        form = UserCreationForm()
    return render(request, 'expenses/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # லாகின் ஆனதும் ஒரு சின்ன வெல்கம் மெசேஜ் (விருப்பப்பட்டால்)
            messages.info(request, f"Welcome back, {user.username}!")
            return redirect('expense_list')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'expenses/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

# --- 2. CORE EXPENSE & INCOME VIEWS ---

def home(request):
    return render(request, 'expenses/home.html')

@login_required
def expense_list(request):
    if request.method == 'POST' and 'add_income' in request.POST:
        income_form = IncomeForm(request.POST)
        if income_form.is_valid():
            income = income_form.save(commit=False)
            income.user = request.user
            if not income.date:
                income.date = timezone.now().date()
            income.save()
            messages.success(request, "Income added successfully!")
            return redirect('expense_list')
    else:
        income_form = IncomeForm()

    if request.method == 'POST' and 'add_expense' in request.POST:
        expense_form = ExpenseForm(request.POST)
        if expense_form.is_valid():
            expense = expense_form.save(commit=False)
            expense.user = request.user
            if not expense.date:
                expense.date = timezone.now().date()
            expense.save()
            messages.success(request, "Expense added successfully!")
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
    budget_limit = user_budget.amount if user_budget else 0 # FIXED: .limit-க்கு பதில் .amount
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

# --- மற்ற फंக்ஷன்கள் (Edit, Delete, Charts, Groups) நீங்கள் கொடுத்தது போலவே சரியாக உள்ளன ---

@login_required
def set_budget(request):
    budget, created = Budget.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            messages.success(request, "Budget updated!")
            return redirect('expense_list')
    else:
        form = BudgetForm(instance=budget)
    return render(request, 'expenses/set_budget.html', {'form': form})

# Edit/Delete Logic
@login_required
def edit_expense(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, "Expense updated successfully!")
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'expenses/edit_expense.html', {'form': form})

@login_required
def delete_expense(request, id):
    try:
        expense = Expense.objects.get(id=id, user=request.user)
        if request.method == 'POST':
            expense.delete()
            messages.success(request, "Expense deleted.")
            return redirect('expense_list')
    except Expense.DoesNotExist:
        return redirect('expense_list')
    return render(request, 'expenses/delete_confirmation.html', {'expense': expense})

@login_required
def delete_income(request, id):
    try:
        income = Income.objects.get(id=id, user=request.user)
        if request.method == 'POST':
            income.delete()
            messages.success(request, "Income entry deleted.")
            return redirect('expense_list')
    except Income.DoesNotExist:
        return redirect('expense_list')
    return redirect('expense_list')

# Group Views
@login_required
def group_detail(request, group_id):
    group = get_object_or_404(ExpenseGroup, id=group_id, members=request.user)

    if request.method == 'POST' and 'add_member' in request.POST:
        username = request.POST.get('username')
        try:
            user_to_add = User.objects.get(username=username)
            group.members.add(user_to_add)
            messages.success(request, f"@{username} added to group.")
        except User.DoesNotExist:
            messages.error(request, "User not found!")
        return redirect('group_detail', group_id=group.id)

    if request.method == 'POST' and 'add_group_expense' in request.POST:
        title = request.POST.get('title')
        amount = request.POST.get('amount')
        if title and amount:
            GroupExpense.objects.create(group=group, paid_by=request.user, title=title, amount=amount)
            messages.success(request, "Group expense added.")
        return redirect('group_detail', group_id=group.id)

    group_expenses = group.expenses.all().order_by('-date')
    total_group_spent = group_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    member_count = group.members.count()
    per_person_share = total_group_spent / member_count if member_count > 0 else 0

    settlements = []
    for member in group.members.all():
        member_paid = group_expenses.filter(paid_by=member).aggregate(Sum('amount'))['amount__sum'] or 0
        balance = member_paid - per_person_share
        settlements.append({'user': member, 'paid': member_paid, 'balance': balance})

    return render(request, 'expenses/group_detail.html', {
        'group': group,
        'group_expenses': group_expenses,
        'total_spent': total_group_spent,
        'per_person': per_person_share,
        'settlements': settlements
    })

# மற்ற views அப்படியே இருக்கட்டும்...
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
def calendar_view(request):
    expenses = Expense.objects.filter(user=request.user)
    incomes = Income.objects.filter(user=request.user)
    events = []
    for exp in expenses:
        events.append({'title': f"Exp: ₹{exp.amount}", 'start': exp.date.strftime("%Y-%m-%d"), 'backgroundColor': '#ff4d4d'})
    for inc in incomes:
        events.append({'title': f"Inc: ₹{inc.amount}", 'start': inc.date.strftime("%Y-%m-%d"), 'backgroundColor': '#2ecc71'})
    return render(request, 'expenses/calendar.html', {'events': json.dumps(events, cls=DjangoJSONEncoder)})

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
        messages.success(request, f"Group '{name}' created!")
        return redirect('group_list')
    return render(request, 'expenses/create_group.html')

def blog_list(request, category_name):
    blogs = Blog.objects.filter(category__iexact=category_name)
    return render(request, 'expenses/blog_list.html', {'blogs': blogs, 'category': category_name})

@login_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="my_expenses.csv"'
    writer = csv.writer(response)
    writer.writerow(['Title', 'Category', 'Amount', 'Date'])
    for expense in Expense.objects.filter(user=request.user):
        writer.writerow([expense.title, expense.category, expense.amount, expense.date])
    return response

@login_required
def download(request):
    return render(request, 'expenses/download.html')