from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Product, ChatRoom, Category
from .forms import NewProductForm, EditProductForm, NewMessageForm, ContactForm, CategoryForm

from django.db.models import Q, Min, Max

from django.views.generic.base import TemplateView

from django.conf import settings
from django.http.response import JsonResponse, HttpResponse

from django.core.paginator import Paginator

from django.db.models import Max

import stripe

# Create your views here.
# Core views

def index(request):
    if request.user.is_authenticated:
        products_list = Product.objects.filter(is_sold=False).exclude(created_by=request.user).order_by('-created_at')
    else:
        products_list = Product.objects.filter(is_sold=False).order_by('-created_at')

    categories = Category.objects.all()

    paginator = Paginator(products_list, 5)

    page_number = request.GET.get('page', 1)
    products = paginator.get_page(page_number)

    return render(request=request, template_name='shopmart/index.html', context={
        'title': 'Welcome',
        'products': products,
        'categories': categories,
    })

@login_required
def dashboard(request):
    products = Product.objects.filter(created_by = request.user)
    
    return render(request=request, template_name='shopmart/dashboard.html', context={
        'products': products,
        'title': 'Dashboard'
    })

def about(request):
    return render(request=request, template_name='shopmart/about.html', context={
        'title': 'About'
    })

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect('/shopmart/')
        
    else:
        form = ContactForm()
        
    return render(request=request, template_name='shopmart/contact.html', context={
        'form': form,
        'title': 'Contact'
    })

def policy(request):
    return render(request=request, template_name='shopmart/policy.html', context={
        'title': 'Policy'
    })

def terms(request):
    return render(request=request, template_name='shopmart/terms.html', context={
        'title': 'Terms'
    })









# Product views



def product_detail(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    related_products = Product.objects.filter(is_sold=False).filter(is_reserved=False).filter(category=product.category).exclude(pk=product_pk)

    if not product.is_sold:
        if product.is_reserved:
            if product.is_reservation_expired():
                print('Product in unreserved')
                product.unreserve()
                product.save()

    return render(request=request, template_name='shopmart/detail.html', context={
        'product': product,
        'related_products': related_products
    })

@login_required
def new_product(request):
    if request.method == 'POST':
        form = NewProductForm(request.POST, request.FILES)

        if form.is_valid():
            product_new = form.save(commit=False)
            product_new.created_by = request.user
            product_new.save()

            return redirect('shopmart:detail', product_new.id)
    
    else:
        form = NewProductForm()

    return render(request=request, template_name='shopmart/product_form.html', context={
        'form': form,
        'title': 'List New Product'
    })

@login_required
def edit_product(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)

    if request.method == 'POST':
        form = EditProductForm(request.POST, request.FILES, instance=product)
        
        if form.is_valid():
            form.save()
            return redirect('shopmart:detail', product.id)
        
    else:
        form = EditProductForm(instance=product)

    return render(request=request, template_name='shopmart/product_form.html', context={
        'form': form,
        'title': 'Edit Your product'
    })
        
@login_required
def product_delete(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    product.delete()
    return redirect('shopmart:dashboard')







# Chat views



@csrf_exempt
@login_required
def new_chatroom(request, product_pk):
    product = get_object_or_404(Product, id=product_pk)

    chatroom = ChatRoom.objects.filter(product=product).filter(members__in=[request.user.id])

    if chatroom:
        return redirect('shopmart:chatroom', chatroom_pk = chatroom.first().id)

    if request.method == 'POST':
        form = NewMessageForm(request.POST)

        if form.is_valid():
            message = form.save(commit=False)
            message.sent_by = request.user
            message.save()

            chatroom = ChatRoom.objects.create(product=product)
            chatroom.members.add(request.user)
            chatroom.members.add(product.created_by)
            chatroom.messages.add(message)
            chatroom.save()

            return redirect('shopmart:chatroom', chatroom_pk=chatroom.id)
    
    else:
        form = NewMessageForm()

    return render(request, 'shopmart/new_chatroom.html', {
        'form': form,
        'title': 'New Chatroom',
    })


@login_required
def chatroom(request, chatroom_pk):
    chatroom = get_object_or_404(ChatRoom, id=chatroom_pk)
    form = NewMessageForm()

    return render(request, 'shopmart/chatroom.html', {
        'chatroom': chatroom,
        'form': form,
        'title': 'ChatRoom',
    })


@login_required
def inbox(request):
    chatrooms = ChatRoom.objects.filter(members__in=[request.user.id]).annotate(latest_message_time=Max('messages__created_at')).order_by('-latest_message_time')

    return render(request, 'shopmart/inbox.html', {
        'chatrooms': chatrooms,
        'title': 'Inbox',
    })






# Payment views


class HomePageView(TemplateView):
    template_name = 'shopmart/payment/home.html'

class SuccessView(TemplateView):
    template_name = 'shopmart/success.html'

class CancelledView(TemplateView):
    template_name = 'shopmart/cancelled.html'


@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)


@csrf_exempt
@login_required
def create_checkout_session(request, product_pk):
    
    product = get_object_or_404(Product, pk=product_pk)

    if request.method == 'GET':
        domain_url = 'http://127.0.0.1:8000/shopmart/payment/'
        stripe.api_key = settings.STRIPE_SECRET_KEY

        if not product.is_reserved and not product.is_sold:
            try:
                checkout_session = stripe.checkout.Session.create(
                    client_reference_id=product.pk if request.user.is_authenticated else None,
                    success_url=domain_url + 'success?session_id={CHECKOUT_SESSION_ID}',
                    cancel_url=domain_url + 'cancelled/',
                    payment_method_types=['card'],
                    mode='payment',
                    line_items=[{
                        "price_data": {
                            "currency": 'usd',
                            "product_data": { "name": product.name,},
                            "unit_amount": int(product.price * 100),
                        },
                        "quantity": 1,
                    }]
                )
                # reserve the product
                product.reserve(request.user)
                # print('Product is reserved')

                return JsonResponse({'sessionId': checkout_session['id']})
            except Exception as e:
                return JsonResponse({'error': str(e)})
        else:
            return JsonResponse({'error': 'Product is already sold or reserved by another customer. Please refresh your page!'})


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    
    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        print("Payment was successful.")

        # Get the Checkout session ID from the event
        session_id = event['data']['object']['id']

        # Find the product associated with this session
        
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        product_pk = checkout_session.get('client_reference_id')
        
        if product_pk:
            # Mark the product as sold here
            product = Product.objects.get(pk=product_pk)
            product.is_reserved = False
            product.is_sold = True
            product.save()
            print("Product marked as sold.")
            print('Sold', product.is_sold)
            print('Reserved', product.is_reserved)

    return HttpResponse(status=200)




# browse views

def get_products(request):
    products_list = Product.objects.filter(is_sold=False).order_by('price')
    categories = Category.objects.all().order_by('name',)
    form = CategoryForm(request.GET)

    min_max_price = products_list.aggregate(Min('price'), Max('price'))

    query = request.GET.get('query', '')
    max_price = request.GET.get('max-price', None)

    if query:
        products_list = products_list.filter(Q(name__icontains=query) | Q(description__icontains=query))

    if max_price:
        products_list = products_list.filter(price__lte=max_price)

    if form.is_valid():
        categories = form.cleaned_data['categories']

        if categories:
            category_based_products = []
            for category in categories:
                category_based_products += products_list.filter(category=category)
            products_list = category_based_products

    paginator = Paginator(products_list, 4)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    return render(request=request, template_name='shopmart/browse.html', context={
        'products': products,
        'categories': categories,
        'category_form': form,

        'min_max_price': min_max_price,

        'max_price': max_price,

        'query': query,
        'title': 'Browse'
    })