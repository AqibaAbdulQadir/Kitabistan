import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api';

export default function LoginPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        // Load Google script dynamically
        const script = document.createElement('script');
        script.src = 'https://accounts.google.com/gsi/client';
        script.async = true;
        script.defer = true;
        script.onload = () => {
            if (window.google) {
                window.google.accounts.id.initialize({
                    client_id: '61036126676-uvpngf6j4i1s3nnqhbmqb7e607slc7c5.apps.googleusercontent.com', // ← Replace this
                    callback: handleGoogleResponse,
                });
                window.google.accounts.id.renderButton(
                    document.getElementById('googleSignInDiv'),
                    { theme: 'outline', size: 'large', width: '100%' }
                );
            }
        };
        document.body.appendChild(script);
    }, []);

    const handleGoogleResponse = async (response) => {
        try {
            const res = await api.post('/auth/google/', {
                access_token: response.credential,
            });
            localStorage.setItem('access_token', res.data.access);
            localStorage.setItem('refresh_token', res.data.refresh);
            localStorage.setItem('user_id', res.data.user?.id);
            localStorage.setItem('user_name', res.data.user?.email);
            navigate('/');
        } catch (err) {
            // setError('Google login failed. Check backend configuration.');
            setError(JSON.stringify(err.response.data));
        }
    };

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const res = await api.post('/auth/login/', { email, password });
            localStorage.setItem('access_token', res.data.tokens.access);
            localStorage.setItem('refresh_token', res.data.tokens.refresh);
            localStorage.setItem('user_id', res.data.user.id);
            localStorage.setItem('user_name', res.data.user.name);
            navigate('/');
        } catch (err) {
            setError('Invalid email or password');
        }
    };

    return (
        <div className="max-w-md mx-auto mt-20 p-6 border rounded-lg shadow">
            <h1 className="text-2xl font-bold mb-6">Login</h1>
            {error && <p className="text-red-500 mb-4">{error}</p>}
            <form onSubmit={handleLogin}>
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
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full border rounded px-3 py-2 mb-4"
                    required
                />
                <button
                    type="submit"
                    className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
                >
                    Login
                </button>
            </form>

            <div className="relative my-4">
                <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-gray-300"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                    <span className="px-2 bg-white text-gray-500">Or continue with</span>
                </div>
            </div>

            <div id="googleSignInDiv" className="flex justify-center"></div>

            <p className="mt-4 text-center">
                <Link to="/forgot-password" className="text-blue-600">Forgot Password?</Link>
            </p>
            <p className="mt-4 text-center">
                Don't have an account? <Link to="/register" className="text-blue-600">Register</Link>
            </p>
        </div>
    );
}