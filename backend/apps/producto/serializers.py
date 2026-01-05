from rest_framework import serializers

from .models import (
    CategoriaProducto,
    Producto
)

class CategoriaProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaProducto
        fields = '__all__'

class ProductoSerializer(serializers.ModelSerializer):
    categoria = CategoriaProductoSerializer()
    class Meta:
        model = Producto
        fields = '__all__'