import json
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from apps.menu.models import Dish
from apps.accounts.decorators import role_required
from .models import Order, OrderItem, Review
from .cart import Cart
from apps.notifications.utils import notify_order_update

class CartView(View):
    """
    Renders the checkout cart page.
    """
    def get(self, request):
        cart = Cart(request)
        # Parse cart items with Dish objects
        cart_items = []
        for dish_id, item in cart.cart.items():
            try:
                dish = Dish.objects.get(id=int(dish_id))
                cart_items.append({
                    'dish': dish,
                    'quantity': item['quantity'],
                    'price': item['price'],
                    'customization': item['customization']
                })
            except Dish.DoesNotExist:
                pass
        
        context = {
            'cart_items': cart_items,
            'total_amount': cart.get_total(),
            'current_table': request.session.get('table_number')
        }
        return render(request, 'orders/cart.html', context)

class CartAddView(View):
    """
    AJAX view to add items to the session cart.
    """
    def post(self, request):
        try:
            data = json.loads(request.body)
            dish_id = data.get('dish_id')
            quantity = int(data.get('quantity', 1))
            customization = data.get('customization', '')
            
            dish = get_object_or_404(Dish, id=dish_id)
            cart = Cart(request)
            qty = cart.add(dish=dish, quantity=quantity, customization=customization)
            
            return JsonResponse({
                'success': True,
                'item_quantity': qty,
                'cart_count': cart.get_cart_count()
            })
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

class CartRemoveView(View):
    """
    AJAX view to decrement/remove items from the session cart.
    """
    def post(self, request):
        try:
            data = json.loads(request.body)
            dish_id = data.get('dish_id')
            
            dish = get_object_or_404(Dish, id=dish_id)
            cart = Cart(request)
            qty = cart.remove(dish=dish)
            
            return JsonResponse({
                'success': True,
                'item_quantity': qty,
                'cart_count': cart.get_cart_count()
            })
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

class CartQtyView(View):
    """
    AJAX view to retrieve cart quantities.
    """
    def get(self, request):
        dish_id = request.GET.get('dish_id')
        cart = Cart(request)
        qty = cart.get_item_qty(dish_id) if dish_id else 0
        return JsonResponse({
            'item_quantity': qty,
            'cart_count': cart.get_cart_count()
        })

class PlaceOrderView(View):
    """
    Handles placing an order. Transfers session cart to database.
    """
    def post(self, request):
        cart = Cart(request)
        if not cart.cart:
            messages.error(request, "Your cart is empty.")
            return redirect('menu:list')

        # Extract post data
        table_number = request.POST.get('table_number')
        customer_name = request.POST.get('customer_name', '')
        special_instructions = request.POST.get('special_instructions', '')
        payment_method = request.POST.get('payment_method', 'cash')

        # Fallback to session table if not explicitly submitted
        if not table_number:
            table_number = request.session.get('table_number')
        
        if not table_number:
            messages.error(request, "Please specify your Table Number to order.")
            return redirect('orders:cart')

        try:
            table_number = int(table_number)
            request.session['table_number'] = table_number
        except ValueError:
            messages.error(request, "Invalid Table Number.")
            return redirect('orders:cart')

        # Determine user/guest association
        customer = request.user if request.user.is_authenticated else None
        if not customer and not customer_name:
            customer_name = "Guest Table " + str(table_number)

        # Create Order
        order = Order.objects.create(
            customer=customer,
            customer_name=customer_name if not customer else customer.username,
            table_number=table_number,
            status='pending',
            payment_status='unpaid',
            payment_method=payment_method,
            total_amount=cart.get_total(),
            special_instructions=special_instructions
        )

        # Create OrderItems
        for dish_id, item in cart.cart.items():
            dish = get_object_or_404(Dish, id=int(dish_id))
            OrderItem.objects.create(
                order=order,
                dish=dish,
                quantity=item['quantity'],
                unit_price=dish.price,
                customization=item['customization']
            )

        # Track guest orders in session
        placed_orders = request.session.get('placed_orders', [])
        placed_orders.append(order.id)
        request.session['placed_orders'] = placed_orders

        # Clear cart
        cart.clear()

        # Trigger real-time alert to kitchen & admin
        notify_order_update(order.id, 'pending', f"New Order #{order.id} placed for Table {table_number}!")

        # Redirect based on payment method
        if payment_method in ['card', 'upi']:
            # Redirect to payment page
            return redirect('payments:checkout', order_id=order.id)
        else:
            # Cash on delivery / Pay at Counter
            messages.success(request, f"Order #{order.id} placed successfully! Please pay at the counter.")
            return redirect('orders:tracking', order_id=order.id)

class OrderTrackingView(View):
    """
    Renders active status-tracking timeline.
    """
    def get(self, request, order_id):
        order = get_object_or_404(Order.objects.prefetch_related('items__dish'), id=order_id)
        
        # Calculate overall preparation time
        total_prep_time = sum(item.dish.estimated_time for item in order.items.all())
        
        context = {
            'order': order,
            'estimated_time': total_prep_time
        }
        return render(request, 'orders/tracking.html', context)

class OrderStatusView(View):
    """
    AJAX view returning raw JSON status for tracking page fallback.
    """
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        return JsonResponse({
            'id': order.id,
            'status': order.status,
            'payment_status': order.payment_status,
            'total_amount': float(order.total_amount)
        })

class OrderHistoryView(View):
    """
    Renders previous orders for customer or session guests.
    """
    def get(self, request):
        if request.user.is_authenticated:
            # Filter user orders
            orders = Order.objects.filter(customer=request.user).prefetch_related('items__dish').order_by('-created_at')
        else:
            # Filter guest orders stored in session
            placed_ids = request.session.get('placed_orders', [])
            orders = Order.objects.filter(id__in=placed_ids).prefetch_related('items__dish').order_by('-created_at')

        return render(request, 'orders/history.html', {'orders': orders})

class ReviewView(View):
    """
    Submits rating feedback.
    """
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        rating = request.POST.get('rating')
        feedback = request.POST.get('feedback', '')

        if not rating:
            messages.error(request, "Please select a rating.")
            return redirect('orders:tracking', order_id=order.id)

        try:
            rating = int(rating)
            # Create or update review
            Review.objects.update_or_create(
                order=order,
                defaults={'rating': rating, 'feedback': feedback}
            )
            messages.success(request, "Thank you for your feedback!")
        except ValueError:
            messages.error(request, "Invalid rating submitted.")

        return redirect('orders:tracking', order_id=order.id)

class UpdateOrderStatusView(LoginRequiredMixin, View):
    """
    AJAX view to update order status. Restricted to admin, chef, and waiters.
    """
    def post(self, request, order_id):
        if request.user.role not in ['admin', 'chef', 'waiter']:
            return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

        try:
            data = json.loads(request.body)
            new_status = data.get('status')
            
            # Validate status
            valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
            if new_status not in valid_statuses:
                return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)

            order = get_object_or_404(Order, id=order_id)
            order.status = new_status
            order.save()

            # Trigger real-time notifications
            status_msgs = {
                'confirmed': f"Order #{order.id} has been confirmed.",
                'preparing': f"Order #{order.id} is cooking in the kitchen.",
                'ready': f"Order #{order.id} is ready for delivery!",
                'delivered': f"Order #{order.id} has been delivered. Enjoy your meal!",
                'cancelled': f"Order #{order.id} has been cancelled."
            }
            msg = status_msgs.get(new_status, f"Order #{order.id} status updated to {new_status}.")
            notify_order_update(order.id, new_status, msg)

            return JsonResponse({'success': True, 'order_id': order.id, 'status': order.status})
        except (json.JSONDecodeError, KeyError) as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
