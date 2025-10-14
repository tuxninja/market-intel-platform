/**
 * Register Page
 */

import Link from 'next/link';
import RegisterForm from '@/components/auth/RegisterForm';
import Card from '@/components/ui/Card';

export default function RegisterPage() {
  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Create Account</h1>
          <p className="text-gray-300">
            Start your journey to smarter trading decisions
          </p>
        </div>

        <Card>
          <RegisterForm />

          <div className="mt-6 text-center text-sm text-gray-300">
            Already have an account?{' '}
            <Link href="/login" className="text-primary hover:text-primary-light font-medium">
              Sign in
            </Link>
          </div>
        </Card>

        <p className="mt-6 text-center text-xs text-gray-400">
          By creating an account, you agree to our{' '}
          <Link href="#" className="text-primary hover:underline">
            Terms of Service
          </Link>{' '}
          and{' '}
          <Link href="#" className="text-primary hover:underline">
            Privacy Policy
          </Link>
        </p>
      </div>
    </div>
  );
}
