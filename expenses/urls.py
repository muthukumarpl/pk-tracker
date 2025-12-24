from django.urls import path
from . import views

urlpatterns = [
    # --- Home & Core Features ---
    path('', views.home, name='home'),
    path('expenses/', views.expense_list, name='expense_list'),
    path('set-budget/', views.set_budget, name='set_budget'),
    path('edit/<int:id>/', views.edit_expense, name='edit_expense'),
    path('delete/<int:id>/', views.delete_expense, name='delete_expense'),
    path('delete-income/<int:id>/', views.delete_income, name='delete_income'),

    # --- Analysis & History ---
    path('charts/', views.charts, name='charts'),
    path('history/', views.expense_history, name='expense_history'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('forecast/', views.forecast_view, name='forecast'),

    # --- Data Export & Download ---
    path('download/', views.download, name='download'),
    path('export-csv/', views.export_csv, name='export_csv'),

    # --- User Authentication (Login/Signup) ---
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # --- Shared Groups (Roommates, Family, Friends) ---
    path('groups/', views.group_list, name='group_list'),
    path('groups/create/', views.create_group, name='create_group'),
    #path('group/<int:group_id>/', views.group_detail, name='group_detail'),
    path('groups/<int:group_id>/', views.group_detail, name='group_detail'), # குரூப் விவரங்களை பார்க்க
    path('blogs/<str:category_name>/', views.blog_list, name='blog_list'),
]
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('expenses/', views.expense_list, name='expense_list'),
    path('set-budget/', views.set_budget, name='set_budget'),
    path('edit/<int:id>/', views.edit_expense, name='edit_expense'),
    path('delete/<int:id>/', views.delete_expense, name='delete_expense'),
    path('delete-income/<int:id>/', views.delete_income, name='delete_income'),
    path('charts/', views.charts, name='charts'),
    path('history/', views.expense_history, name='expense_history'),
    path('download/', views.download, name='download'),
    path('export-csv/', views.export_csv, name='export_csv'),
    path('calendar/', views.calendar_view, name='calendar'),

    # புதிய Forecast வசதிக்கான வரி
    path('forecast/', views.forecast_view, name='forecast'),
]
"""