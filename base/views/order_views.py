# Django Import
from django.core.exceptions import RequestDataTooBig
from django.shortcuts import render
from datetime import datetime

from rest_framework import status

# Rest Framework Import
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.serializers import Serializer


# Local Import
from base.products import products
from base.models import *
from base.serializers import ProductSerializer, OrderSerializer


# views start from here

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addOrderItems(request):
    user = request.user
    data = request.data
    print(data)
    orderItems = data['orderItems']

    if orderItems and len(orderItems) == 0:
        return Response({'detail': 'No Order Items', "status": status.HTTP_400_BAD_REQUEST})
    else:
        # (1) Create Order
        order = Order.objects.create(
            user=user,
            paymentMethod=data['paymentMethod'],
            taxPrice=data['taxPrice'],
            shippingPrice=data['shippingPrice'],
            totalPrice=data['totalPrice'],
        )

        # (2) Create Shipping Address

        shipping = ShippingAddress.objects.create(
            order=order,
            address=data['shippingAddress']['address'],
            city=data['shippingAddress']['city'],
            postalCode=data['shippingAddress']['postalCode'],
            country=data['shippingAddress']['country'],
        )

        # (3) Create order items

        for i in orderItems:
            product = Product.objects.get(_id=i['product'])

            item = OrderItem.objects.create(
                product=product,
                order=order,
                name=product.name,
                qty=i['qty'],
                price=i['price'],
                image=product.image.url,
            )

            # (4) Update Stock

            product.countInStock -= item.qty
            product.save()

        serializer = OrderSerializer(order, many=False)


        try:
            # Send confirmation email
            email = user.email
            subject = f"Order Confirmation - {user.first_name}, Order #{order.id}"
            body = f"""
Hello {user.first_name},

Thank you for placing an order with us! We're excited to let you know that your order has been successfully received.

Here are your order details:
- **Order ID**: {order.id}
- **Order Date**: {order.created_at.strftime('%B %d, %Y')}
- **Username**: {user.username}
- **Email**: {user.email}
- **Shipping Address**: {shipping.address}, {shipping.city}, {shipping.postalCode}, {shipping.country}
- **Total Amount**: ${order.totalPrice}

### Order Item:
- **Product Name**: {orderItems[0]['name']}
- **Quantity**: {orderItems[0]['qty']}
- **Price**: ${orderItems[0]['price']}
- **Total**: ${orderItems[0]['qty'] * orderItems[0]['price']}

Your order will be processed soon, and you will receive another email once it has been shipped.

If you have any questions or need assistance with your order, feel free to contact our support team. We're here to help!

Best regards,  
The Team
"""

    # Send the email
            email_response = send_email(email, subject, body)
        
        except Exception as e:
            print(f"Error sending email: {e}")
            pass

        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMyOrders(request):
    user = request.user
    orders = user.order_set.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def getOrders(request):
    orders = Order.objects.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOrderById(request, pk):

    user = request.user

    try:
        order = Order.objects.get(_id=pk)
        if user.is_staff or order.user == user:
            serializer = OrderSerializer(order, many=False)
            return Response(serializer.data)
        else:
            Response({'detail': 'Not Authorized  to view this order'},
                     status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({'detail': 'Order does not exist'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateOrderToPaid(request, pk):
    order = Order.objects.get(_id=pk)
    order.isPaid = True
    order.paidAt = datetime.now()
    order.save()
    return Response('Order was paid')


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def updateOrderToDelivered(request, pk):
    order = Order.objects.get(_id=pk)
    order.isDeliver = True
    order.deliveredAt = datetime.now()
    order.save()
    return Response('Order was Delivered')
