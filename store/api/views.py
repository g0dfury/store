from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated
# Категории: +
class CategoryList(generics.ListCreateAPIView): # отображение + создание категории
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):    # достать, обновить или удалить категорию
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# Товары +
class ProductList(generics.ListCreateAPIView):  # отобразить и создать продукт
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductDetail(generics.RetrieveUpdateDestroyAPIView): # достать обновить удалить продукт
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductByCategoryList(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return Product.objects.filter(category_id=category_id)
    
# Поиск +
class ProductSearchView(generics.ListAPIView):   
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        query = self.request.GET.get('query', '')
        return Product.objects.filter(name__icontains=query)

# Корзина

# class CartCreate(generics.ListCreateAPIView): # создать отобразить корзмну
#     queryset = Cart.objects.all()
#     serializer_class = CartSerializer
#     permission_classes = [permissions.IsAuthenticated]
    

# class CartList(generics.CreateAPIView):
#     queryset = Cart.objects.all()
#     serializer_class = CartSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def perform_create(self, serializer):
#         user = self.request.user
#         cart_id = self.kwargs.get('cart_id', None)
        
#         if cart_id:
#             user_cart = Cart.objects.get(pk=cart_id)
#         else:
#             user_cart, created = Cart.objects.get_or_create(user=user)

#         serializer.save(cart=user_cart)

#     def create(self, request, *args, **kwargs):
#         data = request.data
#         cart_id = kwargs.get('cart_id', None)
        
#         if cart_id:
#             user_cart = Cart.objects.get(pk=cart_id)
#         else:
#             user_cart, created = Cart.objects.get_or_create(user=request.user)

#         serializer = CartItemSerializer(data=data, many=True, context={'cart': user_cart})
        
#         try:
#             serializer.is_valid(raise_exception=True)
#             serializer.save(cart=user_cart)  # Убедимся, что передаем cart в save()

#             added_items = serializer.validated_data  # Получаем данные добавленных товаров
#             items_info = [
#                 f"{item['product'].name} ({item['quantity']} units)" for item in added_items
#             ]
#             items_message = f"Item(s) added to cart successfully: {', '.join(items_info)}"

#             return Response({'success': True, 'message': items_message}, status=status.HTTP_201_CREATED)
#         except Exception as e:
#             return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

# Управление профилем пользователя(auth): 

class UserProfileView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
    
# Управление товарами (admin):
class ProductAdminListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductAdminSerializer
    permission_classes = [permissions.IsAdminUser]

class ProductAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductAdminSerializer
    permission_classes = [permissions.IsAdminUser]

# Управление аккаунтами (admin):
class UserAdminDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserAdminDeleteSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_destroy(self, instance):
        instance.delete()

# Заказы
# class OrderCreate(generics.CreateAPIView):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def perform_create(self, serializer):
#         user = self.request.user
#         cart_items = user.cart.items.all()
#         order = serializer.save(user=user, total_price=0)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)


# class OrderHistory(generics.ListAPIView):
#     serializer_class = OrderSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         return Order.objects.filter(user=user)
        
class CartView(APIView):
    permission_classes = (IsAuthenticated, )
    def get(self , request):
        user = request.user
        cart = Cart.objects.filter(user = user, ordered=False).first()
        queryset = CartItems.objects.filter(cart = cart)
        serializer = CartItemsSerializer(queryset, many = True)
        return Response(serializer.data)
    
    def post(self , request):
        data = request.data
        user = request.user
        cart,_ = Cart.objects.get_or_create(user = user, ordered = False)

        product = Product.objects.get(id = data.get('product'))
        price = product.price
        quantity = data.get('quantity')
        cart_items = CartItems(cart = cart, user = user, product = product, price = price, quantity = quantity)
        cart_items.save()

        total_price = 0
        cart_items = CartItems.objects.filter(user = user, cart = cart.id)
        for items in cart_items:
            total_price += items.price
        cart.total_price = total_price
        cart.save()

        return Response({'success': 'Items added to your cart'})    
    
    def put(self , request):
        data = request.data
        cart_item = CartItems.objects.get(id = data.get('id'))
        quantity = data.get('quantity')
        cart_item.quantity += quantity
        cart_item.save()
        return Response({'success':'Items upload'})
    
    def delete(self , request):
        user = request.user
        data = request.data

        cart_item = CartItems.objects.get(id = data.get('id'))
        cart_item.delete()

        cart = Cart.objects.filter(user = user, ordered = False).first()
        queryset = CartItems.objects.filter(cart = cart)
        serializer = CartItemsSerializer(queryset, many = True)
        return Response(serializer.data)
    


class OrderAPI(APIView):

    def get(self, request):
        queryset = Orders.objects.filter(user = request.user)
        serializer = OrderSerializer(queryset, many = True)
        return Response(serializer.data)