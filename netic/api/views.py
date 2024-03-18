from rest_framework import generics
from neticapp.models import *
from api.serializers import *
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.http import Http404
from rest_framework.views import APIView

User = get_user_model()

#JWT Login
class MyObtainTokenPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = MyTokenObtainPairSerializer
#Registration
class UserRegisterAPIView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            'status': 200,
            'data': response.data
        }, status=status.HTTP_200_OK)
#Profile
class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()

    def get_object(self):
        user = self.queryset.get(id=self.request.user.id)
        return user
#Logout
class LogoutAPIView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    def get(self,request, *args, **kwargs):
        try:
           if request._authenticate():
                request.user.auth_token.delete()
                logout(self.request)
        except User.DoesNotExist:
            return Response({'error': 'Logout error'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'success': 'You successfully logged out!'}, status=status.HTTP_200_OK)

#ORDER
class OrderListAPIView(APIView):
    """
    Create and List a order instance.
    """
    permission_classes = (IsAuthenticated,)
    def post(self, request, format=None):
        serializer = OrderDisplaySerializer(data=request.data)
        if serializer.is_valid():
            saved_obj = serializer.save()
            response_data = OrderDisplaySerializer(saved_obj).data
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #all orders except user orders
    def get(self, request, format=None):
        user = get_object_or_404(User, pk= request.user.id)
        orders = Order.objects.filter(is_active=True).exclude(order_user_id = user.id).all()
        serializer = OrderDisplaySerializer(orders, many=True)
        return Response(serializer.data)
    
class OrderDetailAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    """
    Retrieve, update or delete a order instance.
    """
    def get_object(self, pk):
        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            raise Http404
   
    def get(self, request, pk, format=None):
        order = self.get_object(pk)
        serializer = OrderDisplaySerializer(order)
        return Response(serializer.data)
    
    def put(self, request, pk, format=None):
        order = self.get_object(pk)
        serializer = OrderDisplaySerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        order = self.get_object(pk)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

#JOBS
class JobsListAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    """
    Create and List a user jobs instance.
    """
    #insert jobs in job model
    def post(self, request, format=None):
        serializer = JobsSerializer(data=request.data)
        if serializer.is_valid():
            saved_obj = serializer.save()
            change_order_active = Order.objects.filter(id=request.data['order']).update(is_active=False)
            response_data = JobsSerializer(saved_obj).data
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #all jobs done by user
    def get(self, request, format=None):
        user = get_object_or_404(User, pk= request.user.id)
        jobs = user.jobs_set.filter(job_status=True)
        serializer = OrderJobsDysplaySerializer(jobs, many=True)
        return Response(serializer.data)

class JobsDetailAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    """
    Create and List a user jobs instance.
    """
    def get_object(self, pk):
            try:
                return Order.objects.get(pk=pk)
            except Order.DoesNotExist:
                raise Http404
    def put(self, request, pk, format=None):
        order = self.get_object(pk)
        user =  get_object_or_404(User, pk= request.user.id)
        try:
            repost_change1 = user.jobs_set.filter(order=order).update(job_status=False)
            repost_change2 = user.order_set.filter(id=order.id).update(is_active=True)
        except BaseException as e:
            return Response({"error": str(e)},status=status.HTTP_400_BAD_REQUEST)
        return Response({"success":"You are successfully repost ! "}, status=status.HTTP_200_OK)

class TotalPaidAmountDetailAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None):
        user =  get_object_or_404(User, pk= request.user.id)
        try:
            all_id_done_jobs = user.jobs_set.filter(job_status=True).values_list("order")
            total_paid_amount = Order.objects.filter(id__in =all_id_done_jobs).filter(is_paid=False).aggregate(total_paid_amount=Sum('paid_amount'))
        except BaseException as e:
            return Response({"error": str(e)},status=status.HTTP_400_BAD_REQUEST)
        return Response(total_paid_amount, status=status.HTTP_200_OK)

    #update is_paid status of order to TRUE after invoice created
    def put(self, request, format=None):
        user =  get_object_or_404(User, pk= request.user.id)
        try:
            all_id_done_jobs = user.jobs_set.filter(job_status=True).values_list("order")
            update_is_paid = Order.objects.filter(id__in =all_id_done_jobs).update(is_active=False, is_paid=True)
        except BaseException as e:
            return Response({"error": str(e)},status=status.HTTP_400_BAD_REQUEST)
        return Response({"success":"You have one unpaid invoice ! "}, status=status.HTTP_200_OK)
        
#INVOICE
class InvoiceAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request, format=None):
        serializer = InvoiceSerializer(data=request.data)
        if serializer.is_valid():
            saved_obj = serializer.save()
            response_data = InvoiceSerializer(saved_obj).data
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #all invoices off user
    def get(self, request, format=None):
        user = get_object_or_404(User, pk= request.user.id)
        invoices = Invoice.objects.filter(invoice_user_id=user.id).all()
        serializer = InvoiceSerializer(invoices, many=True)
        return Response(serializer.data)


#get current user u = User.obejts.get(id='')
#all orders of current user : u.order_user.all()
#all job of current user : aj = u.jobs_set.all()
#all done job of current user : aj.filter(job_status=True)
#all job done of current user aj= u.jobs_set.filter(job_status=True)
#total paid amount of current user u.order_user.aggregate(total_paid_amount=Sum('paid_amount'))

#All Id of done jobs: all_id_job_done = u.jobs_set.filter(job_status=True).values_list("order")
#total_paid_amount of done jobs:  Order.objects.filter(id__in =all_id_job_done).aggregate(total_paid_amount=Sum('paid_amount'))