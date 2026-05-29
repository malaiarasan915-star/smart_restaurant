const KitchenBoard = () => {
    const [orders, setOrders] = React.useState([]);
    const [loading, setLoading] = React.useState(true);

    const fetchKitchenOrders = () => {
        axios.get('/kitchen/api/orders/')
            .then(res => {
                setOrders(res.data);
                setLoading(false);
            })
            .catch(err => console.error("Error fetching kitchen queue:", err));
    };

    React.useEffect(() => {
        fetchKitchenOrders();
        const interval = setInterval(fetchKitchenOrders, 10000);
        return () => clearInterval(interval);
    }, []);

    const updateStatus = (orderId, newStatus) => {
        axios.post(`/orders/${orderId}/update-status/`, { status: newStatus })
            .then(res => {
                if (res.data.success) {
                    showToast(`Order #${orderId} moved to ${newStatus}.`, 'info');
                    fetchKitchenOrders();
                }
            })
            .catch(err => {
                console.error(err);
                showToast("Failed to update kitchen status.", 'danger');
            });
    };

    const getElapsedTime = (isoString) => {
        const diffMs = new Date() - new Date(isoString);
        const diffMins = Math.floor(diffMs / 60000);
        if (diffMins < 1) return 'Just now';
        return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`;
    };

    if (loading) {
        return (
            <div className="text-center py-4">
                <div className="spinner-border text-warning" role="status"></div>
                <p className="text-muted mt-2 small">Loading tickets...</p>
            </div>
        );
    }

    if (orders.length === 0) {
        return (
            <div className="card border-0 p-5 text-center shadow-sm bg-white">
                <i className="bi bi-patch-check-fill text-success fs-1 mb-3"></i>
                <h4 className="fw-bold text-dark">Kitchen Queue Clear!</h4>
                <p className="text-muted">All active dishes have been cooked and ready to serve.</p>
            </div>
        );
    }

    return (
        <div className="row g-3">
            {orders.map(order => (
                <div key={order.id} className="col-md-6 col-lg-4">
                    <div className={`card card-premium h-100 border-start border-4 ${
                        order.status === 'preparing' ? 'border-danger' : 'border-primary'
                    } shadow-sm bg-white p-4`}>
                        <div className="d-flex justify-content-between align-items-start mb-3 border-bottom pb-2">
                            <div>
                                <h5 className="fw-bold mb-0 text-dark">Table {order.table_number}</h5>
                                <small className="text-muted">Order #{order.id}</small>
                            </div>
                            <span className="badge bg-dark rounded-pill">
                                {getElapsedTime(order.created_at)}
                            </span>
                        </div>

                        {/* Items list */}
                        <div className="mb-3 flex-grow-1">
                            <h6 className="fw-bold text-secondary small text-uppercase mb-2">Dishes</h6>
                            <ul className="list-unstyled mb-0">
                                {order.items.map(item => (
                                    <li key={item.id} className="py-1 border-bottom border-light">
                                        <div className="d-flex justify-content-between align-items-start">
                                            <span>
                                                <span className="badge bg-warning text-dark me-2">{item.quantity}x</span>
                                                <span className="fw-medium text-dark">{item.dish_name}</span>
                                            </span>
                                        </div>
                                        {item.customization && (
                                            <div className="small text-danger ms-4" style={{ fontSize: '12px' }}>
                                                <i className="bi bi-chat-left-text-fill text-danger me-1"></i> {item.customization}
                                            </div>
                                        )}
                                    </li>
                                ))}
                            </ul>
                        </div>

                        {/* Special Instructions */}
                        {order.special_instructions && (
                            <div className="alert alert-warning p-2.5 rounded-3 mb-3" style={{ fontSize: '13px' }}>
                                <h6 class="fw-bold text-dark mb-1 small"><i className="bi bi-exclamation-triangle"></i> Chef Notes:</h6>
                                <p className="mb-0 text-muted">{order.special_instructions}</p>
                            </div>
                        )}

                        <div className="mt-auto">
                            {order.status === 'confirmed' ? (
                                <button className="btn btn-primary w-100 py-2.5 fw-bold" onClick={() => updateStatus(order.id, 'preparing')}>
                                    <i className="bi bi-play-fill me-1"></i> Start Preparing
                                </button>
                            ) : (
                                <button className="btn btn-success w-100 py-2.5 fw-bold text-white" onClick={() => updateStatus(order.id, 'ready')}>
                                    <i className="bi bi-check-lg me-1"></i> Mark Cooked (Ready)
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );
};

// Mount
const kitchenEl = document.getElementById('kitchen-board-root');
if (kitchenEl) {
    ReactDOM.createRoot(kitchenEl).render(<KitchenBoard />);
}
