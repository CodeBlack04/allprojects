from django.urls import path

from expensetracker import views


app_name = 'expensetracker'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('new/', views.new, name='new'),
    path('analytics/', views.analytics, name='analytics'),
    path('list/', views.list, name='list'),
    path('incomes/', views.incomes, name='incomes'),
    path('expenses/', views.expenses, name='expenses'),
    path('analytics-data/', views.analytics_data, name='analytics_data'),
    path('chart-data/', views.chart_data, name='chart_data'),
]