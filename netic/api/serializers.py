from neticapp.models import *
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['name'] = user.name
        # ...
        return token

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=False,
            write_only=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
    phone_number = serializers.CharField(
            required=True,
            write_only=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('phone_number', 'password', 'name', 'email')
        
    def validate(self, attrs):
        if User.objects.filter(phone_number=attrs['phone_number']).exists():
            raise serializers.ValidationError(
                'User with this phone number is already exists!')
        return attrs

    @classmethod
    def create(self, validated_data):
        user = User.objects.create(
            name=validated_data['name'],
            phone_number=validated_data['phone_number'],
            # email=validated_data['email'],
            password=validated_data['password']
        )        
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model= User
        fields = ('lat', 'long')     

class UserSerializer(serializers.ModelSerializer):
    order_of_user = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = User
        fields = ('id','phone_number', 'name', 'order_of_user', 'email')
        
class JobsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jobs
        fields = '__all__'  
    
class OrderSerializer(serializers.ModelSerializer):
    accepted = JobsSerializer(many=True, source='Jobs', read_only=True, required=False)
    order_user = serializers.SerializerMethodField()
    class Meta:
        model=Order
        fields="__all__"
    @classmethod
    def get_order_user(self, obj):
        if obj.order_user is not None:
            return UserSerializer(obj.order_user).data
        
class OrderJobsDysplaySerializer(serializers.ModelSerializer):
    order = OrderSerializer()
    class Meta:
        model = Jobs
        fields = ('job_status', 'order')

class OrderDisplaySerializer(serializers.ModelSerializer):
    accepted = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = '__all__'

    def get_accepted(self, order_instance):
        query_datas = Jobs.objects.filter(order=order_instance)
        return [JobsSerializer(order).data for order in query_datas]

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('pay_amount', 'remaining_amount', 'status', 'created_at')

class InvoiceSerializer(serializers.ModelSerializer):
    payment_info = PaymentSerializer(many=True, read_only=True)
    class Meta:
        model = Invoice
        fields = ('payment_info', 'amount', 'created_at')



# class ChangeEmailSerializer(serializers.Serializer):
#     email = serializers.EmailField(label='New E-mail',
#                                    write_only=True,
#                                    validators=[UniqueValidator(
#                                        queryset=User.objects.all())],
#                                    required=True)

#     def validate(self, attrs):
#         email = attrs['email']
#         if User.objects.filter(email=email).exists():
#             raise serializers.ValidationError(
#                 'User with this email is already exists')
#         return attrs

class ChangePhoneSerializer(serializers.Serializer):
    phone_number = serializers.CharField(label='New Phone Number',
                                   write_only=True,
                                   validators=[UniqueValidator(
                                       queryset=User.objects.all())],
                                   required=True)

    def validate(self, attrs):
        phone_number = attrs['phone_number']
        if User.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError(
                'User with this phone number is already exists')
        return attrs

class SendPasswordResetMailSerializer(serializers.Serializer):
    phone_number = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        phone_number = attrs['phone_number']
        try:
            User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'No such user with this phone_number address!')
        return attrs

class PasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True,
                                     required=True,
                                     validators=[validate_password])
    password1 = serializers.CharField(write_only=True,
                                      required=True,
                                      validators=[validate_password])

    def validate(self, attrs):
        password = attrs['password']
        password1 = attrs['password1']
        phone_number = self.context.get('phone_number')

        if password1 != password:
            raise serializers.ValidationError('Password mismatch')

        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'No such user with this phone number')
        if user.check_password(password):
            raise serializers.ValidationError(
                'New password must not be the same as the old one')
        user.set_password(password)
        user.save()
        return attrs