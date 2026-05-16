import { useState, useEffect, useRef } from 'react';
import api from '../api';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Star, ShoppingCart, BookOpen, ChevronRight, Library } from 'lucide-react';


export default function HomePage() {
    const [books, setBooks] = useState([]);
    const [categories, setCategories] = useState([]);
    const [searchInput, setSearchInput] = useState('');
    const [search, setSearch] = useState('');
    const [category, setCategory] = useState('');
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('all');
    const [addedBooks, setAddedBooks] = useState(new Set());
    const debounceRef = useRef(null);
    const navigate = useNavigate();
    const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('access_token'));
    const [userName, setUserName] = useState(localStorage.getItem('user_name') || '');
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const pageSize = 12;

    const handleSearchChange = (e) => {
        setSearchInput(e.target.value);

        // Clear previous timeout
        if (debounceRef.current) clearTimeout(debounceRef.current);

        // Set new timeout - wait 500ms after user stops typing
        debounceRef.current = setTimeout(() => {
            setSearch(e.target.value);
        }, 1000);
    };

    useEffect(() => {
        fetchBooks();
        fetchCategories();
    }, [search, category]);

    const fetchBooks = async () => {
        setLoading(true);
        try {
            let url = `/books/?page=${page}&page_size=${pageSize}`;
            if (search) url += `&search=${search}`;
            if (category) url += `&category=${category}`;
            const res = await api.get(url);

            // DRF returns { count, next, previous, results }
            setBooks(res.data.results || res.data);
            setTotalPages(Math.ceil((res.data.count || res.data.length) / pageSize));
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        setPage(1); // Reset to page 1 when search/category changes
    }, [search, category]);

    useEffect(() => {
        fetchBooks();
    }, [page, search, category]);

    const fetchCategories = async () => {
        try {
            const res = await api.get('/categories/');
            setCategories(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    const addToCart = async (book, e) => {
        e.stopPropagation();
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
                quantity: 1,
            });
            setAddedBooks(prev => new Set([...prev, book.id]));
            setTimeout(() => {
                setAddedBooks(prev => {
                    const next = new Set(prev);
                    next.delete(book.id);
                    return next;
                });
            }, 2000);
        } catch (err) {
            alert('Failed to add to cart');
        }
    };

    const featuredBooks = books.slice(0, 6);
    const newArrivals = [...books].sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 6);
    const popularBooks = [...books].sort((a, b) => b.stock - a.stock).slice(0, 6);

    const getDisplayBooks = () => {
        switch (activeTab) {
            case 'new': return newArrivals;
            case 'popular': return popularBooks;
            default: return books;
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
                <div className="text-center">
                    <BookOpen className="w-16 h-16 text-purple-400 animate-bounce mx-auto mb-4" />
                    <p className="text-purple-200 text-lg">Loading your library...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-purple-50">
            {/* Hero Section */}
            {(
                <div className="relative overflow-hidden bg-gradient-to-br from-slate-900 via-purple-900 to-indigo-900 text-white">
                    <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PGNpcmNsZSBjeD0iMzAiIGN5PSIzMCIgcj0iMiIvPjwvZz48L2c+PC9zdmc+')] opacity-50"></div>
                    <div className="max-w-6xl mx-auto px-4 py-20 relative z-10">
                        <div className="flex flex-col md:flex-row items-center gap-12">
                            <div className="flex-1">
                                <motion.h1
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-purple-300 via-pink-300 to-orange-300 bg-clip-text text-transparent"
                                >
                                    Kitabistan
                                </motion.h1>
                                <motion.p
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.2 }}
                                    className="text-xl text-purple-200 mb-8 max-w-lg"
                                >
                                    Where every book finds its reader. Discover stories that inspire, educate, and transform.
                                </motion.p>
                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.4 }}
                                    className="flex gap-4"
                                >
                                    <button
                                        onClick={() => document.getElementById('books-section').scrollIntoView({ behavior: 'smooth' })}
                                        className="bg-white text-purple-900 px-8 py-4 rounded-2xl font-semibold hover:bg-purple-50 transition flex items-center gap-2 text-lg"
                                    >
                                        Browse Books <ChevronRight className="w-5 h-5" />
                                    </button>
                                    {!isLoggedIn && (
                                        <Link to="/register" className="border-2 border-white/30 text-white px-8 py-4 rounded-2xl font-semibold hover:bg-white/10 transition text-lg">
                                            Join Now
                                        </Link>
                                    )}
                                </motion.div>
                                {isLoggedIn && (
                                    <motion.p
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        transition={{ delay: 0.6 }}
                                        className="mt-6 text-purple-300"
                                    >
                                        Welcome back, <span className="font-semibold text-white">{userName}</span>! 👋
                                    </motion.p>
                                )}
                            </div>
                            <motion.div
                                initial={{ opacity: 0, scale: 0.8 }}
                                animate={{ opacity: 1, scale: 1 }}
                                transition={{ delay: 0.3 }}
                                className="flex-shrink-0"
                            >
                                <div className="relative">
                                    <div className="absolute -inset-4 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full blur-2xl opacity-30"></div>
                                    <div className="relative bg-white/10 backdrop-blur-sm rounded-3xl p-6 border border-white/20">
                                        <Library className="w-32 h-32 text-purple-300" />
                                    </div>
                                </div>
                            </motion.div>
                        </div>
                    </div>
                    <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-slate-50 to-transparent"></div>
                </div>
            )}

            {/* Stats Bar */}
            {(
                <div className="max-w-6xl mx-auto px-4 -mt-16 relative z-20 mb-12">
                    <div className="bg-white rounded-2xl shadow-xl p-6 grid grid-cols-3 gap-8">
                        <div className="text-center">
                            <p className="text-3xl font-bold text-purple-600">{books.length}+</p>
                            <p className="text-gray-500 text-sm">Books Available</p>
                        </div>
                        <div className="text-center border-x">
                            <p className="text-3xl font-bold text-purple-600">{categories.length}</p>
                            <p className="text-gray-500 text-sm">Categories</p>
                        </div>
                        <div className="text-center">
                            <p className="text-3xl font-bold text-purple-600">24/7</p>
                            <p className="text-gray-500 text-sm">Always Open</p>
                        </div>
                    </div>
                </div>
            )}

            {/* Main Content */}
            <div id="books-section" className="max-w-7xl mx-auto px-4 pb-20">
                {/* Search & Filter */}
                <div className="bg-white rounded-2xl shadow-lg p-6 mb-8">
                    <div className="flex flex-col md:flex-row gap-4">
                        <div className="flex-1 relative">
                            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
                            <input
                                type="text"
                                placeholder="Search by title or author..."
                                value={searchInput}
                                onChange={handleSearchChange}
                                className="w-full pl-12 pr-4 py-4 bg-gray-50 border-0 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 text-lg"
                            />
                        </div>
                        <select
                            value={category}
                            onChange={(e) => setCategory(e.target.value)}
                            className="px-6 py-4 bg-gray-50 border-0 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 text-lg min-w-[200px]"
                        >
                            <option value="">📂 All Categories</option>
                            {categories.map((cat) => (
                                <option key={cat.id} value={cat.id}>{cat.name}</option>
                            ))}
                        </select>
                    </div>

                    {/* Tabs */}
                    {!search && (
                        <div className="flex gap-2 mt-6">
                            {['all', 'new', 'popular'].map((tab) => (
                                <button
                                    key={tab}
                                    onClick={() => setActiveTab(tab)}
                                    className={`px-6 py-2 rounded-xl text-sm font-medium transition ${activeTab === tab
                                            ? 'bg-purple-600 text-white'
                                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                        }`}
                                >
                                    {tab === 'all' && '📚 All Books'}
                                    {tab === 'new' && '✨ New Arrivals'}
                                    {tab === 'popular' && '🔥 Popular'}
                                </button>
                            ))}
                        </div>
                    )}
                </div>

                {/* Book Grid */}
                <AnimatePresence mode="wait">
                    {getDisplayBooks().length === 0 ? (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="text-center py-20"
                        >
                            <BookOpen className="w-20 h-20 text-gray-300 mx-auto mb-4" />
                            <h3 className="text-xl font-semibold text-gray-500">No books found</h3>
                            <p className="text-gray-400">Try a different search term</p>
                        </motion.div>
                    ) : (
                        <motion.div
                            key={activeTab + search + category}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
                        >
                            {getDisplayBooks().map((book) => (
                                <motion.div
                                    key={book.id}
                                    whileHover={{ y: -8 }}
                                    onClick={() => navigate(`/books/${book.id}`)}
                                    className="bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all cursor-pointer overflow-hidden group"
                                >
                                    <div className="relative overflow-hidden bg-gradient-to-br from-purple-100 to-pink-100">
                                        <img
                                            src={book.image_url || book.image || "https://placehold.co/400x500?text=No+Cover"}
                                            alt={book.title}
                                            className="w-full h-64 object-cover group-hover:scale-110 transition duration-700"
                                            onError={(e) => { e.target.src = "https://placehold.co/400x500?text=No+Cover"; }}
                                        />
                                        <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent opacity-0 group-hover:opacity-100 transition flex items-end justify-center pb-4">
                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    navigate(`/books/${book.id}`);
                                                }}
                                                className="bg-white text-purple-900 px-6 py-2 rounded-full font-medium hover:bg-purple-50 transition"
                                            >
                                                View Details
                                            </button>
                                        </div>
                                        {!book.in_stock && (
                                            <div className="absolute top-3 left-3 bg-red-500 text-white text-xs px-3 py-1 rounded-full font-medium">
                                                Out of Stock
                                            </div>
                                        )}
                                        {book.stock <= 3 && book.stock > 0 && (
                                            <div className="absolute top-3 left-3 bg-orange-500 text-white text-xs px-3 py-1 rounded-full font-medium">
                                                Only {book.stock} left!
                                            </div>
                                        )}
                                    </div>
                                    <div className="p-5">
                                        <span className="text-xs font-medium text-purple-600 bg-purple-50 px-2 py-1 rounded-full">
                                            {book.category_name}
                                        </span>
                                        <h3 className="font-bold text-gray-800 mt-2 text-lg line-clamp-1 group-hover:text-purple-600 transition">
                                            {book.title}
                                        </h3>
                                        <p className="text-sm text-gray-500 mt-1">by {book.author}</p>
                                        <p className="text-sm text-gray-400 mt-1 line-clamp-2">{book.description}</p>
                                        <div className="flex items-center justify-between mt-4">
                                            <span className="text-2xl font-bold text-gray-900">PKR {book.price}</span>
                                            <div className="flex items-center gap-1">
                                                <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                                                <span className="text-sm text-gray-500">4.5</span>
                                            </div>
                                        </div>
                                        <button
                                            onClick={(e) => addToCart(book, e)}
                                            disabled={!book.in_stock}
                                            className={`mt-4 w-full py-3 rounded-xl font-semibold transition flex items-center justify-center gap-2 ${addedBooks.has(book.id)
                                                    ? 'bg-green-500 text-white'
                                                    : book.in_stock
                                                        ? 'bg-purple-600 text-white hover:bg-purple-700'
                                                        : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                                                }`}
                                        >
                                            {addedBooks.has(book.id) ? (
                                                <>✓ Added to Cart!</>
                                            ) : (
                                                <><ShoppingCart className="w-4 h-4" /> Add to Cart</>
                                            )}
                                        </button>
                                    </div>
                                </motion.div>
                            ))}
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Pagination */}
                {totalPages > 1 && (
                    <div className="flex justify-center items-center gap-4 mt-8">
                        <button
                            onClick={() => setPage(p => Math.max(1, p - 1))}
                            disabled={page === 1}
                            className="px-4 py-2 bg-white rounded-xl shadow hover:shadow-md disabled:opacity-40 disabled:cursor-not-allowed transition"
                        >
                            ← Previous
                        </button>
                        <div className="flex gap-2">
                            {Array.from({ length: totalPages }, (_, i) => i + 1).map(p => (
                                <button
                                    key={p}
                                    onClick={() => setPage(p)}
                                    className={`w-10 h-10 rounded-xl font-medium transition ${page === p
                                        ? 'bg-purple-600 text-white'
                                        : 'bg-white shadow hover:shadow-md'
                                        }`}
                                >
                                    {p}
                                </button>
                            ))}
                        </div>
                        <button
                            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                            disabled={page === totalPages}
                            className="px-4 py-2 bg-white rounded-xl shadow hover:shadow-md disabled:opacity-40 disabled:cursor-not-allowed transition"
                        >
                            Next →
                        </button>
                    </div>
                )}
            </div>


            {/* Footer */}
            <footer className="bg-slate-900 text-white py-12">
                <div className="max-w-6xl mx-auto px-4">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        <div>
                            <h3 className="text-2xl font-bold mb-4">📚 Kitabistan</h3>
                            <p className="text-gray-400">Your digital bookstore. Read, learn, grow.</p>
                        </div>
                        <div>
                            <h4 className="font-semibold mb-4">Quick Links</h4>
                            <div className="flex flex-col gap-2 text-gray-400">
                                <Link to="/" className="hover:text-white">Home</Link>
                                <Link to="/cart" className="hover:text-white">Cart</Link>
                                <Link to="/orders" className="hover:text-white">Orders</Link>
                            </div>
                        </div>
                        <div>
                            <h4 className="font-semibold mb-4">Contact</h4>
                            <p className="text-gray-400">📧 support@kitabistan.com</p>
                            <p className="text-gray-400">📞 +92 300 1234567</p>
                        </div>
                    </div>
                    <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-500">
                        <p>&copy; 2026 Kitabistan. All rights reserved.</p>
                    </div>
                </div>
            </footer>
        </div>
    );
}