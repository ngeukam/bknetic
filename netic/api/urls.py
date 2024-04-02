from rest_framework_simplejwt.views import (
    TokenRefreshView
)
from django.urls import path
from api.views import *

urlpatterns = [
    path('token', MyObtainTokenPairView.as_view(), name='token_obtain'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('register', UserRegisterAPIView.as_view(), name='register'),
    path('logout', LogoutAPIView.as_view(), name='logout'),
    path('profile', UserProfileAPIView.as_view(), name='profile'),
    path('user-phone/<str:pk>', GetUserPhoneAPIView.as_view(), name='retrive_user_phone'),
    path('send-otp', SendOtpCodeAPIView.as_view(), name='send_otp_code'),
    #ORDER
    path('order-list/', OrderExcludeUserListAPIView.as_view(), name='order_list'),
    path('order/', OrderListAPIView.as_view(), name='create_list_order'),
    path('order/<str:pk>', OrderDetailAPIView.as_view(), name='retreive_update_delete_order'),
    #JOBS
    path('job-list/', AllJobUserListAPIView.as_view(), name='job_list'),
    path('job', JobsListAPIView.as_view(), name='create_list_job'),
    path('job/<str:pk>', JobsDetailAPIView.as_view(), name='retrieve_job'),
    path('amount', TotalAmountDetailAPIView.as_view(), name='total_paid_amount'),
    #INVOICE
    path('invoice', InvoiceAPIView.as_view(), name='create_list_invoice'),
    path('invoice-list/', AllInvoiceUserListAPIView.as_view(), name='invoice_list'),
]