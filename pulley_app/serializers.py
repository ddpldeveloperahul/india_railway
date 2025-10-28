from rest_framework import serializers
from .models import Image_database

class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image_database
        fields = '__all__'


