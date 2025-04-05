from rest_framework import serializers
from .models import Product, ProductImage, Review, UserCustomer

class UserCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCustomer
        fields = ['id', 'name', 'email', 'address', 'phone']

class ReviewSerializer(serializers.ModelSerializer):
    userId = serializers.IntegerField(source='user.id')
    userName = serializers.CharField(source='user.name')

    class Meta:
        model = Review
        fields = ['id', 'userId', 'userName', 'rating', 'comment', 'date']

class ProductSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    reviews = ReviewSerializer(source='review_set', many=True, read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'price', 'description', 'category', 'images',
            'rating', 'reviews', 'brand', 'stock', 'featured', 'trending'
        ]

    def get_images(self, obj):
        return [img.image_url for img in obj.images.all()]

    def get_rating(self, obj):
        reviews = obj.review_set.all()
        if not reviews:
            return 0
        return round(sum([r.rating for r in reviews]) / len(reviews), 1)
