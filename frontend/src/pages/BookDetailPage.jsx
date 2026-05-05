
import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api from '../api';

export default function BookDetailPage() {
    const { id } = useParams();
    const [book, setBook] = useState(null);
    const [loading, setLoading] = useState(true);
    const [quantity, setQuantity] = useState(1);
    const navigate = useNavigate();
    const isLoggedIn = localStorage.getItem('access_token');

    useEffect(() => {
        fetchBook();
    }, [id]);

    const fetchBook = async () => {
        try {
            const res = await api.get(`/books/${id}/`);
            setBook(res.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const addToCart = async () => {
        if (!isLoggedIn) {
            navigate('/login');
            return;
        }
        try {
            await api.post('/cart/add/', {
                user_id: parseInt(localStorage.getItem('user_id')),
                product_id: book.id,
                product_name: book.title,
                product_price: parseFloat(book.price),
                quantity: quantity,
            });
            alert(`${quantity} × ${book.title} added to cart!`);
        } catch (err) {
            alert('Failed to add to cart');
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-600"></div>
            </div>
        );
    }

    if (!book) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <p>Book not found</p>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 py-8">
            <div className="max-w-6xl mx-auto px-4">
                <div className="mb-6 text-sm text-gray-500">
                    <Link to="/" className="hover:text-indigo-600">Home</Link>
                    <span className="mx-2">/</span>
                    <span>{book.category_name}</span>
                    <span className="mx-2">/</span>
                    <span className="text-gray-800">{book.title}</span>
                </div>

                <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
                    <div className="flex flex-col md:flex-row">
                        <div className="md:w-1/3 bg-gray-100 flex items-center justify-center p-8">
                            <img
                                src={book.image_url || book.image || "https://placehold.co/400x500?text=No+Cover"}
                                alt={book.title}
                                className="w-64 h-80 object-cover rounded-lg shadow-lg"
                                onError={(e) => { e.target.src = "https://placehold.co/400x500?text=No+Cover"; }}
                            />
                        </div>

                        <div className="md:w-2/3 p-8">
                            <p className="text-sm text-indigo-600 font-medium mb-2">{book.category_name}</p>
                            <h1 className="text-3xl font-bold text-gray-900 mb-2">{book.title}</h1>
                            <p className="text-lg text-gray-600 mb-4">by {book.author}</p>

                            <div className="flex items-center gap-4 mb-6">
                                <span className="text-3xl font-bold text-indigo-600">PKR {book.price}</span>
                                <span className={`px-3 py-1 rounded-full text-sm font-medium ${book.in_stock ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                                    }`}>
                                    {book.in_stock ? `${book.stock} in stock` : 'Out of stock'}
                                </span>
                            </div>

                            <div className="mb-6">
                                <h2 className="text-lg font-semibold text-gray-800 mb-2">Description</h2>
                                <p className="text-gray-600 leading-relaxed">
                                    {book.description || 'No description available for this book.'}
                                </p>
                            </div>

                            <div className="flex items-center gap-4">
                                <div className="flex items-center border rounded-lg">
                                    <button
                                        onClick={() => setQuantity(Math.max(1, quantity - 1))}
                                        className="px-4 py-2 hover:bg-gray-100 text-lg"
                                    >−</button>
                                    <span className="px-4 py-2 font-medium">{quantity}</span>
                                    <button
                                        onClick={() => setQuantity(Math.min(book.stock, quantity + 1))}
                                        className="px-4 py-2 hover:bg-gray-100 text-lg"
                                    >+</button>
                                </div>
                                <button
                                    onClick={addToCart}
                                    disabled={!book.in_stock}
                                    className="bg-indigo-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
                                >
                                    Add to Cart
                                </button>
                            </div>

                            <div className="mt-8 pt-6 border-t">
                                <div className="grid grid-cols-2 gap-4 text-sm">
                                    <div>
                                        <span className="text-gray-500">Added on:</span>
                                        <span className="ml-1 text-gray-800">
                                            {new Date(book.created_at).toLocaleDateString('en-US', {
                                                year: 'numeric', month: 'long', day: 'numeric'
                                            })}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}