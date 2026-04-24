import { useState, useEffect } from 'react';
import api from '../api';

export default function OrdersPage() {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const userId = localStorage.getItem('user_id');

    useEffect(() => {
        fetchOrders();
    }, []);

    const fetchOrders = async () => {
        try {
            const res = await api.get(`/orders/my_orders/?user_id=${userId}`);
            setOrders(res.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="text-center py-10">Loading...</div>;

    return (
        <div className="max-w-3xl mx-auto p-4">
            <h1 className="text-2xl font-bold mb-6">📦 My Orders</h1>
            {orders.length === 0 ? (
                <p>No orders yet.</p>
            ) : (
                orders.map((order) => (
                    <div key={order.id} className="border rounded p-4 mb-4">
                        <div className="flex justify-between mb-2">
                            <span className="font-semibold">Order #{order.id}</span>
                            <span className={`px-2 py-1 rounded text-sm text-white ${order.payment_status === 'paid' ? 'bg-green-500' : 'bg-yellow-500'
                                }`}>
                                {order.payment_status}
                            </span>
                        </div>
                        <p className="text-sm text-gray-600">Status: {order.order_status}</p>
                        <p className="text-sm text-gray-600">Date: {new Date(order.created_at).toLocaleDateString()}</p>
                        <div className="mt-2">
                            {order.items.map((item) => (
                                <p key={item.id} className="text-sm">
                                    {item.product_name} × {item.quantity} — PKR {item.subtotal}
                                </p>
                            ))}
                        </div>
                        <p className="font-bold mt-2">Total: PKR {order.total_price}</p>
                    </div>
                ))
            )}
        </div>
    );
}