from django.db import models
from django.utils import timezone


class Reservation(models.Model):
    product = models.ForeignKey('core.Product', on_delete=models.CASCADE)
    order = models.ForeignKey('core.Order', on_delete=models.SET_NULL, blank=True, null=True)
    
    quantity = models.PositiveIntegerField()
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    confirm = models.BooleanField(default=False)
    
    @property
    def is_expired(self):
        is_expired = timezone.now() > self.expires_at
        # if is_expired and self.is_active:
        #     self.is_active = False
        #     self.save() 
        return is_expired

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

    # def save(self, *args, **kwargs):
    #     assert self.quantity <= self.product.available_stock
    #     super().save(*args, **kwargs)
