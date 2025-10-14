/**
 * Register Form Component
 */

'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { authApi } from '@/lib/api';
import { setTokens, setUser } from '@/lib/auth';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';

interface RegisterFormProps {
  onSuccess?: () => void;
}

const RegisterForm: React.FC<RegisterFormProps> = ({ onSuccess }) => {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validate passwords match
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    // Validate password length
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setLoading(true);

    try {
      // Register
      await authApi.register({
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name || undefined,
      });

      // Login after registration
      const tokenResponse = await authApi.login({
        email: formData.email,
        password: formData.password,
      });
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
      console.error('Registration error:', err);
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        type="text"
        name="full_name"
        label="Full Name (Optional)"
        placeholder="John Doe"
        value={formData.full_name}
        onChange={handleChange}
        autoComplete="name"
      />

      <Input
        type="email"
        name="email"
        label="Email"
        placeholder="your@email.com"
        value={formData.email}
        onChange={handleChange}
        required
        autoComplete="email"
      />

      <Input
        type="password"
        name="password"
        label="Password"
        placeholder="••••••••"
        value={formData.password}
        onChange={handleChange}
        required
        autoComplete="new-password"
        helperText="Minimum 8 characters"
      />

      <Input
        type="password"
        name="confirmPassword"
        label="Confirm Password"
        placeholder="••••••••"
        value={formData.confirmPassword}
        onChange={handleChange}
        required
        autoComplete="new-password"
      />

      {error && (
        <div className="p-3 bg-negative/10 border border-negative/20 rounded-lg">
          <p className="text-negative text-sm">{error}</p>
        </div>
      )}

      <Button type="submit" fullWidth loading={loading}>
        Create Account
      </Button>
    </form>
  );
};

export default RegisterForm;
