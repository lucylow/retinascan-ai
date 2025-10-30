import React, { useMemo, useState } from 'react';
import { InteractiveCard } from '@/components/ui/InteractiveCard';
import { AnimatedSection } from '@/components/ui/AnimatedSection';
import { Button } from '@/components/ui/button';

type Region = 'US' | 'EU' | 'AFRICA';

type Plan = {
  id: 'starter' | 'professional' | 'enterprise';
  name: string;
  basePrice: number | 'custom';
  period: 'month';
  features: string[];
  popular?: boolean;
  cta: string;
};

const BASE_PLANS: Plan[] = [
  {
    id: 'starter',
    name: 'Starter (Primary Care Clinics)',
    basePrice: 2500,
    period: 'month',
    features: [
      'Includes 200 scans/month',
      '$3/scan overage beyond 200',
      'AI report generation under 2 minutes',
      'Email support',
      'No CPT billing integration',
      'Secure cloud deployment',
    ],
    cta: 'Start 30-day Pilot',
  },
  {
    id: 'professional',
    name: 'Professional (Multi-Clinic Networks)',
    basePrice: 8000,
    period: 'month',
    features: [
      'Includes 1,000 scans/month',
      '$2/scan overage beyond 1,000',
      'CPT billing integration + 10% revenue share',
      'Outcome-based bonuses available',
      'Priority support and onboarding',
      'EHR/FHIR integrations',
    ],
    popular: true,
    cta: 'Get Started',
  },
  {
    id: 'enterprise',
    name: 'Enterprise (Large Health Systems)',
    basePrice: 'custom',
    period: 'month',
    features: [
      'Unlimited scans',
      'On‑prem or VPC deployment',
      'Dedicated support and SLA',
      'Custom AI model options',
      'Full data integration (Epic, Cerner, Athena)',
    ],
    cta: 'Contact Sales',
  },
];

export const Pricing: React.FC = () => {
  const [billingPeriod, setBillingPeriod] = useState<'month' | 'year'>('month');
  const [selectedPlan, setSelectedPlan] = useState<string>('professional');
  const [region, setRegion] = useState<Region>('US');

  const regionalMultiplier = useMemo(() => {
    if (region === 'EU') return 0.85;
    if (region === 'AFRICA') return 0.6;
    return 1;
  }, [region]);

  const plans = useMemo(() => BASE_PLANS, []);

  const formatPrice = (basePrice: number | 'custom') => {
    if (basePrice === 'custom') return 'Custom';
    const monthly = Math.round(basePrice * regionalMultiplier);
    if (billingPeriod === 'year') return `$${(monthly * 12 * 0.9).toLocaleString()}`;
    return `$${monthly.toLocaleString()}`;
  };
  const getPeriod = () => (billingPeriod === 'year' ? 'year' : 'month');

  return (
    <section id="pricing" className="py-20 bg-gray-50">
      <div className="container mx-auto px-4">
        <AnimatedSection>
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">RetinaScan AI Pricing</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">Hybrid SaaS tiers designed for clinics and health systems. Transparent, value‑aligned pricing with optional CPT integration and outcome incentives.</p>
            <div className="flex items-center justify-center gap-4 mb-12 flex-wrap">
              <span className={`font-medium ${billingPeriod === 'month' ? 'text-gray-900' : 'text-gray-500'}`}>Monthly</span>
              <button onClick={() => setBillingPeriod(prev => prev === 'month' ? 'year' : 'month')} className="relative w-14 h-7 bg-blue-600 rounded-full transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <div className={`absolute top-1 w-5 h-5 bg-white rounded-full transition-transform duration-300 ${billingPeriod === 'year' ? 'transform translate-x-7' : 'transform translate-x-1'}`} />
              </button>
              <span className={`font-medium ${billingPeriod === 'year' ? 'text-gray-900' : 'text-gray-500'}`}>Yearly</span>
              {billingPeriod === 'year' && (
                <span className="bg-green-100 text-green-800 text-sm font-medium px-3 py-1 rounded-full">Save 10%</span>
              )}
              <span className="mx-2 hidden md:inline text-gray-300">|</span>
              <div className="flex items-center gap-2">
                <span className="font-medium text-gray-700">Region:</span>
                <select
                  aria-label="Region selector"
                  value={region}
                  onChange={(e) => setRegion(e.target.value as Region)}
                  className="border rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="US">United States</option>
                  <option value="EU">Europe</option>
                  <option value="AFRICA">Africa / LMIC</option>
                </select>
              </div>
            </div>
          </div>
        </AnimatedSection>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {plans.map((plan, index) => (
            <AnimatedSection key={plan.id} delay={index * 200}>
              <InteractiveCard className={`h-full relative ${plan.popular ? 'ring-2 ring-blue-500 transform scale-105' : ''}`}>
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                    <span className="bg-blue-500 text-white px-4 py-1 rounded-full text-sm font-medium">Most Popular</span>
                  </div>
                )}

                <div className="p-8 h-full flex flex-col">
                  <div className="text-center mb-8">
                    <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                    <div className="flex items-baseline justify-center gap-1 mb-4">
                      <span className="text-4xl font-bold text-gray-900">{formatPrice(plan.basePrice)}</span>
                      <span className="text-gray-600">/{getPeriod()}</span>
                    </div>
                    {billingPeriod === 'year' && typeof plan.basePrice === 'number' && (
                      <p className="text-green-600 text-sm font-medium">Save 10% with annual billing</p>
                    )}
                  </div>

                  <ul className="space-y-4 mb-8 flex-grow">
                    {plan.features.map((feature, featureIndex) => (
                      <li key={featureIndex} className="flex items-center">
                        <svg className="w-5 h-5 text-green-500 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <span className="text-gray-600">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  <Button variant={plan.popular ? 'default' : 'secondary'} size="lg" className="w-full" onClick={() => setSelectedPlan(plan.id)}>
                    {plan.cta}
                  </Button>
                </div>
              </InteractiveCard>
            </AnimatedSection>
          ))}
        </div>

        <AnimatedSection delay={600}>
          <div className="text-center mt-12">
            <div className="max-w-4xl mx-auto space-y-3 mb-8 text-sm text-gray-600">
              <p>
                Yearly pricing reflects a 10% discount. Regional pricing adjustments applied: Europe ×0.85, Africa/LMIC ×0.60. Professional tier includes optional CPT revenue share at 10% of successful claims. Outcome bonuses configurable by contract.
              </p>
              <p>
                Data licensing for de‑identified datasets available separately ($100k–$250k per license). Contact sales for enterprise/on‑prem deployments and multi‑year agreements.
              </p>
            </div>
            <div className="flex items-center justify-center gap-3">
              <Button variant="outline" size="md">Compare all features</Button>
              <Button variant="ghost" size="md">Talk to Sales</Button>
            </div>
          </div>
        </AnimatedSection>
      </div>
    </section>
  );
};

export default Pricing;


