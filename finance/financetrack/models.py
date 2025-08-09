from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    CATEGORY_TYPES = [
        ('Income', 'Income'),
        ('Expense', 'Expense'),
    ]
    name = models.CharField(max_length=50)
    category_type = models.CharField(max_length=7, choices=CATEGORY_TYPES)

    def __str__(self):
        return self.name
    
class Transaction(models.Model):
    TRANSACTION_TYPES=[
        ('Income','Income'),
        ('Expense','Expense')
    ]
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    amount = models.DecimalField( max_digits=10, decimal_places=3)
    transaction_type = models.CharField(max_length=10, choices= TRANSACTION_TYPES)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField()
    
    def __str__(self):
        return self.title
    
class Goal(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    target_amount = models.DecimalField( max_digits=10, decimal_places=3)
    deadline = models.DateTimeField()

    def __str__(self):
        return self.name