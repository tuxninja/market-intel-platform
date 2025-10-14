/**
 * Login Form Component
 */

'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { authApi } from '@/lib/api';
import { setTokens, setUser } from '@/lib/auth';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';

interface LoginFormProps {
  onSuccess?: () => void;
}

const LoginForm: React.FC<LoginFormProps> = ({ onSuccess }) => {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Login
      const tokenResponse = await authApi.login({ email, password });
      setTokens(tokenResponse.access_token, tokenResponse.refresh_token);

      // Get user info
      const user = await authApi.getCurrentUser();
      setUser(user);

      // Call success callback or redirect
      if (onSuccess) {
        onSuccess();
      } else {
        router.push('/dashboard');
      }
    } catch (err: any) {
      console.error('Login error:', err);
      setError(err.response?.data?.detail || 'Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        type="email"
        label="Email"
        placeholder="your@email.com"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
        autoComplete="email"
      />

      <Input
        type="password"
        label="Password"
        placeholder="••••••••"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
        autoComplete="current-password"
      />

      {error && (
        <div className="p-3 bg-negative/10 border border-negative/20 rounded-lg">
          <p className="text-negative text-sm">{error}</p>
        </div>
      )}

      <Button type="submit" fullWidth loading={loading}>
        Sign In
      </Button>
    </form>
  );
};

export default LoginForm;
