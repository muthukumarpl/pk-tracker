from django.contrib import admin
from .models import Blog, Expense, Income, Budget, ExpenseGroup, GroupExpense

admin.site.register(Blog) # இதை மட்டும் சேர்த்தால் போதும்