from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from .models import Book, Deal, EmailUser

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__' 

class DealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deal
        fields = '__all__' 

class EmailUserSerializer(serializers.ModelSerializer):   
    def create(self, validated_data):
        user = get_user_model().objects.create(
            email = validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = EmailUser
        fields = '__all__' 
        write_only_fields = ('password')
        read_only_fields = ('is_staff', 'is_superuser', 'is_active', 'date_joined',)

class UserLoginSerializer(serializers.ModelSerializer):
    token = serializers.CharField(allow_blank = True, read_only = True)
    email = serializers.EmailField(label = 'Email Address')
    class Meta:
        model = EmailUser
        fields = '__all__' 
        write_only_fields = ('password')
        read_only_fields = ('is_staff', 'is_superuser', 'is_active', 'date_joined',)