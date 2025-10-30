import React from 'react';
import { Hero } from '@/components/Hero/Hero';
import { Features } from '@/components/Features/Features';
import { Pricing } from '@/components/Pricing/Pricing';
import { Testimonials } from '@/components/Testimonials/Testimonials';
import { Contact } from '@/components/Contact/Contact';
 

export default function Landing() {

  return (
    <div className="min-h-screen">
      <main className="pt-16">
        <Hero />
        <Features />
        <Pricing />
        <Testimonials />
        <Contact />
      </main>

      <footer className="bg-gray-900 text-white py-12">
        <div className="container mx-auto px-4">
          <div className="text-center">
            <div className="text-2xl font-bold mb-4">RetinaScan AI</div>
            <p className="text-gray-400 mb-8 max-w-md mx-auto">AI-powered diabetic retinopathy detection with clinical-grade insights.</p>
            <div className="flex justify-center space-x-6 mb-8">
              {['Twitter', 'GitHub', 'LinkedIn', 'Discord'].map((social) => (
                <a key={social} href="#" className="text-gray-400 hover:text-white transition-colors duration-200">{social}</a>
              ))}
            </div>
            <div className="text-gray-500 text-sm">© 2024 RetinaScan AI. All rights reserved.</div>
          </div>
        </div>
      </footer>
    </div>
  );
}


