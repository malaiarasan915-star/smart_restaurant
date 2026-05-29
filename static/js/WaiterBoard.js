const WaiterBoard = () => {
    const [orders, setOrders] = React.useState([]);
    const [loading, setLoading] = React.useState(true);

    const fetchReadyOrders = () => {
        axios.get('/supplier/api/orders/')
            .then(res => {
                setOrders(res.data);
                setLoading(false);
            })
            .catch(err => console.error("Error fetching waiter orders:", err));
    };

    React.useEffect(() => {
        fetchReadyOrders();
        const interval = setInterval(fetchReadyOrders, 10000);
        return () => clearInterval(interval);
    }, []);

    const markDelivered = (orderId) => {
        axios.post(`/orders/${orderId}/update-status/`, { status: 'delivered' })
            .then(res => {
                if (res.data.success) {
                    showToast(`Order #${orderId} delivered!`, 'success');
                    fetchReadyOrders();
                }
            })
            .catch(err => {
                console.error(err);
                showToast("Failed to complete delivery.", 'danger');
            });
    };

    if (loading) {
        return (
            <div className="text-center py-4">
                <div className="spinner-border text-warning" role="status"></div>
                <p className="text-muted mt-2 small">Loading ready orders...</p>
            </div>
        );
    }

    if (orders.length === 0) {
        return (
            <div className="card border-0 p-5 text-center shadow-sm bg-white">
                <i className="bi bi-patch-check-fill text-success fs-1 mb-3"></i>
                <h4 className="fw-bold text-dark">No Delivery Backlog!</h4>
                <p className="text-muted">All cooked dishes are delivered to tables.</p>
            </div>
        );
    }

    return (
        <div className="row g-3">
            {orders.map(order => (
                <div key={order.id} className="col-md-6 col-lg-4">
                    <div className="card card-premium h-100 border-start border-4 border-success shadow-sm bg-white p-4">
                        <div className="d-flex justify-content-between align-items-start mb-3 border-bottom pb-2">
                            <div>
                                <h5 className="fw-bold mb-0 text-dark">Table {order.table_number}</h5>
                                <small className="text-muted">{order.customer_name}</small>
                            </div>
                            <span className="badge bg-warning text-dark px-2.5 py-1.5 rounded-pill text-capitalize">
                                Ready to serve
                            </span>
                        </div>

                        {/* Items list */}
                        <div className="mb-3 flex-grow-1">
                            <ul className="list-unstyled mb-0">
                                {order.items.map(item => (
                                    <li key={item.id} className="py-1 d-flex justify-content-between align-items-center border-bottom border-light">
                                        <span className="text-muted">
                                            <span className="fw-bold text-dark me-2">{item.quantity}x</span> 
                                            {item.dish_name}
                                        </span>
                                    </li>
                                ))}
                            </ul>
                        </div>

                        {/* Payment Status badge */}
                        <div className="mb-3 d-flex justify-content-between align-items-center">
                            <small className="text-muted">Payment status:</small>
                            <span className={`badge ${
                                order.payment_status === 'paid' ? 'bg-success' : 'bg-danger'
                            } px-3 py-1.5 rounded-pill text-capitalize`}>
                                {order.payment_status}
                            </span>
                        </div>

                        <div className="mt-auto">
                            <button className="btn btn-success text-white w-100 py-2.5 fw-bold" onClick={() => markDelivered(order.id)}>
                                <i className="bi bi-truck me-1"></i> Deliver to Table
                            </button>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );
};

// Mount
const waiterEl = document.getElementById('waiter-board-root');
if (waiterEl) {
    ReactDOM.createRoot(waiterEl).render(<WaiterBoard />);
}
