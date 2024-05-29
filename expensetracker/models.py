from django.db import models
from core.models import User

# Create your models here.

class TransactionTypes(models.TextChoices):
    INCOME = 'IN', 'Income'
    EXPENSE = 'EX', 'Expense'

class Category(models.Model):
    name = models.CharField(max_length=191)
    created_by = models.ForeignKey(User, related_name='categories', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ('name',)

class Transaction(models.Model):
    category = models.ForeignKey(Category, related_name='transactions', on_delete=models.SET_NULL, blank=True, null=True)
    new_category = models.CharField(max_length=191, blank=True)
    name = models.CharField(max_length=191)
    type = models.CharField(max_length=2, choices=TransactionTypes.choices, default=TransactionTypes.INCOME)
    notes = models.TextField(max_length=191, blank=True, null=True)
    amount = models.FloatField()
    created_by = models.ForeignKey(User, related_name='transactions', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}--{self.category.name}--{self.type}--{self.amount}"
    
    class Meta:
        ordering = ('created_at',)