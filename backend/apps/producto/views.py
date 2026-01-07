from django.shortcuts import render, get_object_or_404

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework import status 
from rest_framework.response import Response
from dotenv import load_dotenv
import os, requests, uuid, json, threading
from rest_framework.exceptions import ValidationError
from django.core.mail import EmailMessage
from twilio.rest import Client
from django.conf import settings

from .models import (
    CategoriaProducto,
    Producto
)
from .serializers import (
    CategoriaProductoSerializer,
    ProductoSerializer
)

from apps.pagos.models import Pago

class ListPartituras(ListAPIView):
    
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

class ListPartiturasDestacadas(ListAPIView):
    
    serializer_class = ProductoSerializer

    def get_queryset(self):
        return Producto.objects.filter(tieneDestacado=True)

class DetailPartitura(APIView):

    def get(self,request,*args,**kwargs):

        slug = kwargs.get('slug')

        partitura = get_object_or_404(Producto, slug=slug)

        serializer = ProductoSerializer(partitura, many=False)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CreatePay(APIView):

    def enviar_partitura_email(self, to_email, partitura_id):
        try:
            producto = Producto.objects.get(id=partitura_id)

            email = EmailMessage(
                subject="Partitura",
                body=producto.nombre,
                to=[to_email]
            )

            email.attach_file(producto.archivo.path)
            email.send()

        except Exception as e:
            print("Error enviando email:", e)

    def validate_required_fields(self, request, required_fields):
        errors = {}

        for field in required_fields:
            if field not in request.data:
                errors[field] = "Este campo es obligatorio"
            elif request.data[field] in [None, "", []]:
                errors[field] = "Este campo no puede estar vacío"

        if errors:
            raise ValidationError(errors)

    def post(self,request,*args,**kwargs):

        required_fields = [
            "otp",
            "phoneNumber",
            "email",
            "partituraId",
            "whatsappNumber"
        ]

        self.validate_required_fields(request, required_fields)

        bodyToken = {
            'otp': request.data['otp'],
            'phoneNumber': request.data['phoneNumber'],
            'requestId': str(uuid.uuid4())
        }

        headersToken = {
            'Content-Type': 'application/json',
        }

        urlToken = os.getenv('MP_URL_TOKEN') + os.getenv('MP_PUBLIC_KEY')

        responseToken = requests.post(url=urlToken, headers=headersToken, json=bodyToken)

        if responseToken.status_code == 200:

            res = responseToken.json()

            headersPayment = {
                'Authorization': f'Bearer {os.getenv('MP_ACCESS_TOKEN')}',
                'Content-Type': 'application/json',
                'x-idempotency-key': str(res['security_code_id'])
            }

            bodyPay = {
                'token': str(res['id']),
                'transaction_amount': int(Producto.objects.get(id=request.data['partituraId']).precio * 100),
                'description': str(Producto.objects.get(id=request.data['partituraId']).nombre),
                'installments': 1,
                'payment_method_id': 'yape',
                'payer': {
                    'email': str(request.data['email'])
                }
            }


            responsePayment = requests.post(url=os.getenv('MP_URL_PAYMENT'), headers=headersPayment, json=bodyPay)

            if responsePayment.status_code == 201:

                resPayment = responsePayment.json()

                if resPayment['status'] == "approved":
                
                    to_email = str(request.data['email'])
                    partitura_id = request.data['partituraId']

                    threading.Thread(
                        target=self.enviar_partitura_email,
                        args=(to_email, partitura_id)
                    ).start()

                    dataPay = {
                        'monto': int(Producto.objects.get(id=request.data['partituraId']).precio),
                        'whatsappNumber': request.data["whatsappNumber"],
                        'email': request.data['email'],
                        'pagoId': resPayment['id'],
                    }

                    pago = Pago(**dataPay)
                    pago.save()  

                    return Response(True, status=status.HTTP_200_OK)

                return Response({"message": 'Algo salio mal durante el pago'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"message": "Algo salio mal en el Pago"}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({"message": "Algo salio mal en el token"}, status=status.HTTP_400_BAD_REQUEST)