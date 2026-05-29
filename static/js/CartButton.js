const CartButton = ({ dishId, dishName }) => {
    const [quantity, setQuantity] = React.useState(0);

    // Fetch initial quantity in cart on mount
    React.useEffect(() => {
        axios.get(`/orders/cart/quantity/?dish_id=${dishId}`)
            .then(response => {
                setQuantity(response.data.item_quantity);
                updateNavbarBadge(response.data.cart_count);
            })
            .catch(error => console.error("Error fetching cart qty:", error));
    }, [dishId]);

    const updateNavbarBadge = (count) => {
        const badge = document.getElementById('cart-count');
        if (badge) badge.textContent = count;
        
        const mobBadge = document.getElementById('cart-mobile-badge');
        if (mobBadge) mobBadge.textContent = count + " items";

        const sidebarBadge = document.getElementById('cart-sidebar-count');
        if (sidebarBadge) sidebarBadge.textContent = count;
    };

    const handleAdd = () => {
        axios.post('/orders/cart/add/', { dish_id: dishId, quantity: 1 })
            .then(res => {
                if (res.data.success) {
                    setQuantity(res.data.item_quantity);
                    updateNavbarBadge(res.data.cart_count);
                    showToast(`${dishName} added to cart!`, 'success');
                    syncSidebar();
                }
            })
            .catch(err => showToast("Failed to add item to cart.", "danger"));
    };

    const handleRemove = () => {
        axios.post('/orders/cart/remove/', { dish_id: dishId })
            .then(res => {
                if (res.data.success) {
                    setQuantity(res.data.item_quantity);
                    updateNavbarBadge(res.data.cart_count);
                    showToast(`${dishName} removed from cart.`, 'warning');
                    syncSidebar();
                }
            })
            .catch(err => showToast("Failed to remove item from cart.", "danger"));
    };

    const syncSidebar = () => {
        const sidebar = document.getElementById('cart-sidebar-items');
        if (sidebar) {
            // Reload page briefly to synchronize sidebar list templates
            setTimeout(() => {
                window.location.reload();
            }, 600);
        }
    };

    if (quantity > 0) {
        return (
            <div className="d-flex align-items-center justify-content-between border border-warning rounded-pill bg-white px-2 py-1 shadow-sm" style={{ width: '90px', height: '34px' }}>
                <button className="btn btn-sm btn-link p-0 text-warning fw-bold fs-5 text-decoration-none" onClick={handleRemove}>−</button>
                <span className="fw-bold text-dark">{quantity}</span>
                <button className="btn btn-sm btn-link p-0 text-warning fw-bold fs-5 text-decoration-none" onClick={handleAdd}>+</button>
            </div>
        );
    }

    return (
        <button className="btn btn-outline-warning btn-sm rounded-pill px-3 py-1.5 fw-bold text-dark shadow-sm hover-grow" style={{ height: '34px' }} onClick={handleAdd}>
            <i className="bi bi-plus-lg me-1"></i> Add
        </button>
    );
};

// Mount all occurrences of the cart button placeholder
document.querySelectorAll('[data-cart-button]').forEach(el => {
    const dishId = el.dataset.dishId;
    const dishName = el.dataset.dishName;
    ReactDOM.createRoot(el).render(<CartButton dishId={dishId} dishName={dishName} />);
});
