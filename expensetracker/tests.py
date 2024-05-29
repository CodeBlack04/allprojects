from django.test import TestCase
from django.urls import reverse

from core.models import User
from .models import Category, TransactionTypes, Transaction

# Create your tests here.
class TransactionViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com',
            name='testuser',
            password='abcdABCD1234'
        )

        self.category = Category.objects.create(
            name = 'Salary',
            created_by = self.user
        )

        self.transaction1 = Transaction.objects.create(
            name = 'Pavel Sir',
            category = self.category,
            type = TransactionTypes.INCOME,
            amount = 1000,
            created_by = self.user,
        )

        self.transaction2 = Transaction.objects.create(
            name = 'Tuition',
            category = self.category,
            type = TransactionTypes.EXPENSE,
            amount = 750,
            created_by = self.user
        )

    def test_dashboard_without_login_view(self):
        response = self.client.get(reverse('expensetracker:dashboard'))

        self.assertEqual(response.status_code, 302)

    def test_dashboard_view(self):
        self.client.login(email='test@test.com', name='testuser', password='abcdABCD1234')
        response = self.client.get(reverse('expensetracker:dashboard'))
        self.assertEqual(response.status_code, 200)

        self.assertIn('total_income', response.context)
        self.assertIn('total_expense', response.context)
        self.assertIn('total_expense', response.context)

        self.assertEqual(response.context['total_income'], 1000)
        self.assertEqual(response.context['total_expense'], 750)
        self.assertEqual(response.context['total_balance'], 250)


    def test_new_view(self):
        self.client.login(email='test@test.com', name='testuser', password='abcdABCD1234')
        response = self.client.get(reverse('expensetracker:new'))
        self.assertEqual(response.status_code, 200)

        data1 = {
            'name': 'Tuition',
            'category': self.category.pk,
            'type': TransactionTypes.INCOME,
            'amount': 500
        }

        response = self.client.post(reverse('expensetracker:new'), data1)
        self.assertEqual(response.status_code, 302)

        transactions = Transaction.objects.all()
        self.assertEqual(transactions.count(), 3)
        self.assertEqual(Category.objects.all().count(), 1)
        self.assertEqual(Transaction.objects.filter(type='EX').count(), 1)
        self.assertEqual(Transaction.objects.filter(type='IN').count(), 2)

        data2 = {
            'name': 'Fuel',
            'new_category': 'Car',
            'type': TransactionTypes.EXPENSE,
            'amount': 500
        }

        response = self.client.post(reverse('expensetracker:new'), data2)
        self.assertEqual(Category.objects.all().count(), 2)
        self.assertEqual(Transaction.objects.filter(type='EX').count(), 2)
        self.assertEqual(Transaction.objects.filter(type='IN').count(), 2)


    def test_list_without_login_view(self):
        response = self.client.get(reverse('expensetracker:list'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('core:login') + '?next=' + reverse('expensetracker:list'))

    def test_list_view(self):
        self.client.login(email='test@test.com', name='testuser', password='abcdABCD1234')
        response = self.client.get(reverse('expensetracker:list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['transactions'].count(), 2)

        categories = Category.objects.all()
        self.assertEqual(categories.count(), 1)
        self.assertEqual(Transaction.objects.all().count(), 2)


    def test_incomes_view(self):
        self.client.login(email='test@test.com', name='testuser', password='abcdABCD1234')
        response = self.client.get(reverse('expensetracker:incomes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.transaction1.name)
        self.assertEqual(response.context['incomes'].count(), 1)


    def test_expenses_view(self):
        self.client.login(email='test@test.com', name='testuser', password='abcdABCD1234')
        response = self.client.get(reverse('expensetracker:expenses'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.transaction2.name)
        self.assertEqual(response.context['expenses'].count(), 1)


    def test_chart_data_view(self):
        self.client.login(email='test@test.com', name='testuser', password='abcdABCD1234')
        response = self.client.get(reverse('expensetracker:chart_data'))
        self.assertEqual(response.status_code, 200)

        data1 = response.json()
        self.assertIn(self.transaction1.amount, data1['income_values'])
        self.assertIn(self.transaction2.amount, data1['expense_values'])

        category2 = Category.objects.create(
            name = 'Rent',
            created_by = self.user
        )

        transaction3 = Transaction.objects.create(
            name = 'Home',
            category = category2,
            type = TransactionTypes.EXPENSE,
            amount = 300,
            created_by = self.user,
        )

        response = self.client.get(reverse('expensetracker:chart_data'))

        data2 = response.json()
        self.assertIn(self.transaction2.amount + transaction3.amount, data2['expense_values'])


    def test_analytics_data_view(self):
        self.client.login(email='test@test.com', name='testuser', password='abcdABCD1234')
        response = self.client.get(reverse('expensetracker:analytics_data'))
        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertIn(self.category.name, data['income_category_labels'])
        self.assertIn(self.category.name, data['expense_category_labels'])

        category2 = Category.objects.create(
            name = 'Rent',
            created_by = self.user
        )

        Transaction.objects.create(
            name = 'Home',
            category = category2,
            type = TransactionTypes.EXPENSE,
            amount = 300,
            created_by = self.user,
        )


        response = self.client.get(reverse('expensetracker:analytics_data'))

        data2 = response.json()
        self.assertIn(category2.name, data2['expense_category_labels'])


    def test_analytics_view(self):
        self.client.login(email='test@test.com', name='testuser', password='abcdABCD1234')
        response = self.client.get(reverse('expensetracker:analytics'))
        self.assertEqual(response.status_code, 200)
        