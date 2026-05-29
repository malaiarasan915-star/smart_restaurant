const OrderTracker = ({ orderId, initialStatus }) => {
    const [status, setStatus] = React.useState(initialStatus);
    const [messagesList, setMessagesList] = React.useState(['Order placed successfully.']);
    
    const steps = [
        { key: 'pending', label: 'Received', icon: 'bi-clipboard-check-fill' },
        { key: 'confirmed', label: 'Confirmed', icon: 'bi-hand-thumbs-up-fill' },
        { key: 'preparing', label: 'Cooking', icon: 'bi-fire' },
        { key: 'ready', label: 'Ready', icon: 'bi-bell-fill' },
        { key: 'delivered', label: 'Delivered', icon: 'bi-check-circle-fill' }
    ];

    const getStatusIndex = (currStatus) => {
        const index = steps.findIndex(s => s.key === currStatus);
        return index !== -1 ? index : 0;
    };

    const statusIndex = getStatusIndex(status);

    React.useEffect(() => {
        // Establish WebSocket Connection
        const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        const wsUrl = `${protocol}${window.location.host}/ws/orders/${orderId}/`;
        const socket = new WebSocket(wsUrl);

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.status) {
                setStatus(data.status);
                setMessagesList(prev => [...prev, data.message]);
                showToast(data.message, 'info');

                // Reload the page if order has been delivered to display the review form
                if (data.status === 'delivered') {
                    setTimeout(() => window.location.reload(), 1500);
                }
            }
        };

        socket.onclose = () => {
            console.warn("WebSocket closed. Falling back to HTTP polling...");
        };

        // Fallback HTTP Polling
        const interval = setInterval(() => {
            axios.get(`/orders/${orderId}/status/`)
                .then(res => {
                    if (res.data.status !== status) {
                        setStatus(res.data.status);
                        setMessagesList(prev => [...prev, `Order status synced to: ${res.data.status}`]);
                        if (res.data.status === 'delivered') {
                            clearInterval(interval);
                            setTimeout(() => window.location.reload(), 1500);
                        }
                    }
                })
                .catch(err => console.error("Error polling order status:", err));
        }, 5000);

        return () => {
            socket.close();
            clearInterval(interval);
        };
    }, [orderId, status]);

    return (
        <div className="card card-premium border-0 p-4 shadow-sm bg-white mb-4">
            <h4 className="font-playfair fw-bold text-center mb-4 text-dark">Track Your Order</h4>
            
            <!-- Progress Stepper Grid -->
            <div className="d-flex justify-content-between align-items-center mb-4 position-relative px-2">
                <div class="progress-bar-stepper" style={{
                    position: 'absolute',
                    top: '20px',
                    left: '5%',
                    right: '5%',
                    height: '4px',
                    backgroundColor: '#e9ecef',
                    zIndex: 1
                }}>
                    <div style={{
                        height: '100%',
                        backgroundColor: '#ffb703',
                        width: `${(statusIndex / (steps.length - 1)) * 100}%`,
                        transition: 'width 0.4s ease'
                    }}></div>
                </div>

                {steps.map((step, idx) => {
                    const isCompleted = idx <= statusIndex;
                    const isActive = idx === statusIndex;
                    return (
                        <div key={step.key} className="text-center position-relative" style={{ zIndex: 2, width: '60px' }}>
                            <div className={`mx-auto rounded-circle d-flex align-items-center justify-content-center shadow-sm ${
                                isActive ? 'bg-warning text-dark border border-warning' : isCompleted ? 'bg-dark text-warning' : 'bg-white text-muted border border-light'
                            }`} style={{ width: '40px', height: '40px', transition: 'all 0.3s' }}>
                                <i className={`bi ${step.icon}`}></i>
                            </div>
                            <small className={`d-block mt-2 fw-semibold ${isActive ? 'text-dark' : 'text-muted'}`} style={{ fontSize: '11px' }}>
                                {step.label}
                            </small>
                        </div>
                    );
                })}
            </div>

            <!-- Notification Logs Panel -->
            <div className="bg-light p-3 rounded-4 mt-2">
                <h6 className="fw-bold text-dark mb-2"><i className="bi bi-clock-history me-1 text-warning"></i> Updates Log</h6>
                <div style={{ maxHeight: '100px', overflowY: 'auto' }}>
                    {messagesList.slice().reverse().map((msg, i) => (
                        <div key={i} className="small text-muted py-1 border-bottom border-light">
                            <i className="bi bi-arrow-right-short text-warning me-1"></i> {msg}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

// Mount
const trackerEl = document.getElementById('order-tracker-root');
if (trackerEl) {
    const orderId = trackerEl.dataset.orderId;
    const initialStatus = trackerEl.dataset.status;
    ReactDOM.createRoot(trackerEl).render(<OrderTracker orderId={orderId} initialStatus={initialStatus} />);
}
