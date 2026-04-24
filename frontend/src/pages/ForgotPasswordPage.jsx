import { useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api';

export default function ForgotPasswordPage() {
    const [email, setEmail] = useState('');
    const [sent, setSent] = useState(false);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            await api.post('/auth/password/reset/', { email });
            setSent(true);
        } catch (err) {
            setError('Failed to send reset email. Check the email address.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-md mx-auto mt-20 p-6 border rounded-lg shadow">
            <h1 className="text-2xl font-bold mb-6">Forgot Password</h1>

            {sent ? (
                <div className="text-center">
                    <p className="text-green-600 mb-4">✅ Reset link sent!</p>
                    <p className="text-gray-600">Check your email for the password reset link.</p>
                    <p className="text-gray-500 text-sm mt-2">(For demo: the link is printed in Docker logs)</p>
                    <Link to="/login" className="text-blue-600 mt-4 block">Back to Login</Link>
                </div>
            ) : (
                <>
                    {error && <p className="text-red-500 mb-4">{error}</p>}
                    <form onSubmit={handleSubmit}>
                        <p className="text-gray-600 mb-4 text-sm">
                            Enter your email address and we'll send you a link to reset your password.
                        </p>
                        <input
                            type="email"
                            placeholder="Email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="w-full border rounded px-3 py-2 mb-4"
                            required
                        />
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
                        >
                            {loading ? 'Sending...' : 'Send Reset Link'}
                        </button>
                    </form>
                    <p className="mt-4 text-center">
                        <Link to="/login" className="text-blue-600">Back to Login</Link>
                    </p>
                </>
            )}
        </div>
    );
}