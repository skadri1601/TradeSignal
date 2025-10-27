import { Link } from 'react-router-dom';
import { Home } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh]">
      <h1 className="text-6xl font-bold text-gray-900">404</h1>
      <p className="text-xl text-gray-600 mt-4">Page not found</p>
      <Link to="/" className="btn btn-primary mt-8 inline-flex items-center">
        <Home className="h-5 w-5 mr-2" />
        Back to Dashboard
      </Link>
    </div>
  );
}
