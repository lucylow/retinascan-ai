import React, { useState, useEffect } from 'react';
import { InteractiveCard } from '../ui/InteractiveCard';
import { AnimatedSection } from '../ui/AnimatedSection';
import { Testimonial as TestimonialType } from '../../types/landing';

const testimonials: TestimonialType[] = [
  {
    id: '1',
    name: 'Sarah Johnson',
    role: 'Product Manager',
    company: 'TechCorp',
    content: 'This platform has completely transformed how we build and deploy our applications. The speed and reliability are unmatched.',
    avatar: '👩‍💼',
    rating: 5,
  },
  {
    id: '2',
    name: 'Michael Chen',
    role: 'CTO',
    company: 'StartupXYZ',
    content: 'The ease of use and powerful features helped us launch our product 3x faster than expected. Incredible value!',
    avatar: '👨‍💻',
    rating: 5,
  },
  {
    id: '3',
    name: 'Emily Davis',
    role: 'Design Lead',
    company: 'CreativeStudio',
    content: 'As a designer, I appreciate the attention to detail and the beautiful components. It makes my work shine.',
    avatar: '👩‍🎨',
    rating: 5,
  },
];

export const Testimonials: React.FC = () => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isAutoPlaying, setIsAutoPlaying] = useState(true);

  useEffect(() => {
    if (!isAutoPlaying) return;

    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % testimonials.length);
    }, 5000);

    return () => clearInterval(interval);
  }, [isAutoPlaying]);

  const goToSlide = (index: number) => {
    setCurrentIndex(index);
    setIsAutoPlaying(false);
    setTimeout(() => setIsAutoPlaying(true), 10000);
  };

  const nextSlide = () => {
    setCurrentIndex((prev) => (prev + 1) % testimonials.length);
    setIsAutoPlaying(false);
    setTimeout(() => setIsAutoPlaying(true), 10000);
  };

  const prevSlide = () => {
    setCurrentIndex((prev) => (prev - 1 + testimonials.length) % testimonials.length);
    setIsAutoPlaying(false);
    setTimeout(() => setIsAutoPlaying(true), 10000);
  };

  return (
    <section id="testimonials" className="py-20 bg-white">
      <div className="container mx-auto px-4">
        <AnimatedSection>
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Loved by Thousands
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              See what our customers are saying about their experience
            </p>
          </div>
        </AnimatedSection>

        <div className="max-w-4xl mx-auto">
          {/* Carousel */}
          <div className="relative">
            <div className="overflow-hidden">
              <div
                className="flex transition-transform duration-500 ease-in-out"
                style={{ transform: `translateX(-${currentIndex * 100}%)` }}
              >
                {testimonials.map((testimonial, index) => (
                  <div key={testimonial.id} className="w-full flex-shrink-0 px-4">
                    <AnimatedSection delay={200}>
                      <InteractiveCard className="p-8">
                        <div className="text-center">
                          {/* Rating */}
                          <div className="flex justify-center mb-6">
                            {[...Array(5)].map((_, i) => (
                              <svg
                                key={i}
                                className={`w-6 h-6 ${
                                  i < testimonial.rating
                                    ? 'text-yellow-400'
                                    : 'text-gray-300'
                                }`}
                                fill="currentColor"
                                viewBox="0 0 20 20"
                              >
                                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                              </svg>
                            ))}
                          </div>

                          {/* Content */}
                          <blockquote className="text-xl text-gray-700 mb-8 leading-relaxed">
                            "{testimonial.content}"
                          </blockquote>

                          {/* Author */}
                          <div className="flex items-center justify-center">
                            <div className="text-4xl mr-4">{testimonial.avatar}</div>
                            <div className="text-left">
                              <div className="font-semibold text-gray-900">
                                {testimonial.name}
                              </div>
                              <div className="text-gray-600">
                                {testimonial.role}, {testimonial.company}
                              </div>
                            </div>
                          </div>
                        </div>
                      </InteractiveCard>
                    </AnimatedSection>
                  </div>
                ))}
              </div>
            </div>

            {/* Navigation Buttons */}
            <button
              onClick={prevSlide}
              className="absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-4 bg-white rounded-full p-3 shadow-lg hover:shadow-xl transition-all duration-200 z-10"
              aria-label="Previous testimonial"
            >
              <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>

            <button
              onClick={nextSlide}
              className="absolute right-0 top-1/2 transform -translate-y-1/2 translate-x-4 bg-white rounded-full p-3 shadow-lg hover:shadow-xl transition-all duration-200 z-10"
              aria-label="Next testimonial"
            >
              <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>

          {/* Indicators */}
          <div className="flex justify-center mt-8 space-x-2">
            {testimonials.map((_, index) => (
              <button
                key={index}
                onClick={() => goToSlide(index)}
                className={`w-3 h-3 rounded-full transition-all duration-300 ${
                  index === currentIndex
                    ? 'bg-blue-600 w-8'
                    : 'bg-gray-300 hover:bg-gray-400'
                }`}
                aria-label={`Go to testimonial ${index + 1}`}
              />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

