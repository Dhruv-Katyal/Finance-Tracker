from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from financetrack.forms import TransactionForm,GaolForm
from django.contrib.auth import login,logout
from .models import Transaction,Goal
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
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

    total_income= Transaction.objects.filter(user=request.user,transaction_type= 'Income').aggregate(total=Sum('amount'))['total'] or 0  

    total_expense= Transaction.objects.filter(user=request.user,transaction_type= 'Expense').aggregate(total=Sum('amount'))['total'] or 0 

    net_savings= total_income- total_expense

    remaining_savings = net_savings

    goal_progress =[]
    for goal in goals:
        if remaining_savings >= goal.target_amount:
            goal_progress.append({'goal':goal, 'progress':100})
            remaining_savings -= goal.target_amount
        elif remaining_savings >0:
            progress = (remaining_savings / goal.target_amount) *100 
            goal_progress.append({'goal':goal, 'progress':progress})
            remaining_savings = 0
        else: 
            goal_progress.append({'goal':goal, 'progress':0})

    context= {
        'transactions':transactions,
        'total_income' : total_income,
        'total_expense' : total_expense,
        'net_savings' : net_savings,
        'goal_progress' : goal_progress
    }
    return render(request, 'financetrack/dashboard.html', context)

@login_required
def TransactionCreateView(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect('dashboard')
    else:
        form = TransactionForm()
    return render(request, 'financetrack/transaction.html', {'form': form})

@login_required
def TransactionListView(request):
    transactions=Transaction.objects.filter(user=request.user)
    return render(request, 'financetrack/transactionlist.html', {'transactions':transactions})

@login_required    
def GoalView(request):
    if request.method == 'POST':
        form = GaolForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            return redirect('dashboard')
    else:
        form = TransactionForm()
    return render(request, 'financetrack/goal.html', {'form': form})