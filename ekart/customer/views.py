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


# @api_view(['GET', 'POST'])
# def wishlist_list_create(request):
#     if request.method == 'GET':
#         wish = Wishlist.objects.all()
#         return Response(WishlistSerializer(wish, many=True).data)
#     elif request.method == 'POST':
#         serializer = WishlistSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=201)
#         return Response(serializer.errors, status=400)

# @api_view(['DELETE'])
# def delete_wishlist_item(request, wishlist_id):
#     try:
#         wish = Wishlist.objects.get(id=wishlist_id)
#         wish.delete()
#         return Response({'message': 'Wishlist item deleted'})
#     except Wishlist.DoesNotExist:
#         return Response({'error': 'Wishlist item not found'}, status=404)

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

@api_view(['PUT', 'DELETE'])
def order_update_delete(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=404)

    if request.method == 'PUT':
        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

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


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import UserCustomer, Order, OrderItem, Product
from .serializers import ProductSerializer
from django.utils.dateparse import parse_datetime

@api_view(['GET', 'POST'])
def user_orders(request, user_id):
    try:
        user = UserCustomer.objects.get(id=user_id)
    except UserCustomer.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    if request.method == 'GET':
        orders = Order.objects.filter(user=user).order_by('-date')
        result = []
        for order in orders:
            order_items = order.orderitem_set.all()
            cart_items = []

            for item in order_items:
                product = ProductSerializer(item.product).data
                cart_items.append({
                    'product': product,
                    'quantity': item.quantity
                })

            result.append({
                'id': order.id,
                'products': cart_items,
                'totalAmount': float(order.total_amount),
                'date': order.date.isoformat(),
                'status': order.status,
                'address': order.address,
                'paymentMethod': order.payment_method
            })

        return Response(result)

    elif request.method == 'POST':
        data = request.data
        products = data.get('products', [])

        order = Order.objects.create(
            user=user,
            total_amount=data['totalAmount'],
            address=data['address'],
            payment_method=data['paymentMethod']
        )

        for item in products:
            product_id = item['product']['id']
            quantity = item['quantity']
            price_at_purchase = item['product']['price']

            OrderItem.objects.create(
                order=order,
                product_id=product_id,
                quantity=quantity,
                price_at_purchase=price_at_purchase
            )

        # Return created order in compatible format
        cart_items = []
        for item in order.orderitem_set.all():
            product = ProductSerializer(item.product).data
            cart_items.append({
                'product': product,
                'quantity': item.quantity
            })

        result = {
            'id': order.id,
            'products': cart_items,
            'totalAmount': float(order.total_amount),
            'date': order.date.isoformat(),
            'status': order.status,
            'address': order.address,
            'paymentMethod': order.payment_method
        }

        return Response(result, status=201)


# {
#   "products": [
#     {
#       "product": {
#         "id": 3,
#         "name": "Phone X",
#         "price": 599,
#         "description": "Latest model",
#         "category": "Electronics",
#         "images": ["https://example.com/img.jpg"],
#         "rating": 4.5,
#         "reviews": [],
#         "brand": "BrandX",
#         "stock": 10
#       },
#       "quantity": 2
#     }
#   ],
#   "totalAmount": 1198,
#   "address": "123 Main St",
#   "paymentMethod": "Credit Card"
# }


# {
#   "id": 10,
#   "products": [
#     {
#       "product": {
#         "id": 3,
#         "name": "Phone X",
#         "price": 599,
#         "description": "Latest model",
#         "category": "Electronics",
#         "images": ["https://example.com/img.jpg"],
#         "rating": 4.5,
#         "reviews": [],
#         "brand": "BrandX",
#         "stock": 10,
#         "featured": false,
#         "trending": false
#       },
#       "quantity": 2
#     }
#   ],
#   "totalAmount": 1198,
#   "date": "2025-04-15T16:45:21.123Z",
#   "status": "pending",
#   "address": "123 Main St",
#   "paymentMethod": "Credit Card"
# }
