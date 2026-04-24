import { useState } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import api from '../api';

export default function ResetPasswordPage() {
    const [searchParams] = useSearchParams();
    const uid = searchParams.get('uid');
    const token = searchParams.get('token');

    const [password1, setPassword1] = useState('');
    const [password2, setPassword2] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (password1 !== password2) {
            setError('Passwords do not match');
            return;
        }

        if (password1.length < 6) {
            setError('Password must be at least 6 characters');
            return;
        }

        setLoading(true);
        setError('');

        try {
            await api.post(`/auth/password/reset/confirm/${uid}/${token}/`, {
                new_password1: password1,
                new_password2: password2,
                uid: uid,
                token: token,
            });
            setSuccess(true);
            setTimeout(() => navigate('/login'), 3000);
        } catch (err) {
            setError('Failed to reset password. The link may have expired.');
        } finally {
            setLoading(false);
        }
    };

    if (!uid || !token) {
        return (
            <div className="max-w-md mx-auto mt-20 p-6 text-center">
                <p className="text-red-500">Invalid reset link. Missing required parameters.</p>
                <Link to="/forgot-password" className="text-blue-600 mt-4 block">Request a new reset link</Link>
            </div>
        );
    }

    return (
        <div className="max-w-md mx-auto mt-20 p-6 border rounded-lg shadow">
            <h1 className="text-2xl font-bold mb-6">Reset Password</h1>

            {success ? (
                <div className="text-center">
                    <p className="text-green-600 mb-4">✅ Password reset successful!</p>
                    <p className="text-gray-600">Redirecting to login...</p>
                </div>
            ) : (
                <>
                    {error && <p className="text-red-500 mb-4">{error}</p>}
                    <form onSubmit={handleSubmit}>
                        <input
                            type="password"
                            placeholder="New password"
                            value={password1}
                            onChange={(e) => setPassword1(e.target.value)}
                            className="w-full border rounded px-3 py-2 mb-4"
                            required
                            minLength={6}
                        />
                        <input
                            type="password"
                            placeholder="Confirm new password"
                            value={password2}
                            onChange={(e) => setPassword2(e.target.value)}
                            className="w-full border rounded px-3 py-2 mb-4"
                            required
                            minLength={6}
                        />
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
                        >
                            {loading ? 'Resetting...' : 'Reset Password'}
                        </button>
                    </form>
                </>
            )}
        </div>
    );
}