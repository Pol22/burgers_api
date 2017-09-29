from django.contrib import admin
from .models import *


admin.site.register(Restaurant)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Dish)
admin.site.register(Order)
admin.site.register(DishesInOrder)