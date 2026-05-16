import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api';

export default function RegisterPage() {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleRegister = async (e) => {
        e.preventDefault();
        try {
            const res = await api.post('/auth/register/', { email, name, password });
            localStorage.setItem('access_token', res.data.tokens.access);
            localStorage.setItem('refresh_token', res.data.tokens.refresh);
            localStorage.setItem('user_id', res.data.user.id);
            localStorage.setItem('user_name', res.data.user.name);
            window.dispatchEvent(new Event('auth-changed'));
            window.location.href = '/';
        } catch (err) {
            setError('Registration failed. Email may already exist.');
        }
    };

    return (
        <div className="max-w-md mx-auto mt-20 p-6 border rounded-lg shadow">
            <h1 className="text-2xl font-bold mb-6">Register</h1>
            {error && <p className="text-red-500 mb-4">{error}</p>}
            <form onSubmit={handleRegister}>
                <input
                    type="text"
                    placeholder="Full Name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full border rounded px-3 py-2 mb-4"
                    required
                />
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full border rounded px-3 py-2 mb-4"
                    required
                />
                <input
                    type="password"
                    placeholder="Password (min 6 chars)"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full border rounded px-3 py-2 mb-4"
                    required
                />
                <button
                    type="submit"
                    className="w-full bg-green-600 text-white py-2 rounded hover:bg-green-700"
                >
                    Register
                </button>
            </form>
            <p className="mt-4 text-center">
                Already have an account? <Link to="/login" className="text-blue-600">Login</Link>
            </p>
        </div>
    );
}