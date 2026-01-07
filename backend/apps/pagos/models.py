from django.db import models

class Pago(models.Model):
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    whatsappNumber = models.CharField(max_length=20)
    email = models.CharField(max_length=100)
    pagoId = models.IntegerField()

    