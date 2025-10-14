/**
 * Login Page
 */

import Link from 'next/link';
import LoginForm from '@/components/auth/LoginForm';
import Card from '@/components/ui/Card';

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Welcome Back</h1>
          <p className="text-gray-300">
            Sign in to access your market intelligence digest
          </p>
        </div>

        <Card>
          <LoginForm />

          <div className="mt-6 text-center text-sm text-gray-300">
            Don't have an account?{' '}
            <Link href="/register" className="text-primary hover:text-primary-light font-medium">
              Create one
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
}
