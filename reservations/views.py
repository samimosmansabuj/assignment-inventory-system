from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import create_reservation
from .serializers import ReservationSerializer


class ReservationCreateAPI(APIView):
    def post(self, request):
        try:
            reservation = create_reservation(
                product_id=request.data['product_id'],
                qty=request.data['quantity'],
                actor=str(request.user)
            )
            serializer = ReservationSerializer(reservation)
            return Response({
                'request_id': request.request_id,
                'reservation_id': reservation.id,
                'expires_at': reservation.expires_at,
                'reservation': serializer.data
            })
        except Exception as e:
            return Response({
                'request_id': request.request_id,
                'error': str(e)
            }, status=400)