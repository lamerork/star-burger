from django.http import JsonResponse
from django.templatetags.static import static

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from phonenumbers import parse, is_valid_number

from .models import Product, Order, OrderItem


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def validate_order(new_order):
    order_keys = ['firstname', 'lastname', 'address']
    for order_key in order_keys:
        if not new_order.get(order_key):
            content = {'error': f'похоже что {order_key} отсутствует или указано не верное значение (None, Null, 0, False)'}
            return content, False
        if not isinstance(new_order[order_key], str):
            content = {'error': f'получен неподдерживаемый формат данных в параметре {order_key}'}
            return content, False

    if not new_order.get('phonenumber'):
        content = {'error': 'phonenumber отсутствует'}
        return content, False

    client_phonenumber = parse(new_order['phonenumber'], 'RU')
    if not is_valid_number(client_phonenumber):
        content = {'error': 'phonenumber не подходит под формат региона'}
        return content, False

    if not new_order.get('products'):
        content = {'error': 'похоже что список products отсутствует или оказался пустым'}
        return content, False

    ordered_products = new_order['products']
    if not isinstance(ordered_products, list):
        content = {'error': 'похоже вместо списка products получен другой формат данных'}
        return content, False

    all_ordered_products = [ordered_product['product'] for ordered_product in ordered_products]
    all_products = Product.objects.all()
    last_product_id = list(all_products)[-1].id

    for product_id in all_ordered_products:
        if not 0 < int(product_id) <= last_product_id:
            content = {'error': f'Позиции с индексом {product_id} не существует'}
            return content, False
    return {}, True


@api_view(['POST'])
def register_order(request):

    order_data = request.data

    content, validation = validate_order(order_data)
    if not validation:
        return Response(content, status=status.HTTP_404_NOT_FOUND)

    order = Order.objects.create(
        firstname=order_data['firstname'],
        lastname=order_data['lastname'],
        phone_number=order_data['phonenumber'],
        address=order_data['address']
    )

    for item in order_data['products']:

        product = Product.objects.get(id=item['product'])
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item['quantity']
        )

    return JsonResponse({})
