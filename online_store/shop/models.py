from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField


class UserProfile(AbstractUser):
    age = models.PositiveSmallIntegerField(default=0,null=True,blank=True,
                                           validators=[MinValueValidator(15),
                                                       MaxValueValidator(100)])
    register_date = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    phone_number = PhoneNumberField(null=True,blank=True,region='KG')

    STATUS_CHOICES = (
        ('gold', 'gold'),
        ('silver', 'silver'),
        ('bronze', 'bronze'),
        ('simple', 'simple'),

    )
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='simple',null=True,blank=True)

    def __str__(self):
        return f'{self.first_name}-{self.last_name}'


class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.category_name


class Product(models.Model):
    product_name = models.CharField(max_length=30)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    text = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True, verbose_name='cash')
    product_video = models.FileField(upload_to='video', verbose_name='video', null=True, blank=True)
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.product_name

    def get_average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return round(sum(rating.stars for rating in ratings) / ratings.count(), 1)
        return 0


class ProductPhotos(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')


class Rating(models.Model):
    product = models.ForeignKey(Product, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    stars = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], verbose_name='ratings')

    def __str__(self):
        return f'{self.product}-{self.user}-{self.stars}'


class Review(models.Model):
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    txt = models.TextField()
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    parent_review = models.ForeignKey('self', related_name='replies', on_delete=models.CASCADE, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author}-{self.product}'


class Cart(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='carts')
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user}'

    def get_total_price(self):
        total_price=sum(item.get_total_price() for item in self.items.all())
        discount=0

        if self.user.status == 'gold':
            discount = 0.75
        elif self.user.status == 'silver':
            discount = 0.50
        elif self.user.status == 'bronze':
            discount = 0.25
        final_price = total_price * (1 - discount)
        return final_price


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)

    def get_total_price(self):
        return self.product.price * self.quantity
