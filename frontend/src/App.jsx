import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import CartPage from './pages/CartPage';
import OrdersPage from './pages/OrdersPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import ResetPasswordPage from './pages/ResetPasswordPage';
import BookDetailPage from './pages/BookDetailPage';
import NotFoundPage from './pages/NotFoundPage';

export default function App() {
  const PRIMARY_BACKEND = 'https://kitabistan.onrender.com/api/health/';
  const FALLBACK_BACKEND = 'https://kitabistan.up.railway.app/api/health/';

  useEffect(() => {
    // Check primary backend, fallback to Railway if Render is down
    fetch(PRIMARY_BACKEND)
      .catch(() => {
        // Primary down — switch API base URL to fallback
        localStorage.setItem('api_url', FALLBACK_BACKEND);
        window.location.reload();
      });
  }, []);

  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userName, setUserName] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const name = localStorage.getItem('user_name');
    setIsLoggedIn(!!token);
    setUserName(name || '');
  }, []);

  const handleLogout = () => {
    localStorage.clear();
    setIsLoggedIn(false);
    setUserName('');
    window.location.href = '/';
  };

  return (
    <BrowserRouter>
      <nav className="bg-gray-800 text-white p-4">
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          <Link to="/" className="text-xl font-bold">📚 Kitabistan</Link>
          <div className="flex gap-4 items-center">
            <Link to="/cart" className="hover:text-gray-300">🛒 Cart</Link>
            {isLoggedIn ? (
              <>
                <Link to="/orders" className="hover:text-gray-300">📦 Orders</Link>
                <span className="text-gray-400">Hi, {userName}</span>
                <button onClick={handleLogout} className="hover:text-gray-300">Logout</button>
              </>
            ) : (
              <>
                <Link to="/login" className="hover:text-gray-300">Login</Link>
                <Link to="/register" className="hover:text-gray-300">Register</Link>
              </>
            )}
          </div>
        </div>
      </nav>

      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/cart" element={<CartPage />} />
        <Route path="/orders" element={<OrdersPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route path="/books/:id" element={<BookDetailPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}