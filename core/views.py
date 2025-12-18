from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from .models import Order, Product
from .services import transition_order
from .serializers import OrderSerializer, ProductSerializer
from reservations.services import create_order_and_reservation
from rest_framework.pagination import CursorPagination
from django_filters import rest_framework as filters


class OrderCursorPagination(CursorPagination):
    page_size = 10
    ordering = "-created_at"


class ProductAPIViews(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class OrderAPIViews(viewsets.ModelViewSet):
    queryset = Order.objects.select_related('product').all()
    serializer_class = OrderSerializer
    pagination_class = OrderCursorPagination
    # filter_backends = (filters.DjangoFilterBackend, OrderingFilter)

    def get_queryset(self):
        queryset = Order.objects.all()

        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        min_total = self.request.query_params.get("min_total")
        max_total = self.request.query_params.get("max_total")
        status = self.request.query_params.get("status")

        if start_date and end_date:
            queryset = queryset.filter(created_at__range=[start_date, end_date])
        if status:
            queryset = queryset.filter(status=status)
        if min_total:
            queryset = queryset.filter(total__gte=min_total)
        if max_total:
            queryset = queryset.filter(total__lte=max_total)
        
        sort = self.request.query_params.get("sort")
        if sort == "newest":
            queryset = queryset.order_by("-created_at")
        elif sort == "highest":
            queryset = queryset.order_by("-total")

        queryset = queryset.select_related("product")

        return queryset

    def post(self, request, *args, **kwargs):
        return Response(
            {
                "request_id": request.request_id,
                "message": "Use /create-order/ endpoint to create orders.",
            }, status=405
        )


class OrderCreateAPI(APIView):
    def get(self, request):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response({"request_id": request.request_id, "data": serializer.data})

    def post(self, request):
        order = create_order_and_reservation(
            product_id=request.data.get("product"),
            qty=request.data.get("quantity"),
            actor=str(request.user),
        )
        serializer = OrderSerializer(order)
        return Response(
            {
                "request_id": request.request_id,
                "data": serializer.data,
            }
        )


class OrderTransitionAPI(APIView):
    def post(self, request, pk):
        try:
            order = Order.objects.get(id=pk)
            transition_order(order, request.data["new_status"])
            return Response(
                {
                    "request_id": request.request_id,
                    "order_id": order.id,
                    "status": order.status,
                }
            )
        except Exception as e:
            return Response(
                {"request_id": request.request_id, "error": str(e)}, status=400
            )
