# myapp/views.py
from datetime import datetime

from django.db import transaction
from rest_framework import status, viewsets, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from .models import HoaDon, KhachHang, NhanVien, SanPham, HoaDon_SP, User, TichDiemVoucher, NhanVien_QL,Comment
from .serializer import HoaDonSerializer, UserSerializer, SanPhamSerializer, HoaDonSPSerializer, NhanVienSerializer,NhanVien_QLSerializer, KhachHangSerializer,CommentSerializer

import hashlib
import hmac
import json
import urllib
import urllib.parse
import urllib.request
import random
import requests
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
# from django.utils.http import urlquote

from QuanLyCuaHangSet.models import PaymentForm
from QuanLyCuaHangSet.vnpay import vnpay



class UserViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView, generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # permission_classes = [permissions.IsAuthenticated]

    @action(methods=['get', 'patch'], url_path='current-user', detail=False)
    def get_current_user(self, request):
        user = request.user

        if request.method == 'PATCH':
            serializer = self.get_serializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                if 'password' in request.data:
                    # Ensure password is hashed before saving
                    user.set_password(request.data['password'])
                    user.save(update_fields=['password'])
                serializer.save()

                # Update related models based on user role
                if user.user_role == User.UserRole.ROLE_CUSTOMER:
                    khach_hang = KhachHang.objects.get(user=user)
                    khach_hang_serializer = KhachHangSerializer(khach_hang, data=request.data, partial=True)
                    if khach_hang_serializer.is_valid():
                        khach_hang_serializer.save()
                    else:
                        return Response(khach_hang_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                elif user.user_role == User.UserRole.ROLE_USER:
                    nhan_vien = NhanVien.objects.get(user=user)
                    nhan_vien_serializer = NhanVienSerializer(nhan_vien, data=request.data, partial=True)
                    if nhan_vien_serializer.is_valid():
                        nhan_vien_serializer.save()
                    else:
                        return Response(nhan_vien_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                elif user.user_role == User.UserRole.ROLE_ADMIN:
                    nhan_vien_ql = NhanVien_QL.objects.get(user=user)
                    nhan_vien_ql_serializer = NhanVien_QLSerializer(nhan_vien_ql, data=request.data, partial=True)
                    if nhan_vien_ql_serializer.is_valid():
                        nhan_vien_ql_serializer.save()
                    else:
                        return Response(nhan_vien_ql_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(UserSerializer(user).data)


    def get_serializer_class(self):
    # Override serializer class if needed
     return UserSerializer


class HoaDonViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = HoaDon.objects.all()
    serializer_class = HoaDonSerializer

    def get_serializer_class(self):
        if self.request.user.is_authenticated:
            return None;
        else:
            return HoaDonSerializer

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.IsAuthenticated()]  # Adjust permissions as needed
        else:
            return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = self.queryset

        if self.action == 'list':
            q = self.request.query_params.get('q')
            if q:
                queryset = queryset.filter(id__icontains=q)  # Adjust filter based on your needs
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        products = data.get('products', [])  # List of products

        # Fetch KhachHang and NhanVien instances
        khach_hang = KhachHang.objects.get(id=data.get("khach_hang"))
        nhan_vien = NhanVien.objects.get(id=data.get("nhan_vien"))

        # Create HoaDon object
        hoa_don_data = {
            "ghi_chu": data.get("ghi_chu", ""),
            "tong_tien": data.get("tong_tien", 0),
            "khach_hang": khach_hang,  # Use the fetched instance
            "nhan_vien": nhan_vien,  # Use the fetched instance
        }

        hoa_don = HoaDon.objects.create(**hoa_don_data)

        # Create HoaDon_SP objects
        for product in products:
            san_pham_id = product.get('san_pham_id')
            so_luong = product.get('so_luong', 0)

            if san_pham_id:
                HoaDon_SP.objects.create(
                    hoa_don=hoa_don,
                    san_pham_id=san_pham_id,
                    so_luong=so_luong
                )

        return Response(
            HoaDonSerializer(hoa_don, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    @action(methods=['put'], detail=True)
    def update_partial(self, request, pk=None):
        try:
            hoa_don = HoaDon.objects.get(pk=pk)
        except HoaDon.DoesNotExist:
            return Response({"error": "Hóa đơn không tồn tại"}, status=status.HTTP_404_NOT_FOUND)
        serializer = HoaDonSerializer(hoa_don, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['delete'], detail=True)
    def delete(self, request, pk=None):
        try:
            hoa_don = HoaDon.objects.get(pk=pk)
            hoa_don.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except HoaDon.DoesNotExist:
            return Response({"error": "Hóa đơn không tồn tại"}, status=status.HTTP_404_NOT_FOUND)


class StatisticViewSet(viewsets.ViewSet):
    queryset = HoaDon.objects.all()
    serializer_class = HoaDonSerializer

    def get_queryset(self):
        queryset = self.queryset
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        if month and year:
            queryset = queryset.filter(ngay_lap__year=year, ngay_lap__month=month)
        queryset = queryset.annotate(month=TruncMonth('ngay_lap')).values('month').annotate(
            total_revenue=Sum('tong_tien')).order_by('month')
        return queryset


class SanPhamViewSet(viewsets.ModelViewSet):
    queryset = SanPham.objects.filter(active=True)
    serializer_class = SanPhamSerializer
    @action(methods=['get'], url_path='comments', detail=True)
    def show_comments(self, request, pk=None):
        # Lấy sản phẩm dựa trên pk
        product = self.get_object()

        # Lấy các bình luận liên quan đến sản phẩm
        comments = Comment.objects.filter(product=product)

        # Serialize dữ liệu bình luận
        serializer = CommentSerializer(comments, many=True)

        # Trả về phản hồi
        return Response(serializer.data)

    @action(methods=['post'], url_path='add_comment', detail=True)
    def add_comment(self, request, pk=None):
        user = request.user
        product = self.get_object()
        content = request.data.get("content")

        if not user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."},
                            status=status.HTTP_403_FORBIDDEN)

        if not content:
            return Response({"detail": "Content is required."}, status=status.HTTP_400_BAD_REQUEST)

        comment = Comment.objects.create(content=content, user=user, product=product)
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CommentViewSet(viewsets.ViewSet, generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer



def index(request):
    return render(request, "payment/index.html", {"title": "Danh sách demo"})


def hmacsha512(key, data):
    byteKey = key.encode('utf-8')
    byteData = data.encode('utf-8')
    return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest()


def payment(request):

    if request.method == 'POST':
        # Process input data and build url payment
        form = PaymentForm(request.POST)
        if form.is_valid():
            order_type = form.cleaned_data['order_type']
            order_id = form.cleaned_data['order_id']
            amount = form.cleaned_data['amount']
            order_desc = form.cleaned_data['order_desc']
            bank_code = form.cleaned_data['bank_code']
            language = form.cleaned_data['language']
            ipaddr = get_client_ip(request)
            # Build URL Payment
            vnp = vnpay()
            vnp.requestData['vnp_Version'] = '2.1.0'
            vnp.requestData['vnp_Command'] = 'pay'
            vnp.requestData['vnp_TmnCode'] = settings.VNPAY_TMN_CODE
            vnp.requestData['vnp_Amount'] = amount * 100
            vnp.requestData['vnp_CurrCode'] = 'VND'
            vnp.requestData['vnp_TxnRef'] = order_id
            vnp.requestData['vnp_OrderInfo'] = order_desc
            vnp.requestData['vnp_OrderType'] = order_type
            # Check language, default: vn
            if language and language != '':
                vnp.requestData['vnp_Locale'] = language
            else:
                vnp.requestData['vnp_Locale'] = 'vn'
                # Check bank_code, if bank_code is empty, customer will be selected bank on VNPAY
            if bank_code and bank_code != "":
                vnp.requestData['vnp_BankCode'] = bank_code

            vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')  # 20150410063022
            vnp.requestData['vnp_IpAddr'] = ipaddr
            vnp.requestData['vnp_ReturnUrl'] = settings.VNPAY_RETURN_URL
            vnpay_payment_url = vnp.get_payment_url(settings.VNPAY_PAYMENT_URL, settings.VNPAY_HASH_SECRET_KEY)
            print(vnpay_payment_url)
            return redirect(vnpay_payment_url)
        else:
            print("Form input not validate")
    else:
        return render(request, "payment/payment.html", {"title": "Thanh toán"})


def payment_ipn(request):
    inputData = request.GET
    if inputData:
        vnp = vnpay()
        vnp.responseData = inputData.dict()
        order_id = inputData['vnp_TxnRef']
        amount = inputData['vnp_Amount']
        order_desc = inputData['vnp_OrderInfo']
        vnp_TransactionNo = inputData['vnp_TransactionNo']
        vnp_ResponseCode = inputData['vnp_ResponseCode']
        vnp_TmnCode = inputData['vnp_TmnCode']
        vnp_PayDate = inputData['vnp_PayDate']
        vnp_BankCode = inputData['vnp_BankCode']
        vnp_CardType = inputData['vnp_CardType']
        if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            # Check & Update Order Status in your Database
            # Your code here
            firstTimeUpdate = True
            totalamount = True
            if totalamount:
                if firstTimeUpdate:
                    if vnp_ResponseCode == '00':
                        print('Payment Success. Your code implement here')
                    else:
                        print('Payment Error. Your code implement here')

                    # Return VNPAY: Merchant update success
                    result = JsonResponse({'RspCode': '00', 'Message': 'Confirm Success'})
                else:
                    # Already Update
                    result = JsonResponse({'RspCode': '02', 'Message': 'Order Already Update'})
            else:
                # invalid amount
                result = JsonResponse({'RspCode': '04', 'Message': 'invalid amount'})
        else:
            # Invalid Signature
            result = JsonResponse({'RspCode': '97', 'Message': 'Invalid Signature'})
    else:
        result = JsonResponse({'RspCode': '99', 'Message': 'Invalid request'})

    return result


def payment_return(request):
    inputData = request.GET
    if inputData:
        vnp = vnpay()
        vnp.responseData = inputData.dict()
        order_id = inputData['vnp_TxnRef']
        amount = int(inputData['vnp_Amount']) / 100
        order_desc = inputData['vnp_OrderInfo']
        vnp_TransactionNo = inputData['vnp_TransactionNo']
        vnp_ResponseCode = inputData['vnp_ResponseCode']
        vnp_TmnCode = inputData['vnp_TmnCode']
        vnp_PayDate = inputData['vnp_PayDate']
        vnp_BankCode = inputData['vnp_BankCode']
        vnp_CardType = inputData['vnp_CardType']
        if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            if vnp_ResponseCode == "00":
                return render(request, "payment/payment_return.html", {"title": "Kết quả thanh toán",
                                                               "result": "Thành công", "order_id": order_id,
                                                               "amount": amount,
                                                               "order_desc": order_desc,
                                                               "vnp_TransactionNo": vnp_TransactionNo,
                                                               "vnp_ResponseCode": vnp_ResponseCode})
            else:
                return render(request, "payment/payment_return.html", {"title": "Kết quả thanh toán",
                                                               "result": "Lỗi", "order_id": order_id,
                                                               "amount": amount,
                                                               "order_desc": order_desc,
                                                               "vnp_TransactionNo": vnp_TransactionNo,
                                                               "vnp_ResponseCode": vnp_ResponseCode})
        else:
            return render(request, "payment/payment_return.html",
                          {"title": "Kết quả thanh toán", "result": "Lỗi", "order_id": order_id, "amount": amount,
                           "order_desc": order_desc, "vnp_TransactionNo": vnp_TransactionNo,
                           "vnp_ResponseCode": vnp_ResponseCode, "msg": "Sai checksum"})
    else:
        return render(request, "payment/payment_return.html", {"title": "Kết quả thanh toán", "result": ""})


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

n = random.randint(10**11, 10**12 - 1)
n_str = str(n)
while len(n_str) < 12:
    n_str = '0' + n_str


def query(request):
    if request.method == 'GET':
        return render(request, "payment/query.html", {"title": "Kiểm tra kết quả giao dịch"})

    url = settings.VNPAY_API_URL
    secret_key = settings.VNPAY_HASH_SECRET_KEY
    vnp_TmnCode = settings.VNPAY_TMN_CODE
    vnp_Version = '2.1.0'

    vnp_RequestId = n_str
    vnp_Command = 'querydr'
    vnp_TxnRef = request.POST['order_id']
    vnp_OrderInfo = 'kiem tra gd'
    vnp_TransactionDate = request.POST['trans_date']
    vnp_CreateDate = datetime.now().strftime('%Y%m%d%H%M%S')
    vnp_IpAddr = get_client_ip(request)

    hash_data = "|".join([
        vnp_RequestId, vnp_Version, vnp_Command, vnp_TmnCode,
        vnp_TxnRef, vnp_TransactionDate, vnp_CreateDate,
        vnp_IpAddr, vnp_OrderInfo
    ])

    secure_hash = hmac.new(secret_key.encode(), hash_data.encode(), hashlib.sha512).hexdigest()

    data = {
        "vnp_RequestId": vnp_RequestId,
        "vnp_TmnCode": vnp_TmnCode,
        "vnp_Command": vnp_Command,
        "vnp_TxnRef": vnp_TxnRef,
        "vnp_OrderInfo": vnp_OrderInfo,
        "vnp_TransactionDate": vnp_TransactionDate,
        "vnp_CreateDate": vnp_CreateDate,
        "vnp_IpAddr": vnp_IpAddr,
        "vnp_Version": vnp_Version,
        "vnp_SecureHash": secure_hash
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_json = json.loads(response.text)
    else:
        response_json = {"error": f"Request failed with status code: {response.status_code}"}

    return render(request, "payment/query.html", {"title": "Kiểm tra kết quả giao dịch", "response_json": response_json})

def refund(request):
    if request.method == 'GET':
        return render(request, "payment/refund.html", {"title": "Hoàn tiền giao dịch"})

    url = settings.VNPAY_API_URL
    secret_key = settings.VNPAY_HASH_SECRET_KEY
    vnp_TmnCode = settings.VNPAY_TMN_CODE
    vnp_RequestId = n_str
    vnp_Version = '2.1.0'
    vnp_Command = 'refund'
    vnp_TransactionType = request.POST['TransactionType']
    vnp_TxnRef = request.POST['order_id']
    vnp_Amount = request.POST['amount']
    vnp_OrderInfo = request.POST['order_desc']
    vnp_TransactionNo = '0'
    vnp_TransactionDate = request.POST['trans_date']
    vnp_CreateDate = datetime.now().strftime('%Y%m%d%H%M%S')
    vnp_CreateBy = 'user01'
    vnp_IpAddr = get_client_ip(request)

    hash_data = "|".join([
        vnp_RequestId, vnp_Version, vnp_Command, vnp_TmnCode, vnp_TransactionType, vnp_TxnRef,
        vnp_Amount, vnp_TransactionNo, vnp_TransactionDate, vnp_CreateBy, vnp_CreateDate,
        vnp_IpAddr, vnp_OrderInfo
    ])

    secure_hash = hmac.new(secret_key.encode(), hash_data.encode(), hashlib.sha512).hexdigest()

    data = {
        "vnp_RequestId": vnp_RequestId,
        "vnp_TmnCode": vnp_TmnCode,
        "vnp_Command": vnp_Command,
        "vnp_TxnRef": vnp_TxnRef,
        "vnp_Amount": vnp_Amount,
        "vnp_OrderInfo": vnp_OrderInfo,
        "vnp_TransactionDate": vnp_TransactionDate,
        "vnp_CreateDate": vnp_CreateDate,
        "vnp_IpAddr": vnp_IpAddr,
        "vnp_TransactionType": vnp_TransactionType,
        "vnp_TransactionNo": vnp_TransactionNo,
        "vnp_CreateBy": vnp_CreateBy,
        "vnp_Version": vnp_Version,
        "vnp_SecureHash": secure_hash
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_json = json.loads(response.text)
    else:
        response_json = {"error": f"Request failed with status code: {response.status_code}"}

    return render(request, "payment/refund.html", {"title": "Kết quả hoàn tiền giao dịch", "response_json": response_json})

