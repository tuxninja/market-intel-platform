/**
 * Dashboard Page
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated, getUser } from '@/lib/auth';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import Link from 'next/link';

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    const userData = getUser();
    setUser(userData);
    setLoading(false);
  }, [router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const stats = [
    { label: 'Subscription', value: user?.subscription_tier || 'Free', color: 'primary' },
    { label: 'Status', value: user?.is_active ? 'Active' : 'Inactive', color: user?.is_active ? 'success' : 'error' },
    { label: 'Email Verified', value: user?.is_verified ? 'Yes' : 'No', color: user?.is_verified ? 'success' : 'warning' },
  ];

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Welcome back, {user?.full_name || 'Trader'}!
          </h1>
          <p className="text-gray-300">
            Here's your market intelligence overview
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {stats.map((stat, index) => (
            <Card key={index}>
              <div className="text-center">
                <p className="text-gray-400 text-sm mb-2">{stat.label}</p>
                <Badge variant={stat.color as any} size="md">
                  {stat.value}
                </Badge>
              </div>
            </Card>
          ))}
        </div>

        {/* Quick Actions */}
        <Card className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link href="/digest">
              <Button variant="primary" fullWidth>
                View Today's Digest
              </Button>
            </Link>
            <Link href="/settings">
              <Button variant="secondary" fullWidth>
                Manage Settings
              </Button>
            </Link>
            <Button variant="secondary" fullWidth disabled>
              View Performance (Coming Soon)
            </Button>
          </div>
        </Card>

        {/* Features Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <h3 className="text-xl font-bold text-white mb-3">📊 Daily Digest</h3>
            <p className="text-gray-300 mb-4">
              Get curated market intelligence with actionable trading signals delivered daily.
            </p>
            <Link href="/digest">
              <Button variant="ghost" size="sm">
                View Digest →
              </Button>
            </Link>
          </Card>

          <Card>
            <h3 className="text-xl font-bold text-white mb-3">⚙️ Customize Experience</h3>
            <p className="text-gray-300 mb-4">
              Personalize your digest settings, notification preferences, and more.
            </p>
            <Link href="/settings">
              <Button variant="ghost" size="sm">
                Go to Settings →
              </Button>
            </Link>
          </Card>

          <Card>
            <h3 className="text-xl font-bold text-white mb-3">🎯 Signal Categories</h3>
            <p className="text-gray-300 mb-4">
              Trade Alerts, Watch List, and Market Context - all organized for you.
            </p>
            <Badge variant="error">TRADE ALERT</Badge>{' '}
            <Badge variant="warning">WATCH LIST</Badge>{' '}
            <Badge variant="info">MARKET CONTEXT</Badge>
          </Card>

          <Card>
            <h3 className="text-xl font-bold text-white mb-3">📈 Upgrade Plan</h3>
            <p className="text-gray-300 mb-4">
              Unlock more signals, ML enhancements, and advanced features with Pro.
            </p>
            <Button variant="ghost" size="sm" disabled>
              View Plans (Coming Soon) →
            </Button>
          </Card>
        </div>
      </div>
    </div>
  );
}
