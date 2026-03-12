from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Service
from .serializers import ServiceSerializer

class ServiceCreateView(APIView):

    def post(self, request):
        serializer = ServiceSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ServiceListView(APIView):

    def get(self, request):
        services = Service.objects.all()
        serializer = ServiceSerializer(services, many=True, context={'request': request})
        return Response({
            "count": services.count(),
            "services": serializer.data
        })

class ServiceDetailView(APIView):

    def get(self, request, pk):
        try:
            service = Service.objects.get(id=pk)
        except Service.DoesNotExist:
            return Response({"error": "Service not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ServiceSerializer(service, context={'request': request})
        return Response(serializer.data)