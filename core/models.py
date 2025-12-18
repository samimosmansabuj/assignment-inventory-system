from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    total_stock = models.PositiveIntegerField(default=0)
    available_stock = models.PositiveIntegerField()
    reserved_stock = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        assert self.available_stock + self.reserved_stock == self.total_stock
        super().save(*args, **kwargs)

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['total']),
        ]
    
    def save(self, *args, **kwargs):
        if self.product and self.total is None:
            self.total = float(self.product.price) * float(self.quantity)
        super().save(*args, **kwargs)


class AuditLog(models.Model):
    actor = models.CharField(max_length=50)
    action = models.CharField(max_length=100)
    object_type = models.CharField(max_length=50)
    object_id = models.CharField(max_length=50)
    old_value = models.JSONField(null=True)
    new_value = models.JSONField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.timestamp} - {self.actor} - {self.action}"


def audit_log(actor, action, obj, old_value=None, new_value=None):
    AuditLog.objects.create(
        actor=actor,
        action=action,
        object_type=obj.__class__.__name__,
        object_id=obj.id,
        old_value=old_value,
        new_value=new_value
    )

