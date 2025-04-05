from django.db import models

class UserCustomer(models.Model):  
    name = models.TextField(null=False)
    email = models.TextField(unique=True, null=False)
    password = models.TextField(null=False)
    address = models.TextField(null=True, blank=True)
    phone = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.TextField(null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    description = models.TextField(null=True, blank=True)
    category = models.TextField(null=False)
    brand = models.TextField(null=True, blank=True)
    stock = models.IntegerField(default=0)
    featured = models.BooleanField(default=False)
    trending = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField()

    def __str__(self):
        return f"{self.product.name} Image"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    ]
    
    user = models.ForeignKey(UserCustomer, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    address = models.TextField(null=False)
    payment_method = models.TextField(null=False)

    def __str__(self):
        return f"Order {self.id} - {self.user.name}"

class Cart(models.Model):
    user = models.ForeignKey(UserCustomer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.user.name} - {self.product.name} ({self.quantity})"

class Review(models.Model):
    user = models.ForeignKey(UserCustomer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    comment = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} - {self.product.name} ({self.rating})"

class Wishlist(models.Model):
    user = models.ForeignKey(UserCustomer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.name} - {self.product.name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2, null=False)

    def __str__(self):
        return f"Order {self.order.id} - {self.product.name} ({self.quantity})"
