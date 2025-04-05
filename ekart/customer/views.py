from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import UserCustomer
from .serializers import UserCustomerSerializer
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
