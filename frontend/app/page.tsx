/**
 * Landing Page
 */

import Link from 'next/link';
import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';

export default function HomePage() {
  const features = [
    {
      title: 'Signal Alignment Technology',
      description: 'Our proprietary algorithm aligns news sentiment, technical patterns, and market conditions to identify high-probability trading opportunities.',
      icon: '🎯',
    },
    {
      title: 'ML-Driven Intelligence',
      description: 'Machine learning models continuously learn from market patterns to enhance signal quality and filter noise.',
      icon: '🤖',
    },
    {
      title: 'Mobile-First Design',
      description: 'Access your daily digest anywhere, anytime. Beautiful, responsive interface optimized for all devices.',
      icon: '📱',
    },
    {
      title: 'Actionable Insights',
      description: 'Every signal includes WHY THIS MATTERS and HOW TO TRADE sections with entry strategy, risk management, and targets.',
      icon: '💡',
    },
  ];

  const pricing = [
    {
      tier: 'Free',
      price: '$0',
      features: [
        'Daily digest (10 signals)',
        'Basic market context',
        'Email delivery',
        'Community support',
      ],
      cta: 'Get Started',
      popular: false,
    },
    {
      tier: 'Pro',
      price: '$29',
      features: [
        'Daily digest (20 signals)',
        'ML-enhanced analysis',
        'Advanced filtering',
        'Priority support',
        'Historical signals',
      ],
      cta: 'Start Free Trial',
      popular: true,
    },
    {
      tier: 'Premium',
      price: '$79',
      features: [
        'Daily digest (50 signals)',
        'Real-time alerts',
        'Custom watchlists',
        'API access',
        'Dedicated support',
        'Strategy backtesting',
      ],
      cta: 'Start Free Trial',
      popular: false,
    },
    {
      tier: 'Elite',
      price: '$199',
      features: [
        'Unlimited signals',
        'Live trading integration',
        'Personal AI analyst',
        'Custom ML models',
        'White-glove support',
        'Private Slack channel',
      ],
      cta: 'Contact Sales',
      popular: false,
    },
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-transparent" />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 relative">
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="text-5xl sm:text-6xl font-bold text-white mb-6">
              Trade The Hype,{' '}
              <span className="text-primary">Not The News</span>
            </h1>
            <p className="text-xl text-gray-300 mb-8">
              Daily curated trading signals powered by AI. Get the WHY and HOW behind every market move.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/register">
                <Button size="lg">Get Started Free</Button>
              </Link>
              <Link href="/login">
                <Button variant="secondary" size="lg">
                  Sign In
                </Button>
              </Link>
            </div>
          </div>

          {/* Demo Screenshot Placeholder */}
          <div className="mt-16 relative">
            <div className="bg-gradient-to-br from-card to-card-secondary rounded-2xl border border-primary/20 p-8 shadow-2xl shadow-primary/10">
              <div className="space-y-4">
                <div className="h-4 bg-primary/20 rounded w-1/4"></div>
                <div className="h-8 bg-primary/10 rounded w-3/4"></div>
                <div className="h-20 bg-neutral/10 rounded"></div>
                <div className="h-20 bg-neutral/10 rounded"></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-card/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">
              Why TradeTheHype?
            </h2>
            <p className="text-xl text-gray-300">
              News-driven signals powered by FinBERT machine learning
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {features.map((feature, index) => (
              <Card key={index} hover>
                <div className="flex items-start gap-4">
                  <div className="text-4xl">{feature.icon}</div>
                  <div>
                    <h3 className="text-xl font-bold text-white mb-2">
                      {feature.title}
                    </h3>
                    <p className="text-gray-300">{feature.description}</p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">
              Choose Your Plan
            </h2>
            <p className="text-xl text-gray-300">
              Start free, upgrade as you grow
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {pricing.map((plan, index) => (
              <Card
                key={index}
                className={`relative ${
                  plan.popular ? 'border-primary ring-2 ring-primary/20' : ''
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <span className="bg-primary text-black text-xs font-bold px-3 py-1 rounded-full">
                      MOST POPULAR
                    </span>
                  </div>
                )}

                <div className="text-center mb-6">
                  <h3 className="text-2xl font-bold text-white mb-2">
                    {plan.tier}
                  </h3>
                  <div className="text-4xl font-bold text-primary mb-4">
                    {plan.price}
                    <span className="text-lg text-gray-400">/mo</span>
                  </div>
                </div>

                <ul className="space-y-3 mb-6">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-start gap-2 text-gray-300">
                      <span className="text-primary mt-1">✓</span>
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>

                <Link href="/register">
                  <Button
                    variant={plan.popular ? 'primary' : 'secondary'}
                    fullWidth
                  >
                    {plan.cta}
                  </Button>
                </Link>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-br from-primary/10 to-transparent">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold text-white mb-6">
            Ready to Level Up Your Trading?
          </h2>
          <p className="text-xl text-gray-300 mb-8">
            Join thousands of traders making smarter decisions with AI-powered intelligence.
          </p>
          <Link href="/register">
            <Button size="lg">Start Your Free Trial</Button>
          </Link>
        </div>
      </section>
    </div>
  );
}
