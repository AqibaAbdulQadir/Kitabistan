import { useState, useEffect } from 'react';
import api from '../api';
import { useNavigate } from 'react-router-dom';

export default function CartPage() {
    const [cart, setCart] = useState(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();
    const userId = localStorage.getItem('user_id');

    useEffect(() => {
        if (!userId) {
            navigate('/login');
            return;
        }
        fetchCart();
    }, []);

    const fetchCart = async () => {
        try {
            const res = await api.get(`/cart/my_cart/?user_id=${userId}`);
            setCart(res.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const updateQuantity = async (productId, quantity) => {
        try {
            await api.put('/cart/update_item/', {
                user_id: parseInt(userId),
                product_id: productId,
                quantity,
            });
            fetchCart();
        } catch (err) {
            alert('Failed to update');
        }
    };

    const removeItem = async (productId) => {
        try {
            await api.delete(`/cart/remove/?user_id=${userId}&product_id=${productId}`);
            fetchCart();
        } catch (err) {
            alert('Failed to remove');
        }
    };

    const checkout = async () => {
        try {
            const items = cart.items.map(item => ({
                product_id: item.product_id,
                product_name: item.product_name,
                product_price: item.product_price,
                quantity: item.quantity,
            }));

            // Step 1: Create order (stock check happens here)
            let orderRes;
            try {
                orderRes = await api.post('/orders/create_order/', {
                    user_id: parseInt(userId),
                    items,
                    shipping_address: 'Default Address',
                });
            } catch (err) {
                // Stock insufficient or other order creation error
                if (err.response && err.response.data) {
                    const errorMsg = err.response.data.error || JSON.stringify(err.response.data);
                    alert('❌ Order Failed: ' + errorMsg);
                } else {
                    alert('❌ Order failed. Please try again.');
                }
                return;
            }

            const orderId = orderRes.data.id;

            // Step 2: Process payment
            try {
                const paymentRes = await api.post('/payments/process_payment/', {
                    order_id: orderId,
                    user_id: parseInt(userId),
                    amount: parseFloat(cart.total_price),
                });

                if (paymentRes.data.status === 'completed') {
                    await api.delete(`/cart/clear/?user_id=${userId}`);
                    alert('✅ Order placed successfully!');
                    navigate('/orders');
                } else {
                    alert('❌ Payment failed. Please try again.');
                }
            } catch (err) {
                alert('❌ Payment processing failed. Your order is saved. You can retry payment from Orders page.');
                navigate('/orders');
            }
        } catch (err) {
            alert('❌ Checkout failed. Please try again.');
        }
    };

    if (loading) return <div className="text-center py-10">Loading...</div>;
    if (!cart || cart.items.length === 0) {
        return (
            <div className="max-w-2xl mx-auto p-4 text-center">
                <h1 className="text-2xl font-bold mb-4">🛒 Your Cart</h1>
                <p>Your cart is empty.</p>
            </div>
        );
    }

    return (
        <div className="max-w-2xl mx-auto p-4">
            <h1 className="text-2xl font-bold mb-6">🛒 Your Cart</h1>
            {cart.items.map((item) => (
                <div key={item.id} className="border rounded p-4 mb-3 flex justify-between items-center">
                    <div>
                        <h3 className="font-semibold">{item.product_name}</h3>
                        <p className="text-gray-600">PKR {item.product_price} × {item.quantity} = PKR {item.subtotal}</p>
                    </div>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => updateQuantity(item.product_id, item.quantity - 1)}
                            className="px-2 py-1 border rounded"
                        >-</button>
                        <span>{item.quantity}</span>
                        <button
                            onClick={() => updateQuantity(item.product_id, item.quantity + 1)}
                            className="px-2 py-1 border rounded"
                        >+</button>
                        <button
                            onClick={() => removeItem(item.product_id)}
                            className="ml-4 text-red-500"
                        >Remove</button>
                    </div>
                </div>
            ))}
            <div className="mt-6 text-right">
                <p className="text-xl font-bold">Total: PKR {cart.total_price}</p>
                <button
                    onClick={checkout}
                    className="mt-3 bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700"
                >
                    Checkout & Pay
                </button>
            </div>
        </div>
    );
}