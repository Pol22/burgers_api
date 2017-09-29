from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from web_admin.models import Dish, Order, DishesInOrder
import json
import base64


def checked_auth(auth):
    if auth[0].lower() == 'basic':
        uname, passwd = base64.b64decode(auth[1]).decode('utf').split(':')
        user = authenticate(username=uname, password=passwd)
        if user is not None:
            if user.is_active:
                return user
    return None


def get_menu(request):
    auth = request.META['HTTP_AUTHORIZATION'].split()
    user = checked_auth(auth)
    if user is not None:
        all_dishes = Dish.objects.all()
        ret_dict = {'dishes': []}
        for item in all_dishes:
            ret_dict['dishes'].append({'id': item.id,
                                       'name': item.name,
                                       'price': item.price,
                                       'category': item.category.name,
                                       'subcategory': item.subcategory.name
                                       })
        return JsonResponse(ret_dict)
    else:
        response = HttpResponse()
        response.status_code = 401
        response['WWW-Authenticate'] = 'Basic realm="User Visible Realm"'
        return response


def create_order(request):
    auth = request.META['HTTP_AUTHORIZATION'].split()
    user = checked_auth(auth)
    if user is not None:
        try:
            json_dict = json.loads(request.body.decode('utf'))[0]
            keys = json_dict.keys()
            if 'restaurant' not in keys or 'order' not in keys:
                raise KeyError('Not restaurant or order keys')

            new_order = Order.objects.create(
                operator=user.first_name+' '+user.last_name,
                restaurant_id=json_dict['restaurant'],
                status='New'
                )

            for k, v in json_dict['order'].items():
                DishesInOrder.objects.create(
                    order=new_order,
                    dish_id=int(k),
                    number=int(v)
                )

            return JsonResponse({'order': new_order.id})
        except:
            return HttpResponse('Wrong JSON stucture')

    response = HttpResponse()
    response.status_code = 401
    response['WWW-Authenticate'] = 'Basic realm="User Visible Realm"'
    return response
