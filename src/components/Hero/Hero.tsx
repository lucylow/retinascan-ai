import React, { useState, useEffect } from 'react';
import { Button } from '../ui/button';
import { AnimatedSection } from '../ui/AnimatedSection';

export const Hero: React.FC = () => {
  const [currentWordIndex, setCurrentWordIndex] = useState(0);
  const [displayText, setDisplayText] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);

  const words = ['amazing', 'beautiful', 'fast', 'responsive', 'modern'];

  useEffect(() => {
    const currentWord = words[currentWordIndex];
    
    const timeout = setTimeout(() => {
      if (!isDeleting) {
        // Typing effect
        if (displayText.length < currentWord.length) {
          setDisplayText(currentWord.slice(0, displayText.length + 1));
        } else {
          // Wait before starting to delete
          setTimeout(() => setIsDeleting(true), 1500);
        }
      } else {
        // Deleting effect
        if (displayText.length > 0) {
          setDisplayText(currentWord.slice(0, displayText.length - 1));
        } else {
          setIsDeleting(false);
          setCurrentWordIndex((prev) => (prev + 1) % words.length);
        }
      }
    }, isDeleting ? 50 : 100);

    return () => clearTimeout(timeout);
  }, [displayText, isDeleting, currentWordIndex]);

  const stats = [
    { number: '10K+', label: 'Happy Customers' },
    { number: '99.9%', label: 'Uptime' },
    { number: '24/7', label: 'Support' },
  ];

  return (
    <section className="relative min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50 overflow-hidden">
      {/* Background Animation */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
        <div className="absolute top-1/3 right-1/4 w-72 h-72 bg-purple-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
        <div className="absolute bottom-1/4 left-1/2 w-72 h-72 bg-pink-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
      </div>

      <div className="relative z-10 container mx-auto px-4 text-center">
        <AnimatedSection direction="down" delay={200}>
          <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-6 leading-tight">
            Build{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
              {displayText}
            </span>
            <br />
            websites
          </h1>
        </AnimatedSection>

        <AnimatedSection direction="up" delay={400}>
          <p className="text-xl md:text-2xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
            Transform your ideas into stunning digital experiences with our modern 
            platform. Fast, reliable, and built for the future.
          </p>
        </AnimatedSection>

        <AnimatedSection direction="up" delay={600}>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
            <Button
              size="lg"
              className="shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all"
            >
              Get Started Free
            </Button>
            <Button
              variant="secondary"
              size="lg"
              className="border-2 hover:border-gray-300"
            >
              Watch Demo
            </Button>
          </div>
        </AnimatedSection>

        {/* Stats */}
        <AnimatedSection direction="up" delay={800}>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-2xl mx-auto">
            {stats.map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="text-3xl font-bold text-gray-900 mb-2">
                  {stat.number}
                </div>
                <div className="text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </AnimatedSection>
      </div>

      {/* Scroll Indicator */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2">
        <div className="animate-bounce">
          <div className="w-6 h-10 border-2 border-gray-400 rounded-full flex justify-center">
            <div className="w-1 h-3 bg-gray-400 rounded-full mt-2"></div>
          </div>
        </div>
      </div>
    </section>
  );
};

