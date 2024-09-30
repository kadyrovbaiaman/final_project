from rest_framework import serializers
from .models import *

from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=UserProfile
        fields=['username','email','password','first_name','last_name','age','phone_number','status']
        extra_kwargs={'password':{'write_only':True}}

    def create(self, validated_data):
        user=UserProfile.objects.create_user(**validated_data)
        return user

    def to_representation(self, instance):
        refresh=RefreshToken.for_user(instance)
        return {
            'user':{
                'username':instance.username,
                'email':instance.email,
            },
            'access':str(refresh.access_token),
            'refresh':str(refresh),
        }


class LoginSerialize(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError('Неверный учетные данные')

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {
            'user': {
                'username': instance.username,
                'email': instance.email,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class UserProfileSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['product_name']


class ProductPhotosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPhotos
        fields = '__all__'


class RatingSerializer(serializers.ModelSerializer):
    user = UserProfileSimpleSerializer()
    product = ProductSimpleSerializer()

    class Meta:
        model = Rating
        fields = ['user', 'product', 'stars']


class ReviewSerializer(serializers.ModelSerializer):
    author = UserProfileSimpleSerializer()
    product = ProductSimpleSerializer()
    created_date = serializers.DateTimeField(format='%d-%m-%Y %H:%M')

    class Meta:
        model = Review
        fields = ['author', 'product', 'txt', 'parent_review', 'created_date']


class ProductListSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'price', 'active', 'average_rating', 'date']

    def get_average_rating(self, obj):
        return obj.get_average_rating()


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    ratings = RatingSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    date = serializers.DateTimeField(format='%d-%m-%Y %H:%M')
    average_rating = serializers.SerializerMethodField()
    owner=UserProfileSimpleSerializer()

    class Meta:
        model = Product
        fields = ['id', 'owner','category', 'product_name', 'text', 'price', 'active', 'date', 'product_video',
                  'average_rating','ratings', 'reviews', ]

    def get_average_rating(self, obj):
        return obj.get_average_rating()


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True, source='product')
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'get_total_price',]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    created_date=serializers.DateTimeField(format='%d-%m-%Y %H:%M')

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price','created_date']

    def get_total_price(self, obj):
        return obj.get_total_price()
