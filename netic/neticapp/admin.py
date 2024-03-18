from django.contrib import admin
from neticapp.models import *
# Register your models here.
admin.site.register(Order)
admin.site.register(User)
admin.site.register(Jobs)
admin.site.register(Invoice)
admin.site.register(Payment)