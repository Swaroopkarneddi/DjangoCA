from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import (
    UserCustomer, Product, ProductImage, Review, Cart,
    Order, Wishlist, OrderItem
)
from .serializers import (
    UserCustomerSerializer, ProductSerializer, ReviewSerializer,CartSerializer,
    WishlistSerializer, OrderSerializer, OrderItemSerializer
)
from django.contrib.auth.hashers import make_password, check_password

# -------------------- User Registration & Login --------------------

@api_view(['POST'])
def register_view(request):
    data = request.data
    if not all(k in data for k in ('name', 'email', 'password')):
        return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

    if UserCustomer.objects.filter(email=data['email']).exists():
        return Response({'error': 'User already exists'}, status=status.HTTP_409_CONFLICT)

    user = UserCustomer.objects.create(
        name=data['name'],
        email=data['email'],
        password=make_password(data['password']),
        address=data.get('address'),
        phone=data.get('phone')
    )
    serializer = UserCustomerSerializer(user)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def login_view(request):
    data = request.data
    if not all(k in data for k in ('email', 'password')):
        return Response({'error': 'Missing email or password'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = UserCustomer.objects.get(email=data['email'])
    except UserCustomer.DoesNotExist:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    if check_password(data['password'], user.password):
        serializer = UserCustomerSerializer(user)
        return Response(serializer.data)
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# -------------------- Users --------------------

@api_view(['GET'])
def get_users(request):
    users = UserCustomer.objects.all()
    serializer = UserCustomerSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
def update_user(request, user_id):
    try:
        user = UserCustomer.objects.get(id=user_id)
    except UserCustomer.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    data = request.data
    for attr in ['name', 'email', 'address', 'phone']:
        setattr(user, attr, data.get(attr, getattr(user, attr)))
    if 'password' in data:
        user.password = make_password(data['password'])
    user.save()

    return Response(UserCustomerSerializer(user).data)

@api_view(['DELETE'])
def delete_user(request, user_id):
    try:
        user = UserCustomer.objects.get(id=user_id)
        user.delete()
        return Response({'message': 'User deleted'})
    except UserCustomer.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

# -------------------- Products --------------------

@api_view(['GET'])
def get_all_products(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        return Response(ProductSerializer(product).data)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=404)

@api_view(['POST'])
def add_product(request):
    data = request.data
    images = data.pop('images', [])
    reviews = data.pop('reviews', [])

    product = Product.objects.create(**data)

    for img in images:
        ProductImage.objects.create(product=product, image_url=img)

    for rev in reviews:
        user = UserCustomer.objects.get(id=rev['userId'])
        Review.objects.create(
            user=user,
            product=product,
            rating=rev['rating'],
            comment=rev.get('comment', ''),
            date=rev.get('date')
        )

    return Response(ProductSerializer(product).data, status=201)

@api_view(['PUT'])
def update_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=404)

    for field in ['name', 'price', 'description', 'category', 'brand', 'stock', 'featured', 'trending']:
        if field in request.data:
            setattr(product, field, request.data[field])
    product.save()

    return Response(ProductSerializer(product).data)

@api_view(['DELETE'])
def delete_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        product.delete()
        return Response({'message': 'Product deleted'})
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=404)

# -------------------- Reviews --------------------

@api_view(['POST'])
def add_review(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=404)

    data = request.data
    try:
        user = UserCustomer.objects.get(id=data['userId'])
    except UserCustomer.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    review = Review.objects.create(
        user=user,
        product=product,
        rating=data['rating'],
        comment=data.get('comment', '')
    )
    return Response(ReviewSerializer(review).data, status=201)

@api_view(['GET'])
def get_reviews(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=404)

    reviews = product.review_set.all()
    return Response(ReviewSerializer(reviews, many=True).data)

@api_view(['DELETE'])
def delete_review(request, review_id):
    try:
        review = Review.objects.get(id=review_id)
        review.delete()
        return Response({'message': 'Review deleted'})
    except Review.DoesNotExist:
        return Response({'error': 'Review not found'}, status=404)


# -------------------- Cart --------------------

@api_view(['GET', 'POST'])
def cart_list_create(request):
    if request.method == 'GET':
        carts = Cart.objects.all()
        return Response(CartSerializer(carts, many=True).data)
    elif request.method == 'POST':
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['PUT', 'DELETE'])
def cart_update_delete(request, cart_id):
    try:
        cart = Cart.objects.get(id=cart_id)
    except Cart.DoesNotExist:
        return Response({'error': 'Cart item not found'}, status=404)

    if request.method == 'PUT':
        serializer = CartSerializer(cart, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        cart.delete()
        return Response({'message': 'Cart item deleted'})

@api_view(['POST'])
def add_to_cart(request, user_id):
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity', 1)

    try:
        user = UserCustomer.objects.get(id=user_id)
        product = Product.objects.get(id=product_id)
    except (UserCustomer.DoesNotExist, Product.DoesNotExist):
        return Response({'error': 'Invalid user or product'}, status=404)

    # Check if product already exists in cart
    cart_item, created = Cart.objects.get_or_create(user=user, product=product)
    if not created:
        cart_item.quantity += int(quantity)
    else:
        cart_item.quantity = int(quantity)
    cart_item.save()

    return Response(CartSerializer(cart_item).data, status=201)

@api_view(['GET'])
def get_user_cart(request, user_id):
    cart_items = Cart.objects.filter(user_id=user_id)
    serializer = CartSerializer(cart_items, many=True)
    return Response(serializer.data)

@api_view(['DELETE'])
def delete_cart_item(request, user_id, product_id):
    try:
        cart_item = Cart.objects.get(user_id=user_id, product_id=product_id)
        cart_item.delete()
        return Response({'message': 'Item removed from cart'}, status=200)
    except Cart.DoesNotExist:
        return Response({'error': 'Item not found in cart'}, status=404)

@api_view(['PUT'])
def update_cart_quantity(request, user_id, product_id):
    try:
        cart_item = Cart.objects.get(user_id=user_id, product_id=product_id)
        quantity = request.data.get('quantity')
        if quantity is not None and int(quantity) > 0:
            cart_item.quantity = int(quantity)
            cart_item.save()
            return Response(CartSerializer(cart_item).data)
        else:
            return Response({'error': 'Invalid quantity'}, status=400)
    except Cart.DoesNotExist:
        return Response({'error': 'Cart item not found'}, status=404)

@api_view(['DELETE'])
def clear_user_cart(request, user_id):
    cart_items = Cart.objects.filter(user_id=user_id)
    if cart_items.exists():
        cart_items.delete()
        return Response({'message': 'All items removed from cart'}, status=200)
    else:
        return Response({'message': 'Cart is already empty'}, status=200)


# -------------------- Wishlist --------------------

@api_view(['GET'])
def get_user_wishlist(request, user_id):
    try:
        user = UserCustomer.objects.get(id=user_id)
    except UserCustomer.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    wishlist_items = Wishlist.objects.filter(user=user)
    serializer = WishlistSerializer(wishlist_items, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def add_to_wishlist(request, user_id):
    try:
        user = UserCustomer.objects.get(id=user_id)
    except UserCustomer.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    product_id = request.data.get('product')
    if not product_id:
        return Response({'error': 'Product ID is required'}, status=400)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=404)

    if Wishlist.objects.filter(user=user, product=product).exists():
        return Response({'message': 'Already in wishlist'}, status=200)

    wishlist = Wishlist.objects.create(user=user, product=product)
    return Response(WishlistSerializer(wishlist).data, status=201)


@api_view(['DELETE'])
def delete_wishlist_item(request):
    user_id = request.data.get('user_id')
    product_id = request.data.get('product_id')

    try:
        # Get the wishlist item for the user and product combination
        wish = Wishlist.objects.get(user_id=user_id, product_id=product_id)
        wish.delete()
        return Response({'message': 'Wishlist item deleted successfully'})
    except Wishlist.DoesNotExist:
        return Response({'error': 'Wishlist item not found for this user and product'}, status=404)



# -------------------- Orders --------------------

@api_view(['GET', 'POST'])
def order_list_create(request):
    if request.method == 'GET':
        orders = Order.objects.all()
        return Response(OrderSerializer(orders, many=True).data)
    elif request.method == 'POST':
        data = request.data
        items = data.pop('items', [])
        order = Order.objects.create(**data)

        for item in items:
            OrderItem.objects.create(
                order=order,
                product_id=item['product'],
                quantity=item['quantity'],
                price_at_purchase=item['price_at_purchase']
            )

        return Response(OrderSerializer(order).data, status=201)

@api_view(['PUT', 'DELETE','PATCH'])
def order_update_delete(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=404)
    
    
    if request.method in ['PUT', 'PATCH']:
        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    # if request.method == 'PUT':
    #     serializer = OrderSerializer(order, data=request.data, partial=True)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        order.delete()
        return Response({'message': 'Order deleted'})

# -------------------- Order Items --------------------

@api_view(['GET'])
def get_order_items(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=404)

    items = order.orderitem_set.all()
    return Response(OrderItemSerializer(items, many=True).data)

@api_view(['PUT', 'DELETE'])
def update_delete_order_item(request, item_id):
    try:
        item = OrderItem.objects.get(id=item_id)
    except OrderItem.DoesNotExist:
        return Response({'error': 'Order item not found'}, status=404)

    if request.method == 'PUT':
        serializer = OrderItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        item.delete()
        return Response({'message': 'Order item deleted'})


@api_view(['GET', 'POST'])
def user_orders(request, user_id):
    try:
        user = UserCustomer.objects.get(id=user_id)
    except UserCustomer.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    if request.method == 'GET':
        # Fetch orders in descending order of date (LIFO)
        orders = Order.objects.filter(user=user).order_by('-date')
        formatted_orders = []
        for order in orders:
            products = [
                {
                    "product": {
                        "id": item.product.id,
                        "quantity": item.quantity
                    }
                }
                for item in order.orderitem_set.all()
            ]
            formatted_orders.append({
                "id": order.id,
                "products": products,
                "totalAmount": order.total_amount,
                "date": order.date.isoformat(),
                "status": order.status,
                "address": order.address,
                "paymentMethod": order.payment_method
            })
        return Response(formatted_orders)

    elif request.method == 'POST':
        data = request.data
        products_data = data.get("products", [])

        if not products_data:
            return Response({'error': 'Products required'}, status=400)

        order = Order.objects.create(
            user=user,
            total_amount=data.get('totalAmount', 0),
            status=data.get('status', 'pending'),
            address=data.get('address', ''),
            payment_method=data.get('paymentMethod', 'cod')
        )

        for product_entry in products_data:
            product_info = product_entry.get('product', {})
            product_id = product_info.get('id')
            quantity = product_info.get('quantity', 1)

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({'error': f'Product with id {product_id} not found'}, status=404)

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price_at_purchase=product.price
            )

        return Response({
            "id": order.id,
            "products": [
                {
                    "product": {
                        "id": item.product.id,
                        "quantity": item.quantity
                    }
                }
                for item in order.orderitem_set.all()
            ],
            "totalAmount": order.total_amount,
            "date": order.date.isoformat(),
            "status": order.status,
            "address": order.address,
            "paymentMethod": order.payment_method
        }, status=201)


























# from django.shortcuts import render, get_object_or_404, redirect
# from django.http import JsonResponse
# from .models import (
#     UserCustomer, Product, ProductImage, Review, Cart,
#     Order, Wishlist, OrderItem
# )

# # -------------------- Product Detail Views --------------------

# def product_detail(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     images = ProductImage.objects.filter(product=product)
#     reviews = Review.objects.filter(product=product).select_related('user')
    
#     # Calculate average rating
#     avg_rating = 0
#     if reviews:
#         avg_rating = sum([r.rating for r in reviews]) / len(reviews)
    
#     context = {
#         'product': product,
#         'images': images,
#         'reviews': reviews,
#         'avg_rating': round(avg_rating, 1),
#         'review_count': len(reviews),
#     }
#     return render(request, 'ecommerce/product_detail.html', context)

# def product_list(request):
#     products = Product.objects.all().prefetch_related('images')
    
#     # Add average rating to each product
#     for product in products:
#         reviews = Review.objects.filter(product=product)
#         if reviews:
#             product.avg_rating = round(sum([r.rating for r in reviews]) / len(reviews), 1)
#         else:
#             product.avg_rating = 0
#         product.review_count = len(reviews)
    
#     context = {
#         'products': products,
#         'categories': Product.objects.values_list('category', flat=True).distinct(),
#         'brands': Product.objects.values_list('brand', flat=True).distinct(),
#     }
#     return render(request, 'ecommerce/product_list.html', context)

# def update_product(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
    
#     if request.method == 'POST':
#         product.name = request.POST.get('name', product.name)
#         product.price = request.POST.get('price', product.price)
#         product.description = request.POST.get('description', product.description)
#         product.category = request.POST.get('category', product.category)
#         product.brand = request.POST.get('brand', product.brand)
#         product.stock = request.POST.get('stock', product.stock)
#         product.featured = 'featured' in request.POST
#         product.trending = 'trending' in request.POST
#         product.save()
        
#         # Handle images
#         if 'images' in request.FILES:
#             ProductImage.objects.filter(product=product).delete()
#             for image in request.FILES.getlist('images'):
#                 ProductImage.objects.create(product=product, image_url=image)
        
#         return redirect('product_detail', product_id=product.id)
    
#     images = ProductImage.objects.filter(product=product)
#     context = {
#         'product': product,
#         'images': images,
#     }
#     return render(request, 'ecommerce/update_product.html', context)

# # -------------------- Order Detail Views --------------------

# def order_detail(request, order_id):
#     order = get_object_or_404(Order, id=order_id)
#     items = OrderItem.objects.filter(order=order).select_related('product')
#     user = order.user
    
#     context = {
#         'order': order,
#         'items': items,
#         'user': user,
#     }
#     return render(request, 'ecommerce/order_detail.html', context)

# def order_list(request):
#     orders = Order.objects.all().select_related('user').prefetch_related('orderitem_set__product')
    
#     context = {
#         'orders': orders,
#     }
#     return render(request, 'ecommerce/order_list.html', context)

# def update_order(request, order_id):
#     order = get_object_or_404(Order, id=order_id)
    
#     if request.method == 'POST':
#         order.status = request.POST.get('status', order.status)
#         order.address = request.POST.get('address', order.address)
#         order.payment_method = request.POST.get('payment_method', order.payment_method)
#         order.save()
        
#         # Update order items
#         for item in order.orderitem_set.all():
#             quantity_key = f'quantity_{item.id}'
#             if quantity_key in request.POST:
#                 item.quantity = request.POST[quantity_key]
#                 item.save()
        
#         return redirect('order_detail', order_id=order.id)
    
#     items = order.orderitem_set.all().select_related('product')
#     context = {
#         'order': order,
#         'items': items,
#         'status_choices': ['pending', 'shipped', 'delivered'],
#     }
#     return render(request, 'ecommerce/update_order.html', context)
