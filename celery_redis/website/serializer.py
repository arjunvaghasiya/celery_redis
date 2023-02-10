from rest_framework import serializers, status
from django.contrib.auth.models import User
from .models import *
import re


class RegisterSerializer(serializers.ModelSerializer):
    # import pdb;pdb.set_trace()
    password2 = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = User
        fields = ('username','email','password','password2',)
        extra_kwargs = {
            "password":{'write_only':True}
            }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    # import pdb;pdb.set_trace()
    def create(self, validated_data):
          
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            is_active=False,
            is_staff = True,
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class News_Serializer(serializers.ModelSerializer):
    class Meta:
        model=News_Data
        fields=('link_n', 'headline', 'category', 'short_description', 'authors', 'date_d')
        
class File_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Store_File
        fields="__all__"
        
        
class Top_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Top_Status
        fields="__all__"