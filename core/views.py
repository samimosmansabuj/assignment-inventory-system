from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from .models import Order, Product
from .services import transition_order
from .serializers import OrderSerializer, ProductSerializer
from reservations.services import create_order_and_reservation

class ProductAPIViews(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class OrderCreateAPI(APIView):
    def get(self, request):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response({
            'request_id': request.request_id,
            'data': serializer.data
        })
    
    def post(self, request):
        order = create_order_and_reservation(product_id=request.data.get("product"), qty=request.data.get("quantity"), actor=str(request.user))
        serializer = OrderSerializer(order)
        return Response({
            'request_id': request.request_id,
            'order_id': serializer.instance.id,
            'status': serializer.instance.status,
            'data': serializer.data
        })

class OrderTransitionAPI(APIView):
    def post(self, request, pk):
        try:
            order = Order.objects.get(id=pk)
            transition_order(order, request.data['new_status'])
            return Response({
                'request_id': request.request_id,
                'order_id': order.id,
                'status': order.status
            })
        except Exception as e:
            return Response({
                'request_id': request.request_id,
                'error': str(e)
            }, status=400)
