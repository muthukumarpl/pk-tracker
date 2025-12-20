from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('set-budget/', views.set_budget, name='set_budget'), 
    path('expenses/', views.expense_list, name='expense_list'),
    path('edit/<int:id>/', views.edit_expense, name='edit_expense'),
    path('delete/<int:id>/', views.delete_expense, name='delete_expense'),
    path('charts/', views.charts, name='charts'),
    path('download/', views.download, name='download'), # இது டவுன்லோட் பேஜ்-க்கு
    path('export-csv/', views.export_csv, name='export_csv'), # இது ஃபைல் டவுன்லோட் செய்ய
    path('history/', views.expense_history, name='expense_history'), # பெயர் மாற்றப்பட்டுள்ளது
]
