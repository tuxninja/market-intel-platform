/**
 * Header Component
 */

'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import { getUser, isAuthenticated, logout } from '@/lib/auth';
import Button from '@/components/ui/Button';
import { Bars3Icon, XMarkIcon, UserCircleIcon } from '@heroicons/react/24/outline';

const Header: React.FC = () => {
  const router = useRouter();
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    setAuthenticated(isAuthenticated());
    if (isAuthenticated()) {
      setUser(getUser());
    }
  }, [pathname]);

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  return (
    <header className="bg-background border-b border-neutral/20 sticky top-0 z-50">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-primary to-primary-dark rounded-lg flex items-center justify-center">
              <span className="text-black font-bold text-lg">T</span>
            </div>
            <span className="text-white font-bold text-xl hidden sm:inline">
              TradeTheHype
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-6">
            {authenticated ? (
              <>
                <Link
                  href="/dashboard"
                  className="text-gray-300 hover:text-primary transition-colors"
                >
                  Dashboard
                </Link>
                <Link
                  href="/digest"
                  className="text-gray-300 hover:text-primary transition-colors"
                >
                  Digest
                </Link>
                <Link
                  href="/settings"
                  className="text-gray-300 hover:text-primary transition-colors"
                >
                  Settings
                </Link>

                {/* User Menu */}
                <div className="flex items-center gap-3 pl-4 border-l border-neutral/20">
                  <div className="text-right">
                    <p className="text-sm text-white font-medium">
                      {user?.full_name || user?.email || 'User'}
                    </p>
                    <p className="text-xs text-neutral capitalize">
                      {user?.subscription_tier || 'free'} tier
                    </p>
                  </div>
                  <Button variant="ghost" size="sm" onClick={handleLogout}>
                    Logout
                  </Button>
                </div>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  className="text-gray-300 hover:text-primary transition-colors"
                >
                  Sign In
                </Link>
                <Button onClick={() => router.push('/register')} size="sm">
                  Get Started
                </Button>
              </>
            )}
          </div>

          {/* Mobile menu button */}
          <button
            className="md:hidden text-white"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? (
              <XMarkIcon className="w-6 h-6" />
            ) : (
              <Bars3Icon className="w-6 h-6" />
            )}
          </button>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 space-y-3">
            {authenticated ? (
              <>
                <Link
                  href="/dashboard"
                  className="block text-gray-300 hover:text-primary transition-colors py-2"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Dashboard
                </Link>
                <Link
                  href="/digest"
                  className="block text-gray-300 hover:text-primary transition-colors py-2"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Digest
                </Link>
                <Link
                  href="/settings"
                  className="block text-gray-300 hover:text-primary transition-colors py-2"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Settings
                </Link>
                <div className="pt-3 border-t border-neutral/20">
                  <p className="text-white font-medium mb-2">
                    {user?.full_name || user?.email || 'User'}
                  </p>
                  <Button variant="ghost" size="sm" onClick={handleLogout} fullWidth>
                    Logout
                  </Button>
                </div>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  className="block text-gray-300 hover:text-primary transition-colors py-2"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Sign In
                </Link>
                <Button
                  onClick={() => {
                    router.push('/register');
                    setMobileMenuOpen(false);
                  }}
                  size="sm"
                  fullWidth
                >
                  Get Started
                </Button>
              </>
            )}
          </div>
        )}
      </nav>
    </header>
  );
};

export default Header;
