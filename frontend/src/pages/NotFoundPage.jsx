import { Link } from 'react-router-dom';

export default function NotFoundPage() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
            <div className="text-center px-4">
                <h1 className="text-9xl font-bold text-purple-400">404</h1>
                <h2 className="text-2xl font-semibold text-white mt-4">Page Not Found</h2>
                <p className="text-purple-200 mt-2 max-w-md mx-auto">
                    The page you're looking for doesn't exist or has been moved.
                </p>
                <Link
                    to="/"
                    className="inline-block mt-8 bg-purple-600 text-white px-8 py-3 rounded-xl font-semibold hover:bg-purple-700 transition"
                >
                    ← Back to Home
                </Link>
            </div>
        </div>
    );
}