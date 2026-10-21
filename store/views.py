import uuid
from decimal import Decimal
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .models import Book, Customer, SalesOrder, OrderItem, EmailDelivery
from .forms import CheckoutForm
from .services import send_delivery

def cart_books(request):
    return list(Book.objects.filter(pk__in=request.session.get('cart', []), is_active=True))

def catalog(request):
    books = Book.objects.filter(is_active=True)
    query = request.GET.get('q','').strip()
    category = request.GET.get('category','')
    if query: books = books.filter(Q(title__icontains=query) | Q(author__icontains=query))
    if category: books = books.filter(category=category)
    from django.core.paginator import Paginator
    page = Paginator(books, 12).get_page(request.GET.get('page'))
    return render(request,'store/catalog.html',{'books':page,'query':query,'category':category,'categories':Book.objects.filter(is_active=True).values_list('category',flat=True).distinct().order_by('category')})

def detail(request, pk):
    return render(request,'store/detail.html',{'book':get_object_or_404(Book,pk=pk,is_active=True)})

@require_POST
def add_cart(request, pk):
    book = get_object_or_404(Book,pk=pk,is_active=True)
    cart = request.session.get('cart',[])
    if pk not in cart:
        cart.append(pk)
        request.session['cart'] = cart
    messages.success(request,f'“{book.title}” was added to your cart.')
    return redirect('cart')

@require_POST
def remove_cart(request, pk):
    request.session['cart'] = [i for i in request.session.get('cart',[]) if i != pk]
    return redirect('cart')

def cart(request):
    books = cart_books(request)
    return render(request,'store/cart.html',{'books':books,'total':sum((b.price for b in books),Decimal('0.00'))})

def checkout(request):
    if 'checkout_key' not in request.session: request.session['checkout_key'] = str(uuid.uuid4())
    key = request.session['checkout_key']
    existing = SalesOrder.objects.filter(checkout_key=key).first()
    if existing and request.method == 'POST':
        request.session['last_order'] = str(existing.order_number)
        return redirect('confirmation', number=existing.order_number)
    books = cart_books(request)
    if not books:
        messages.info(request,'Add a book to your cart before checking out.')
        return redirect('catalog')
    form = CheckoutForm(request.POST or None)
    total = sum((b.price for b in books),Decimal('0.00'))
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            customer, _ = Customer.objects.get_or_create(email=form.cleaned_data['email'],defaults={'name':form.cleaned_data['name']})
            order, created = SalesOrder.objects.get_or_create(checkout_key=key,defaults={'customer':customer,'customer_name':form.cleaned_data['name'],'customer_email':form.cleaned_data['email'],'total_amount':total})
            if created:
                OrderItem.objects.bulk_create([OrderItem(order=order,book=b,book_title=b.title,unit_price=b.price) for b in books])
                delivery = EmailDelivery.objects.create(order=order,recipient_email=order.customer_email,attachment_name=f'ebooks-{str(order.order_number)[:8]}.txt')
                transaction.on_commit(lambda: send_delivery(delivery.pk))
        request.session['cart'] = []
        request.session['last_order'] = str(order.order_number)
        return redirect('confirmation',number=order.order_number)
    # A new visit after a completed order needs its own idempotency key.
    if existing:
        request.session['checkout_key'] = str(uuid.uuid4())
    return render(request,'store/checkout.html',{'form':form,'books':books,'total':total})

def confirmation(request, number):
    if request.session.get('last_order') != str(number):
        from django.http import Http404
        raise Http404
    order = get_object_or_404(SalesOrder,order_number=number)
    return render(request,'store/confirmation.html',{'order':order,'delivery':order.deliveries.first()})
