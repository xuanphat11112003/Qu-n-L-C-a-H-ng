from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from QuanLyCuaHang.QuanLyCuaHangSet.models import User, KhachHang


class UserSerializer(ModelSerializer):

    def create(self, validated_data):
        data = validated_data.copy()
        user = User(**data)
        user.set_password(user.password)
        user.save()
        a= KhachHang(user=user)
        a.save()

        return user

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'password', 'email', 'image_url','avatar', 'role']
        extra_kwargs = {
            'password': {
                'write_only': 'true'
            }
        }