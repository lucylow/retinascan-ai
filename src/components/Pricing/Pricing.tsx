import React, { useState } from 'react';
import { InteractiveCard } from '@/components/ui/InteractiveCard';
import { AnimatedSection } from '@/components/ui/AnimatedSection';
import { Button } from '@/components/ui/button';

const plans = [
  { id: 'starter', name: 'Starter', price: 19, period: 'month', features: ['Up to 5 projects','Basic analytics','Email support','1GB storage','Basic templates'], cta: 'Start Free Trial' },
  { id: 'professional', name: 'Professional', price: 49, period: 'month', features: ['Unlimited projects','Advanced analytics','Priority support','50GB storage','All templates','Custom domains','Team collaboration'], popular: true, cta: 'Get Started' },
  { id: 'enterprise', name: 'Enterprise', price: 99, period: 'month', features: ['Unlimited everything','Real-time analytics','24/7 phone support','1TB storage','Custom development','SLA guarantee','Dedicated account manager'], cta: 'Contact Sales' },
];

export const Pricing: React.FC = () => {
  const [billingPeriod, setBillingPeriod] = useState<'month' | 'year'>('month');
  const [, setSelectedPlan] = useState<string>('professional');

  const getPrice = (price: number) => billingPeriod === 'year' ? price * 10 : price;
  const getPeriod = () => (billingPeriod === 'year' ? 'year' : 'month');

  return (
    <section id="pricing" className="py-20 bg-gray-50">
      <div className="container mx-auto px-4">
        <AnimatedSection>
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">Simple, Transparent Pricing</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-8">Choose the perfect plan for your needs. No hidden fees, no surprises.</p>
            <div className="flex items-center justify-center gap-4 mb-12">
              <span className={`font-medium ${billingPeriod === 'month' ? 'text-gray-900' : 'text-gray-500'}`}>Monthly</span>
              <button onClick={() => setBillingPeriod(prev => prev === 'month' ? 'year' : 'month')} className="relative w-14 h-7 bg-blue-600 rounded-full transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <div className={`absolute top-1 w-5 h-5 bg-white rounded-full transition-transform duration-300 ${billingPeriod === 'year' ? 'transform translate-x-7' : 'transform translate-x-1'}`} />
              </button>
              <span className={`font-medium ${billingPeriod === 'year' ? 'text-gray-900' : 'text-gray-500'}`}>Yearly</span>
              {billingPeriod === 'year' && (
                <span className="bg-green-100 text-green-800 text-sm font-medium px-3 py-1 rounded-full">Save 20%</span>
              )}
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
                      <span className="text-4xl font-bold text-gray-900">${getPrice(plan.price)}</span>
                      <span className="text-gray-600">/{getPeriod()}</span>
                    </div>
                    {billingPeriod === 'year' && (
                      <p className="text-green-600 text-sm font-medium">Save ${plan.price * 2} annually</p>
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
            <p className="text-gray-600 mb-4">All plans include 14-day free trial. No credit card required.</p>
            <Button variant="outline" size="default">Compare all features</Button>
          </div>
        </AnimatedSection>
      </div>
    </section>
  );
};

export default Pricing;


