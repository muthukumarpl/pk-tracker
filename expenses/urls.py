from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('expenses/', views.expense_list, name='expense_list'),
    path('set-budget/', views.set_budget, name='set_budget'),
    path('edit/<int:id>/', views.edit_expense, name='edit_expense'),
    path('delete/<int:id>/', views.delete_expense, name='delete_expense'),
    path('delete-income/<int:id>/', views.delete_income, name='delete_income'), # New
    path('charts/', views.charts, name='charts'),
    path('history/', views.expense_history, name='expense_history'),
    path('download/', views.download, name='download'),
    path('export-csv/', views.export_csv, name='export_csv'),
]