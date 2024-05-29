from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from collections import defaultdict

from .models import Transaction, Category
from .forms import NewTransactionForm

# Create your views here.
@login_required
def chart_data(request):
    transactions = Transaction.objects.filter(created_by = request.user)

    income_amounts = [income.amount for income in transactions if income.type == 'IN']
    income_values = []
    total_income = 0

    for amount in income_amounts:
        total_income += amount
        income_values.append(total_income)
    
    expense_amounts = [expense.amount for expense in transactions if expense.type == 'EX']
    expense_values = []
    total_expense = 0
    
    for amount in expense_amounts:
        total_expense += amount
        expense_values.append(total_expense)

    labels = [transaction.created_at.strftime('%d-%m-%Y') for transaction in transactions]

    chart_data = {
        'label': 'Income-Expense Chart',
        'labels': labels,

        'income_values': income_values,
        'expense_values': expense_values,

        'chart_type': 'areaspline',
    }

    return JsonResponse(chart_data)



def dashboard(request):
    if request.user.is_authenticated:
        transactions = Transaction.objects.filter(created_by = request.user).order_by('-created_at')
        recent_history = transactions[:5]
    else:
        transactions = None

    if transactions:
        total_income = 0
        total_expense = 0

        income_category_totals = defaultdict(float)
        expense_category_totals = defaultdict(float)

        for transaction in transactions:

            if transaction.type == 'IN':
                total_income += transaction.amount
                income_category_totals[transaction.category] += transaction.amount

            elif transaction.type == 'EX':
                total_expense += transaction.amount
                expense_category_totals[transaction.category] += transaction.amount

        total_balance = total_income - total_expense
        
        
        highest_income_category = max(income_category_totals, key=income_category_totals.get, default=None)
        lowest_income_category = min(income_category_totals, key=income_category_totals.get, default=None)

        highest_expense_category = min(expense_category_totals, key=expense_category_totals.get, default=None)
        lowest_expense_category = max(expense_category_totals, key=expense_category_totals.get, default=None)    

    else:
        return redirect('expensetracker:new')
                
    return render(request, 'expensetracker/dashboard.html', {
        'recent_history': recent_history,
        'total_income': round(total_income, 2),
        'total_expense': round(total_expense, 2),
        'total_balance': round(total_balance, 2),

        'highest_income_category': highest_income_category,
        'lowest_income_category': lowest_income_category,

        'highest_expense_category': highest_expense_category,
        'lowest_expense_category': lowest_expense_category,

    })

@login_required
def new(request):
    if request.method == 'POST':
        form = NewTransactionForm(request.POST)

        if form.is_valid():
            transaction = form.save(commit=False)

            category = form.cleaned_data['category']
            new_category = form.cleaned_data['new_category']

            if not category and new_category:
                category = Category.objects.create(name=new_category, created_by=request.user)

            transaction.category = category
            transaction.created_by = request.user
            transaction.save()

            return redirect('expensetracker:dashboard')
    else:
        form = NewTransactionForm()

    return render(request, 'expensetracker/form.html', { 'form': form })

login_required
def analytics_data(request):
    transactions = Transaction.objects.filter(created_by = request.user)

    if transactions:
        income_category_totals = defaultdict(float)
        expense_category_totals = defaultdict(float)

        for transaction in transactions:

            if transaction.type == 'IN':
                income_category_totals[transaction.category] += transaction.amount

            elif transaction.type == 'EX':
                expense_category_totals[transaction.category] += transaction.amount
        
        income_category_total_labels = []
        for income_category_total in income_category_totals:
            income_category_total_labels.append(income_category_total.name)

        expense_category_total_labels = []
        for expense_category_total in expense_category_totals:
            expense_category_total_labels.append(expense_category_total.name)
        
        income_category_total_amounts = []
        for income_category_total in income_category_totals:
            amount = income_category_totals[income_category_total]
            income_category_total_amounts.append(amount)

        expense_category_total_amounts = []
        for expense_category_total in expense_category_totals:
            amount = expense_category_totals[expense_category_total]
            expense_category_total_amounts.append(amount)
        

    chart_data = {
        'title': 'Analytics',

        'income_category_labels': income_category_total_labels,
        'income_category_totals': income_category_total_amounts,

        'expense_category_labels': expense_category_total_labels,
        'expense_category_totals': expense_category_total_amounts
    }

    return JsonResponse(chart_data)

login_required
def analytics(request):
    return render(request, 'expensetracker/analytics.html', {'title': 'Analytics'})


@login_required
def list(request):
    transactions = Transaction.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'expensetracker/list.html', {
        'transactions': transactions,
    })

@login_required
def incomes(request):
    incomes = Transaction.objects.filter(created_by=request.user).filter(type = 'IN').order_by('-created_at')
    return render(request, 'expensetracker/incomes.html', {
        'incomes': incomes,
    })

@login_required
def expenses(request):
    expenses = Transaction.objects.filter(created_by=request.user).filter(type = 'EX').order_by('-created_at')
    return render(request, 'expensetracker/expenses.html', {
        'expenses': expenses,
    })