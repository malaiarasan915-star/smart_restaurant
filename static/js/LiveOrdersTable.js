const LiveOrdersTable = () => {
    const [orders, setOrders] = React.useState([]);
    const [loading, setLoading] = React.useState(true);

    const fetchOrders = () => {
        axios.get('/admin-dashboard/api/orders/')
            .then(res => {
                setOrders(res.data);
                setLoading(false);
            })
            .catch(err => console.error("Error fetching live orders:", err));
    };

    React.useEffect(() => {
        fetchOrders();
        const interval = setInterval(fetchOrders, 10000);
        return () => clearInterval(interval);
    }, []);

    const handleStatusChange = (orderId, newStatus) => {
        axios.post(`/orders/${orderId}/update-status/`, { status: newStatus })
            .then(res => {
                if (res.data.success) {
                    showToast(`Order #${orderId} updated to ${newStatus}.`, 'success');
                    fetchOrders();
                }
            })
            .catch(err => {
                console.error(err);
                showToast("Failed to update status. Check authorization.", 'danger');
            });
    };

    if (loading) {
        return (
            <div className="text-center py-4">
                <div className="spinner-border text-warning" role="status"></div>
                <p class="text-muted mt-2 small">Loading active orders...</p>
            </div>
        );
    }

    if (orders.length === 0) {
        return (
            <div className="text-center py-5 text-muted">
                <i className="bi bi-inbox fs-1 d-block mb-2 text-black-50"></i>
                No active orders at the moment.
            </div>
        );
    }

    const getStatusBadgeClass = (status) => {
        switch (status) {
            case 'pending': return 'bg-warning text-dark';
            case 'confirmed': return 'bg-primary text-white';
            case 'preparing': return 'bg-info text-dark';
            case 'ready': return 'bg-success text-white';
            default: return 'bg-secondary text-white';
        }
    };

    return (
        <div className="table-responsive">
            <table className="table table-hover align-middle">
                <thead class="table-light">
                    <tr>
                        <th>Order #</th>
                        <th>Table</th>
                        <th>Items Count</th>
                        <th>Total</th>
                        <th>Status</th>
                        <th>Placed Time</th>
                        <th className="text-end">Update Dispatch</th>
                    </tr>
                </thead>
                <tbody>
                    {orders.map(order => (
                        <tr key={order.id}>
                            <td className="fw-bold">#{order.id}</td>
                            <td><span className="badge bg-dark rounded-pill">Table {order.table_number}</span></td>
                            <td>{order.item_count} items</td>
                            <td className="fw-bold">₹{order.total_amount}</td>
                            <td>
                                <span className={`badge px-3 py-1.5 rounded-pill text-capitalize ${getStatusBadgeClass(order.status)}`}>
                                    {order.status}
                                </span>
                            </td>
                            <td className="text-muted small">
                                {new Date(order.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </td>
                            <td className="text-end">
                                <select 
                                    className="form-select form-select-sm d-inline-block w-auto" 
                                    value={order.status} 
                                    onChange={(e) => handleStatusChange(order.id, e.target.value)}
                                >
                                    <option value="pending">Pending</option>
                                    <option value="confirmed">Confirm Order</option>
                                    <option value="preparing">Start Prep (Kitchen)</option>
                                    <option value="ready">Ready to Serve</option>
                                    <option value="delivered">Mark Delivered</option>
                                    <option value="cancelled">Cancel Order</option>
                                </select>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

// Mount
const tableEl = document.getElementById('live-orders-root');
if (tableEl) {
    ReactDOM.createRoot(tableEl).render(<LiveOrdersTable />);
}
