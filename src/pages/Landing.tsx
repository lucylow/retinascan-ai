import React, { useState, useEffect } from 'react';
import { Hero } from '../components/Hero/Hero';
import { Features } from '../components/Features/Features';
import { Pricing } from '../components/Pricing/Pricing';
import { Testimonials } from '../components/Testimonials/Testimonials';
import { Contact } from '../components/Contact/Contact';
import { useScrollAnimation } from '../hooks/useScrollAnimation';

export const Landing: React.FC = () => {
  const { scrollY, scrollDirection } = useScrollAnimation();
  const [isNavVisible, setIsNavVisible] = useState(true);

  useEffect(() => {
    if (scrollY > 100 && scrollDirection === 'down') {
      setIsNavVisible(false);
    } else {
      setIsNavVisible(true);
    }
  }, [scrollY, scrollDirection]);

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav
        className={`fixed top-0 left-0 right-0 z-50 bg-white/90 backdrop-blur-md border-b border-gray-200 transition-transform duration-300 ${
          isNavVisible ? 'transform translate-y-0' : 'transform -translate-y-full'
        }`}
      >
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center">
              <div className="text-2xl font-bold text-gray-900">Logo</div>
            </div>

            {/* Navigation Links */}
            <div className="hidden md:flex items-center space-x-8">
              {['features', 'pricing', 'testimonials', 'contact'].map((item) => (
                <button
                  key={item}
                  onClick={() => scrollToSection(item)}
                  className="text-gray-700 hover:text-blue-600 transition-colors duration-200 font-medium capitalize"
                >
                  {item}
                </button>
              ))}
            </div>

            {/* CTA Button */}
            <button
              onClick={() => scrollToSection('contact')}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors duration-200"
            >
              Get Started
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main>
        <Hero />
        <Features />
        <Pricing />
        <Testimonials />
        <Contact />
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="container mx-auto px-4">
          <div className="text-center">
            <div className="text-2xl font-bold mb-4">Logo</div>
            <p className="text-gray-400 mb-8 max-w-md mx-auto">
              Building the future of web development with cutting-edge technology and design.
            </p>
            <div className="flex justify-center space-x-6 mb-8">
              {['Twitter', 'GitHub', 'LinkedIn', 'Discord'].map((social) => (
                <a
                  key={social}
                  href="#"
                  className="text-gray-400 hover:text-white transition-colors duration-200"
                >
                  {social}
                </a>
              ))}
            </div>
            <div className="text-gray-500 text-sm">
              © 2024 Your Company. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

