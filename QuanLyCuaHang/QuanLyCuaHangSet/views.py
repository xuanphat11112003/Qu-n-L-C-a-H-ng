from django.contrib.admin import action
from django.shortcuts import render

from QuanLyCuaHang.QuanLyCuaHangSet.models import User
from QuanLyCuaHang.QuanLyCuaHangSet.serializer import UserSerializer
from rest_framework import permissions, viewsets, generics, status, parsers


# Create your views here.


class Response:
    pass


class UserViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView, generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(methods=['get', 'patch'], url_path='current-user', detail=False)
    def get_current_user(self, request):
        user = request.user
        if request.method.__eq__('PATCH'):
            for k, v in request.data.items():
                setattr(user, k, v)
            user.set_password(user.password)
            user.save()

        return Response(UserSerializer(user).data)