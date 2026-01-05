from django.urls import path 
from .views import (
    ListPartituras,
    DetailPartitura,
    ListPartiturasDestacadas,
    CreatePay
)

urlpatterns = [
    path('partituras/list/', ListPartituras.as_view()),
    path('partituras/list/destacados/', ListPartiturasDestacadas.as_view()),
    path('partituras/get/<slug:slug>/', DetailPartitura.as_view()),
    path('partituras/create/pay/', CreatePay.as_view()),
]