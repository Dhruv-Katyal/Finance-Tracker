from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from financetrack.forms import TransactionForm,GaolForm
from django.contrib.auth import login,logout
from .models import Transaction,Goal
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models.functions import TruncMonth,TruncYear,ExtractQuarter
import json
from decimal import Decimal
from django.shortcuts import get_object_or_404

# from .middlewares import auth,guest

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user= form.save()   
            login(request,user)
            return redirect('dashboard')
    else:
        initial_data = {'username':'', 'password1': '', 'password2':''}
        form = UserCreationForm(initial=initial_data)
    return render(request, 'financetrack/registration.html', {'form':form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request,data=request.POST)
        if form.is_valid():
            user= form.get_user() 
            login(request,user)
            return redirect('dashboard')
    else:
        initial_data = {'username':'', 'password': ''}
        form = AuthenticationForm(initial=initial_data)
    return render(request, 'financetrack/login.html', {'form':form})    

@login_required
def dashboard(request):
    transactions = Transaction.objects.filter(user=request.user)
    goals = Goal.objects.filter(user=request.user)

    # Totals
    total_income = transactions.filter(transaction_type='Income').aggregate(total=Sum('amount'))['total'] or 0
    total_expense = transactions.filter(transaction_type='Expense').aggregate(total=Sum('amount'))['total'] or 0
    net_savings = total_income - total_expense

    # Goal progress
    remaining_savings = net_savings
    goal_progress = []
    for goal in goals:
        if remaining_savings >= goal.target_amount:
            goal_progress.append({'goal': goal, 'progress': 100})
            remaining_savings -= goal.target_amount
        elif remaining_savings > 0:
            progress = (remaining_savings / goal.target_amount) * 100
            goal_progress.append({'goal': goal, 'progress': progress})
            remaining_savings = 0
        else:
            goal_progress.append({'goal': goal, 'progress': 0})

    # Monthly data
    monthly_income = (
        transactions.filter(transaction_type='Income')
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )
    monthly_expense = (
        transactions.filter(transaction_type='Expense')
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    # Quarterly data
    quarterly_data = (
        transactions
        .annotate(year=TruncYear('date'), quarter=ExtractQuarter('date'))
        .values('year', 'quarter', 'transaction_type')
        .annotate(total=Sum('amount'))
        .order_by('year', 'quarter')
    )

    # Yearly data
    yearly_data = (
        transactions
        .annotate(year=TruncYear('date'))
        .values('year', 'transaction_type')
        .annotate(total=Sum('amount'))
        .order_by('year')
    )

    # Convert Decimals to floats for JSON
    def dec_to_float(value):
        return float(value) if isinstance(value, Decimal) else value

    context = {
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_savings': net_savings,
        'goal_progress': goal_progress,
        'monthly_labels': json.dumps([m['month'].strftime('%b %Y') for m in monthly_income]),
        'monthly_income': json.dumps([dec_to_float(m['total']) for m in monthly_income]),
        'monthly_expense': json.dumps([dec_to_float(e['total']) for e in monthly_expense]),
        'quarterly_labels': json.dumps([f"Q{q['quarter']} {q['year'].year}" for q in quarterly_data if q['transaction_type'] == 'Income']),
        'quarterly_income': json.dumps([dec_to_float(q['total']) for q in quarterly_data if q['transaction_type'] == 'Income']),
        'quarterly_expense': json.dumps([dec_to_float(q['total']) for q in quarterly_data if q['transaction_type'] == 'Expense']),
        'yearly_labels': json.dumps([y['year'].year for y in yearly_data if y['transaction_type'] == 'Income']),
        'yearly_income': json.dumps([dec_to_float(y['total']) for y in yearly_data if y['transaction_type'] == 'Income']),
        'yearly_expense': json.dumps([dec_to_float(y['total']) for y in yearly_data if y['transaction_type'] == 'Expense']),
    }

    return render(request, 'financetrack/dashboard.html', context)

@login_required
def TransactionUpdateView(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction updated successfully!')
            return redirect('dashboard')
    else:
        form = TransactionForm(instance=transaction)
    return render(request, 'financetrack/transaction_edit.html', {'form': form})

@login_required
def TransactionDeleteView(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Transaction deleted successfully!')
        return redirect('dashboard')
    return render(request, 'financetrack/transaction_confirm_delete.html', {'transaction': transaction})

@login_required
def TransactionCreateView(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request,'Transaction Added Successfully!!!')
            return redirect('dashboard')
    else:
        form = TransactionForm()
    return render(request, 'financetrack/transaction.html', {'form': form})

@login_required
def TransactionListView(request):
    transactions=Transaction.objects.filter(user=request.user).exclude(id__isnull=True)
    return render(request, 'financetrack/transactionlist.html', {'transactions':transactions})

@login_required    
def GoalView(request):
    if request.method == 'POST':
        form = GaolForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request,'Goal Added Successfully!!!')
            return redirect('dashboard')
    else:
        form = TransactionForm()
    return render(request, 'financetrack/goal.html', {'form': form})
