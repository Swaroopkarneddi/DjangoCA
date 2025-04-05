from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import UserCustomer, Product, ProductImage, Review
from .serializers import UserCustomerSerializer, ProductSerializer, ReviewSerializer
from django.contrib.auth.hashers import make_password, check_password

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
        password=make_password(data['password'])
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

@api_view(['GET'])
def get_all_products(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def add_product(request):
    data = request.data
    images = data.pop('images', [])
    reviews = data.pop('reviews', [])

    product = Product.objects.create(**data)

    for img in images:
        ProductImage.objects.create(product=product, image_url=img)

    for rev in reviews:
        user = UserCustomer.objects.get(id=rev['userId'])  # make sure user exists
        Review.objects.create(
            user=user,
            product=product,
            rating=rev['rating'],
            comment=rev.get('comment', ''),
            date=rev.get('date')
        )

    serializer = ProductSerializer(product)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
