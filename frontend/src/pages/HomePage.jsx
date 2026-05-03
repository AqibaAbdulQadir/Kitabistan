import { useState, useEffect } from 'react';
import api from '../api';
import { Link } from 'react-router-dom';

export default function HomePage() {
    const [books, setBooks] = useState([]);
    const [categories, setCategories] = useState([]);
    const [search, setSearch] = useState('');
    const [category, setCategory] = useState('');
    const [loading, setLoading] = useState(true);

    // 🔥 ONLY RUN ONCE (NO FILTER DEPENDENCY)
    useEffect(() => {
        fetchBooks();
        fetchCategories();
    }, []);

    // 🔥 SIMPLE + RELIABLE FETCH (NO PAGINATION LOOP)
   const fetchBooks = async () => {
    try {
        const res = await api.get('/books/'); // ✅ correct

        console.log("TOTAL BOOKS:", res.data.length);

        setBooks(res.data); // ✅ direct array

    } catch (err) {
        console.error(err);
    } finally {
        setLoading(false);
    }
};

    const fetchCategories = async () => {
        try {
            const res = await api.get('/categories/');
            setCategories(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    const addToCart = async (book) => {
        try {
            const userId = localStorage.getItem('user_id');

            if (!userId) {
                alert('Please login first');
                return;
            }

            await api.post('/cart/add/', {
                user_id: parseInt(userId),
                product_id: book.id,
                product_name: book.title,
                product_price: parseFloat(book.price),
                quantity: 1,
            });

            alert(`${book.title} added to cart!`);
        } catch (err) {
            alert('Failed to add to cart');
        }
    };

    if (loading) return <div className="text-center py-10">Loading...</div>;

    return (
        <div className="max-w-6xl mx-auto p-4">

            <h1 className="text-3xl font-bold mb-6">📚 Bookstore</h1>

            {/* 🔍 UI ONLY (does NOT filter now) */}
            <div className="flex gap-4 mb-6 flex-wrap">
                <input
                    type="text"
                    placeholder="Search books..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="border rounded px-3 py-2 w-64"
                />

                <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="border rounded px-3 py-2"
                >
                    <option value="">All Categories</option>
                    {categories.map((cat) => (
                        <option key={cat.id} value={cat.id}>
                            {cat.name}
                        </option>
                    ))}
                </select>
            </div>

            {/* 📚 Book Count */}
            <p className="mb-4 text-gray-600">
                Showing {books.length} books
            </p>

            {/* 📚 Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {books.map((book) => (
                    <div
                        key={book.id}
                        className="border rounded-lg p-4 shadow hover:shadow-lg transition"
                    >
                        {/* 📸 Image */}
                        <img
                            src={book.image_url || "https://via.placeholder.com/150"}
                            alt={book.title}
                            className="h-48 w-full object-cover mb-3 rounded"
                            onError={(e) => {
                                e.target.src = "https://via.placeholder.com/150";
                            }}
                        />

                        {/* 📖 Info */}
                        <h2 className="text-xl font-semibold">{book.title}</h2>
                        <p className="text-gray-600">by {book.author}</p>

                        {/* 📝 Description */}
                        <p className="text-sm text-gray-500 line-clamp-2 mt-1">
                            {book.description}
                        </p>

                        {/* 💰 Price */}
                        <p className="text-lg font-bold mt-2">
                            PKR {book.price}
                        </p>

                        {/* 📦 Stock */}
                        <p
                            className={`text-sm ${
                                book.in_stock ? 'text-green-600' : 'text-red-600'
                            }`}
                        >
                            {book.in_stock
                                ? `${book.stock} in stock`
                                : 'Out of stock'}
                        </p>

                        {/* 🏷 Category */}
                        <p className="text-sm text-gray-500">
                            {book.category_name}
                        </p>

                        {/* 🛒 Button */}
                        <button
                            onClick={() => addToCart(book)}
                            disabled={!book.in_stock}
                            className="mt-3 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:bg-gray-400 w-full"
                        >
                            Add to Cart
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
}