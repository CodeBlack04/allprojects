from django.urls import path
from . import views

app_name = 'shopmart'

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('browse/', views.get_products, name='browse'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('policy/', views.policy, name='policy'),
    path('terms/', views.terms, name='terms'),
    path('new/', views.new_product, name='new'),
    path('inbox/', views.inbox, name='inbox'),
    path('config/', views.stripe_config, name='config'),
    path('payment/success/', views.SuccessView.as_view(), name='success'),
    path('payment/cancelled/', views.CancelledView.as_view(), name='cancelled'),
    path('payment/webhook/', views.stripe_webhook, name='webhook'),
    path('<str:product_pk>/', views.product_detail, name='detail'),
    path('<str:product_pk>/edit/', views.edit_product, name='edit'),
    path('<str:product_pk>/delete/', views.product_delete, name='delete'),
    path('new/<str:product_pk>/', views.new_chatroom, name='new-chatroom'),
    path('inbox/<str:chatroom_pk>/', views.chatroom, name='chatroom'),
    path('create-checkout-session/<str:product_pk>/', views.create_checkout_session, name='checkout'),
]