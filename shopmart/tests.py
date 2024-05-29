from django.test import TestCase
from django.urls import reverse

from core.models import User
from .models import Product, Category, ChatRoom, ConversationMessage
from .forms import CategoryForm

from django.conf import settings
from unittest.mock import patch, MagicMock

# Create your tests here.
# PRODUCT TESTS
class ProductViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@test.com', name='testuser', password='abcdABCD1234')
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            category = self.category,
            name = 'Test Product',
            price = 100,
            created_by = self.user
        )




    def test_product_detail_view(self):
        response = self.client.get(reverse('shopmart:detail', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
    
        product = Product.objects.get(id=self.product.id)
        self.assertEqual(product.name, 'Test Product')
        self.assertEqual(product.price, 100)




    def test_new_product_view(self):
        self.client.login(email='test@test.com', name='testuser', password='abcdABCD1234')
        response = self.client.post(reverse('shopmart:new'), data={
            'category': self.category.id,
            'name': 'New Product',
            'price': 200,
            
        })
        self.assertEqual(response.status_code, 302)

        new_product = Product.objects.get(name='New Product')
        self.assertEqual(new_product.name, 'New Product')
        self.assertEqual(new_product.price, 200)




    def test_edit_product_view(self):
        self.client.login(email='test@test.com', name='testuser', password='abcdABCD1234')
        response = self.client.post(reverse('shopmart:edit', args=[self.product.id]), data={
            'category': self.category.id,
            'name': 'Updated Product',
            'price': 150
        })

        updated_product = Product.objects.get(id=self.product.id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(updated_product.name, 'Updated Product')
        self.assertEqual(updated_product.price, 150)




    def test_product_delete_view(self):
        self.client.login(email='test@test.com', name='testuser', password='abcdABCD1234')
        response = self.client.post(reverse('shopmart:delete', args=[self.product.id]))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Product.objects.filter(id=self.product.id).count(), 0)





# PAYMENT TESTS

class PaymentViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@test.com', name='testuser', password='abcdABCD1234')
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            category = self.category,
            name = 'Test Product',
            price = 100,
            created_by = self.user
        )

    
    def test_stripe_config_view(self):
        response = self.client.get(reverse('shopmart:config'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'publicKey': settings.STRIPE_PUBLISHABLE_KEY})


    @patch('stripe.checkout.Session.create')
    def test_create_checkout_session_view(self, mock_create_session):
        mock_checkout_session = MagicMock(id='fake_session_id')
        mock_create_session.return_value = mock_checkout_session

        self.client.login(email='test@test.com', name='testuser', password='abcdABCD1234')

        response = self.client.get(reverse('shopmart:checkout', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)

        mock_create_session.assert_called_once_with(
            client_reference_id=self.product.pk,
            success_url='http://127.0.0.1:8000/shopmart/payment/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://127.0.0.1:8000/shopmart/payment/cancelled/',
            payment_method_types=['card'],
            mode='payment',
            line_items=[{
                "price_data": {
                    "currency": 'usd',
                    "product_data": {"name": self.product.name,},
                    "unit_amount": int(self.product.price * 100),
                },
                "quantity": 1,
            }]
        )


# CORE TESTS
class SignupViewTest(TestCase):
    def test_signup_view(self):
        form_data = {
            'name': 'testuser',
            'email': 'test@test.com',
            'password1': 'abcdABCD1234',
            'password2': 'abcdABCD1234'
        }

        post_response = self.client.post(reverse('core:signup'), data=form_data)

        get_response = self.client.get(reverse('core:signup'))

        self.assertEqual(post_response.status_code, 302)
        self.assertRedirects(post_response, reverse('core:welcome_page'))
        self.assertEqual(get_response.status_code, 200)

class DashboardViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@test.com', name='testuser', password='abcdABCD1234')
        self.category = Category.objects.create(name='Test Category')


    def test_dashboard_view(self):
        self.client.login(email='test@test.com', name='testuser', password='abcdABCD1234')

        product1 = Product.objects.create(
            category=self.category,  # Replace with the correct category
            name='Product 1',
            price=100.0,
            created_by = self.user
        )

        product2 = Product.objects.create(
            category=self.category,
            name='Product 2',
            price=200.0,
            created_by = self.user
        )

        response = self.client.get(reverse('shopmart:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Product 1')
        self.assertContains(response, 'Product 2')
        self.assertIn(product1, response.context['products'])
        self.assertIn(product2, response.context['products'])

        returned_products = Product.objects.all()

        for product in returned_products:
            self.assertEqual(product.created_by, self.user)


    def test_index_view(self):
        product1 = Product.objects.create(
            category=self.category,  # Replace with the correct category
            name='Product 1',
            price=100.0,
            created_by = self.user
        )

        product2 = Product.objects.create(
            category=self.category,
            name='Product 2',
            price=200.0,
            created_by = self.user
        )

        response = self.client.get(reverse('shopmart:index'))

        self.assertEqual(response.status_code, 200)

        products = Product.objects.all()

        self.assertTrue(products.exists())
        self.assertEqual(products.count(), 2)


    def test_contact_view(self):
        post_response = self.client.post(reverse('shopmart:contact'), data={
            'full_name': 'test',
            'email': 'test@test.com',
            'subject': 'test'
        })

        get_response = self.client.get(reverse('shopmart:contact'))

        self.assertEqual(post_response.status_code, 302)
        self.assertEqual(get_response.status_code, 200)



# CHAT TESTS
class ChatViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@test.com', name='testuser', password='abcdABCD1234')
        self.customer = User.objects.create_user(email='customer@customer.com', name='customer', password='abcdABCD1234')
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            category = self.category,
            name = 'Test Product',
            price = 100,
            created_by = self.user
        )

    
    def test_new_chatroom_view(self):
        self.client.login(email='customer@customer.com', name='customer', password='abcdABCD1234')

        chatrooms = ChatRoom.objects.all()
        self.assertFalse(chatrooms.exists())
        self.assertEqual(chatrooms.count(), 0)

        response = self.client.post(reverse('shopmart:new-chatroom', args=[self.product.id]), data={
            'body': 'Hello!'
        })

        chatrooms = ChatRoom.objects.all()
        message = chatrooms.first().messages.first().body
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(chatrooms.exists)
        self.assertEqual(chatrooms.count(), 1)
        self.assertEqual(message, 'Hello!')


    def test_chatroom_view(self):
        self.client.login(email='customer@customer.com', name='customer', password='abcdABCD1234')

        message1 = ConversationMessage.objects.create(
            body = 'Hello!',
            sent_by = self.customer
        )

        message2 = ConversationMessage.objects.create(
            body = 'Hi! There!',
            sent_by = self.user
        )

        chatroom = ChatRoom.objects.create(
            product = self.product
        )
        chatroom.members.add(self.customer)
        chatroom.members.add(self.user)
        chatroom.messages.add(message1)
        chatroom.messages.add(message2)

        response = self.client.get(reverse('shopmart:chatroom', args=[chatroom.id]))

        self.assertEqual(response.status_code, 200)

        messages = chatroom.messages.all()

        self.assertEqual(messages.first().body, 'Hello!')
        self.assertEqual(messages.last().body, 'Hi! There!')
        self.assertEqual(messages.first().sent_by, self.customer)
        self.assertEqual(messages.last().sent_by, self.user)

    
    def test_inbox_view(self):
        self.client.login(email='customer@customer.com', name='customer', password='abcdABCD1234')

        message1 = ConversationMessage.objects.create(
            body = 'Hello!',
            sent_by = self.customer
        )

        message2 = ConversationMessage.objects.create(
            body = 'Hi! There!',
            sent_by = self.user
        )

        chatroom = ChatRoom.objects.create(
            product = self.product
        )
        chatroom.members.add(self.customer)
        chatroom.members.add(self.user)
        chatroom.messages.add(message1)
        chatroom.messages.add(message2)

        response = self.client.get(reverse('shopmart:inbox'))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(ChatRoom.objects.all().exists())
        self.assertEqual(ChatRoom.objects.all().count(), 1)


# BROESE TESTS
class ProductsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@test.com', name='testuser', password='abcdABCD1234')

        self.category1 = Category.objects.create(name='Category 1')
        self.category2 = Category.objects.create(name='Category 2')

        self.product1 = Product.objects.create(
            category=self.category1,
            name='Product 1',
            price=100,
            created_by = self.user
        )

        self.product2 = Product.objects.create(
            category=self.category2,
            name='Product 2',
            price=150,
            created_by = self.user
        )

    def test_get_products_view(self):
        response_without_query = self.client.get(reverse('shopmart:browse'))

        self.assertEqual(response_without_query.status_code, 200)
        self.assertContains(response_without_query, 'Product 1')
        self.assertContains(response_without_query, 'Product 2')
        self.assertContains(response_without_query, 'Category 1')
        self.assertContains(response_without_query, 'Category 2')

        self.assertIsInstance(response_without_query.context['category_form'], CategoryForm)

        products = response_without_query.context['products']

        self.assertEqual(len(products), 2)
        self.assertEqual(products[0].name, 'Product 1')
        self.assertEqual(products[1].name, 'Product 2')

        response_with_query = self.client.get(reverse('shopmart:browse') + '?query=Product 1')
        self.assertEqual(len(response_with_query.context['products']), 1)
        self.assertEqual(response_with_query.context['products'][0].name, 'Product 1')

        response_with_max_price = self.client.get(reverse('shopmart:browse') + '?max-price=125')
        self.assertEqual(len(response_with_max_price.context['products']), 1)
        self.assertEqual(response_with_max_price.context['products'][0].name, 'Product 1')

        response_with_categories = self.client.get(reverse('shopmart:browse') + f'?categories={self.category2.id}')
        self.assertEqual(len(response_with_categories.context['products']), 1)
        self.assertEqual(response_with_categories.context['products'][0].name, 'Product 2')

        response_with_all_filters = self.client.get(reverse('shopmart:browse') + '?query=Product 1' + '&max-price=125' + f'&categories={self.category1.id}')
        self.assertEqual(len(response_with_all_filters.context['products']), 1)
        self.assertEqual(response_with_all_filters.context['products'][0].name, 'Product 1')
