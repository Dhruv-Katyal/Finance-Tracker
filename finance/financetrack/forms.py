from django import forms
from financetrack.models import Transaction,Goal

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields =['title', 'amount', 'transaction_type', 'date']

class GaolForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields =['name', 'target_amount', 'deadline']