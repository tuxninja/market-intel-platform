/**
 * Settings Page
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated, getUser, setUser } from '@/lib/auth';
import { authApi } from '@/lib/api';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Badge from '@/components/ui/Badge';

export default function SettingsPage() {
  const router = useRouter();
  const [user, setUserState] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [fullName, setFullName] = useState('');
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    const userData = getUser();
    setUserState(userData);
    setFullName(userData?.full_name || '');
    setLoading(false);
  }, [router]);

  const handleSave = async () => {
    setSaving(true);
    setError('');
    setSuccess('');

    try {
      const updatedUser = await authApi.updateProfile(fullName);
      setUser(updatedUser);
      setUserState(updatedUser);
      setSuccess('Profile updated successfully!');
    } catch (err: any) {
      console.error('Failed to update profile:', err);
      setError(err.response?.data?.detail || 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-white mb-8">Settings</h1>

        <div className="space-y-6">
          {/* Account Information */}
          <Card>
            <h2 className="text-2xl font-bold text-white mb-4">Account Information</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Email
                </label>
                <p className="text-white">{user?.email}</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Subscription Tier
                </label>
                <Badge variant="success" size="md">
                  {user?.subscription_tier || 'free'}
                </Badge>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Account Status
                </label>
                <Badge variant={user?.is_active ? 'success' : 'error'} size="md">
                  {user?.is_active ? 'Active' : 'Inactive'}
                </Badge>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Email Verification
                </label>
                <Badge variant={user?.is_verified ? 'success' : 'warning'} size="md">
                  {user?.is_verified ? 'Verified' : 'Not Verified'}
                </Badge>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Member Since
                </label>
                <p className="text-white">
                  {user?.created_at && new Date(user.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          </Card>

          {/* Profile Settings */}
          <Card>
            <h2 className="text-2xl font-bold text-white mb-4">Profile Settings</h2>

            <div className="space-y-4">
              <Input
                label="Full Name"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Enter your full name"
              />

              {success && (
                <div className="p-3 bg-primary/10 border border-primary/20 rounded-lg">
                  <p className="text-primary text-sm">{success}</p>
                </div>
              )}

              {error && (
                <div className="p-3 bg-negative/10 border border-negative/20 rounded-lg">
                  <p className="text-negative text-sm">{error}</p>
                </div>
              )}

              <Button onClick={handleSave} loading={saving}>
                Save Changes
              </Button>
            </div>
          </Card>

          {/* Digest Preferences */}
          <Card>
            <h2 className="text-2xl font-bold text-white mb-4">Digest Preferences</h2>
            <p className="text-gray-300 mb-4">
              Customize your daily digest settings (Coming soon)
            </p>

            <div className="space-y-3 opacity-50">
              <div className="flex items-center justify-between py-2">
                <span className="text-gray-300">Email notifications</span>
                <input type="checkbox" disabled className="w-5 h-5" />
              </div>
              <div className="flex items-center justify-between py-2">
                <span className="text-gray-300">ML enhancement</span>
                <input type="checkbox" disabled className="w-5 h-5" />
              </div>
              <div className="flex items-center justify-between py-2">
                <span className="text-gray-300">Real-time alerts</span>
                <input type="checkbox" disabled className="w-5 h-5" />
              </div>
            </div>
          </Card>

          {/* Subscription Management */}
          <Card>
            <h2 className="text-2xl font-bold text-white mb-4">Subscription</h2>
            <p className="text-gray-300 mb-4">
              You are currently on the <strong className="text-primary capitalize">{user?.subscription_tier || 'free'}</strong> plan
            </p>
            <Button variant="secondary" disabled>
              Upgrade Plan (Coming Soon)
            </Button>
          </Card>

          {/* Danger Zone */}
          <Card className="border-negative/20">
            <h2 className="text-2xl font-bold text-negative mb-4">Danger Zone</h2>
            <p className="text-gray-300 mb-4">
              Permanently delete your account and all associated data
            </p>
            <Button variant="secondary" className="border-negative text-negative hover:bg-negative/10" disabled>
              Delete Account (Coming Soon)
            </Button>
          </Card>
        </div>
      </div>
    </div>
  );
}
