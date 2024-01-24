from rest_framework import generics
from .models.userModel import userModel
from .serializers import UserModelSerializer

class UserModelListCreateView(generics.ListCreateAPIView):
    queryset = userModel.objects.all()
    serializer_class = UserModelSerializer