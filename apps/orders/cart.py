class Cart:
    """
    Session-based cart helper class.
    Allows guests and logged-in customers to build orders.
    """
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, dish, quantity=1, customization=''):
        """
        Adds a dish to the session cart or increases its quantity.
        """
        dish_id = str(dish.id)
        if dish_id not in self.cart:
            self.cart[dish_id] = {
                'quantity': 0,
                'price': str(dish.price),
                'name': dish.name,
                'customization': customization,
            }
        self.cart[dish_id]['quantity'] += quantity
        self.save()
        return self.cart[dish_id]['quantity']

    def remove(self, dish):
        """
        Decrements the quantity of a dish or removes it entirely if quantity reaches 0.
        """
        dish_id = str(dish.id)
        if dish_id in self.cart:
            if self.cart[dish_id]['quantity'] > 1:
                self.cart[dish_id]['quantity'] -= 1
                qty = self.cart[dish_id]['quantity']
            else:
                del self.cart[dish_id]
                qty = 0
            self.save()
            return qty
        return 0

    def get_item_qty(self, dish_id):
        """
        Get current quantity for a specific dish ID in the cart.
        """
        dish_id = str(dish_id)
        if dish_id in self.cart:
            return self.cart[dish_id]['quantity']
        return 0

    def get_cart_count(self):
        """
        Returns total number of items in the cart.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def save(self):
        """
        Marks session as modified to ensure it is saved.
        """
        self.session.modified = True

    def get_total(self):
        """
        Calculates total monetary value of items in the cart.
        """
        return sum(
            float(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    def clear(self):
        """
        Clears the cart from the session.
        """
        if 'cart' in self.session:
            del self.session['cart']
            self.save()
