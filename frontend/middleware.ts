/**
 * Middleware for protected routes
 */

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('access_token');
  const { pathname } = request.nextUrl;

  // Check if route requires authentication
  const protectedRoutes = ['/dashboard', '/digest', '/settings'];
  const isProtectedRoute = protectedRoutes.some((route) =>
    pathname.startsWith(route)
  );

  // Redirect to login if trying to access protected route without token
  if (isProtectedRoute && !token) {
    // For client-side navigation, we'll handle this in the component
    // This middleware is mainly for direct URL access
    return NextResponse.next();
  }

  // Redirect to dashboard if already logged in and trying to access auth pages
  const authRoutes = ['/login', '/register'];
  if (authRoutes.includes(pathname) && token) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/digest/:path*', '/settings/:path*', '/login', '/register'],
};
