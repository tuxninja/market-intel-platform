# Market Intelligence Platform - Frontend

Modern Next.js 14 frontend for the Market Intelligence Platform with dark Robinhood-style aesthetic.

## Features

- ✅ **Next.js 14** with App Router
- ✅ **TypeScript** for type safety
- ✅ **Tailwind CSS** for styling
- ✅ **Dark Theme** with lime green accents (#00ff88)
- ✅ **JWT Authentication** with auto-refresh
- ✅ **Protected Routes** with middleware
- ✅ **Responsive Design** - mobile-first approach
- ✅ **Real-time Digest** with filtering and sorting
- ✅ **Signal Cards** with expandable details
- ✅ **Professional UI Components**

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Backend API running at `http://localhost:8000`

### Installation

1. Clone the repository and navigate to frontend:

```bash
cd /path/to/market-intel-platform/frontend
```

2. Install dependencies:

```bash
npm install
```

3. Create environment file:

```bash
cp .env.local.example .env.local
```

4. Edit `.env.local` with your settings:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NODE_ENV=development
```

### Running the Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
frontend/
├── app/                      # Next.js 14 App Router
│   ├── (auth)/              # Auth pages group
│   │   ├── login/           # Login page
│   │   └── register/        # Register page
│   ├── dashboard/           # Dashboard page
│   ├── digest/              # Digest feed page
│   ├── settings/            # Settings page
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Landing page
│   └── globals.css          # Global styles
├── components/              # React components
│   ├── ui/                  # Base UI components
│   │   ├── Button.tsx       # Button component
│   │   ├── Card.tsx         # Card container
│   │   ├── Input.tsx        # Input field
│   │   └── Badge.tsx        # Badge label
│   ├── auth/                # Auth components
│   │   ├── LoginForm.tsx    # Login form
│   │   └── RegisterForm.tsx # Register form
│   ├── digest/              # Digest components
│   │   ├── DigestCard.tsx   # Signal card
│   │   └── DigestFilters.tsx # Filters sidebar
│   └── layout/              # Layout components
│       └── Header.tsx       # Navigation header
├── lib/                     # Utilities and config
│   ├── api.ts              # API client (axios)
│   ├── auth.ts             # Auth utilities
│   └── types.ts            # TypeScript types
├── public/                 # Static assets
├── middleware.ts           # Route protection
├── package.json            # Dependencies
├── tsconfig.json           # TypeScript config
├── tailwind.config.ts      # Tailwind config
└── next.config.js          # Next.js config
```

## API Integration

The frontend connects to the backend API at `/api/v1`:

### Authentication Endpoints

- `POST /auth/register` - Create new account
- `POST /auth/login` - Login and get JWT tokens
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user info
- `PUT /auth/me` - Update user profile

### Digest Endpoints

- `GET /digest/daily` - Get daily digest
- `POST /digest/generate` - Generate custom digest

## Authentication Flow

1. User logs in via `/login` page
2. API returns JWT access token and refresh token
3. Tokens stored in localStorage
4. Access token added to all API requests via axios interceptor
5. On 401 error, refresh token used to get new access token
6. If refresh fails, user redirected to login

## Protected Routes

Routes requiring authentication:
- `/dashboard` - User dashboard
- `/digest` - Daily intelligence feed
- `/settings` - User settings

Middleware automatically redirects unauthenticated users to `/login`.

## Available Scripts

```bash
# Development server
npm run dev

# Production build
npm run build

# Start production server
npm start

# Run linter
npm run lint
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000/api/v1` |
| `NODE_ENV` | Environment | `development` |

## Styling

### Theme Colors

- Background: `#000000`
- Card: `#0f1419`, `#1a1f29`
- Primary (lime green): `#00ff88`
- Negative (red): `#ff4444`
- Neutral: `#6b7280`

### Tailwind Classes

```tsx
// Primary button
<Button variant="primary">Click Me</Button>

// Card with hover effect
<Card hover>Content</Card>

// Badge with variant
<Badge variant="success">Active</Badge>
```

## Components

### Button

```tsx
<Button
  variant="primary" // primary | secondary | ghost
  size="md"         // sm | md | lg
  fullWidth         // boolean
  loading           // boolean
>
  Click Me
</Button>
```

### Input

```tsx
<Input
  label="Email"
  type="email"
  error="Error message"
  helperText="Helper text"
/>
```

### DigestCard

```tsx
<DigestCard item={digestItem} />
```

## Building for Production

```bash
# Build optimized production bundle
npm run build

# Start production server
npm start
```

The app will be optimized for production with:
- Minified JavaScript and CSS
- Image optimization
- Route prefetching
- Static page generation where possible

## Deployment

### Vercel (Recommended)

1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main

### Docker

```bash
# Build Docker image
docker build -t market-intel-frontend .

# Run container
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=https://api.example.com/api/v1 \
  market-intel-frontend
```

### Manual Deployment

```bash
# Build the app
npm run build

# Copy .next, public, package.json, and next.config.js to server
# Install production dependencies
npm install --production

# Start the server
npm start
```

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Troubleshooting

### API Connection Issues

If you see connection errors:
1. Verify backend is running at `http://localhost:8000`
2. Check `.env.local` has correct `NEXT_PUBLIC_API_URL`
3. Ensure CORS is configured in backend

### Authentication Issues

If authentication fails:
1. Clear browser localStorage
2. Check token expiry settings in backend
3. Verify JWT secret matches between frontend/backend

### Build Errors

If build fails:
1. Delete `.next` folder and `node_modules`
2. Run `npm install` again
3. Check Node.js version (18+ required)

## Development Tips

### Hot Reload

Next.js automatically reloads on file changes. If it stops working:
```bash
rm -rf .next
npm run dev
```

### Type Checking

```bash
npx tsc --noEmit
```

### Debugging

Use browser DevTools:
- Network tab for API requests
- Console for errors
- React DevTools extension

## Contributing

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request

## License

Proprietary - All rights reserved

## Support

For issues or questions:
- GitHub Issues: [repository]/issues
- Email: support@example.com
