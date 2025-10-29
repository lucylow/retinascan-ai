import React from 'react';
import { useIntersectionObserver } from '../../hooks/useIntersectionObserver';

interface AnimatedSectionProps {
  children: React.ReactNode;
  className?: string;
  delay?: number;
  direction?: 'up' | 'down' | 'left' | 'right';
}

export const AnimatedSection: React.FC<AnimatedSectionProps> = ({
  children,
  className = '',
  delay = 0,
  direction = 'up',
}) => {
  const { ref, hasAnimated } = useIntersectionObserver(0.1);

  const getTransform = () => {
    switch (direction) {
      case 'up': return 'translateY(30px)';
      case 'down': return 'translateY(-30px)';
      case 'left': return 'translateX(30px)';
      case 'right': return 'translateX(-30px)';
      default: return 'translateY(30px)';
    }
  };

  return (
    <div
      ref={ref}
      className={`transition-all duration-700 ease-out ${
        hasAnimated
          ? 'opacity-100 transform translate-x-0 translate-y-0'
          : 'opacity-0'
      } ${className}`}
      style={{
        transform: hasAnimated ? 'none' : getTransform(),
        transitionDelay: hasAnimated ? `${delay}ms` : '0ms',
      }}
    >
      {children}
    </div>
  );
};

