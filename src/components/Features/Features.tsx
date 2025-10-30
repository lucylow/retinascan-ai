import React, { useState } from 'react';
import { InteractiveCard } from '@/components/ui/InteractiveCard';
import { AnimatedSection } from '@/components/ui/AnimatedSection';

const features = [
  { id: '1', title: 'Lightning Fast', description: 'Blazing fast performance with optimized code and modern architecture.', icon: '⚡', color: 'from-yellow-400 to-orange-500' },
  { id: '2', title: 'Fully Responsive', description: 'Looks perfect on all devices from mobile to desktop.', icon: '📱', color: 'from-blue-400 to-cyan-500' },
  { id: '3', title: 'SEO Optimized', description: 'Built with search engine optimization best practices.', icon: '🔍', color: 'from-green-400 to-teal-500' },
  { id: '4', title: 'Secure & Safe', description: 'Enterprise-grade security to protect your data.', icon: '🛡️', color: 'from-red-400 to-pink-500' },
  { id: '5', title: 'Easy to Use', description: 'Intuitive interface that requires no technical skills.', icon: '🎯', color: 'from-purple-400 to-indigo-500' },
  { id: '6', title: '24/7 Support', description: 'Round-the-clock customer support and documentation.', icon: '💬', color: 'from-indigo-400 to-blue-500' },
];

export const Features: React.FC = () => {
  const [activeFeature, setActiveFeature] = useState<string | null>(null);

  return (
    <section id="features" className="py-20 bg-white">
      <div className="container mx-auto px-4">
        <AnimatedSection>
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">Powerful Features</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">Everything you need to build amazing websites and applications</p>
          </div>
        </AnimatedSection>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <AnimatedSection key={feature.id} delay={index * 100}>
              <InteractiveCard
                className="h-full cursor-pointer"
                onMouseEnter={() => setActiveFeature(feature.id)}
                onMouseLeave={() => setActiveFeature(null)}
              >
                <div className="p-8 h-full flex flex-col">
                  <div className={`w-16 h-16 rounded-2xl bg-gradient-to-r ${feature.color} flex items-center justify-center text-2xl mb-6 transition-transform duration-300 ${activeFeature === feature.id ? 'scale-110' : ''}`}>
                    {feature.icon}
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-4">{feature.title}</h3>
                  <p className="text-gray-600 leading-relaxed flex-grow">{feature.description}</p>
                  <div className={`mt-6 transition-all duration-300 ${activeFeature === feature.id ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-2'}`}>
                    <div className="flex items-center text-blue-600 font-medium">
                      Learn more
                      <svg className="w-4 h-4 ml-2 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                  </div>
                </div>
              </InteractiveCard>
            </AnimatedSection>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;


