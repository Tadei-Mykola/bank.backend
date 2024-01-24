from rest_framework import serializers

from .models.userModel import userModel

class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = userModel
        fields = '__all__'