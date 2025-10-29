import React, { useState, useEffect, useRef } from 'react';
import { cn } from '@/lib/utils';

interface LazyImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  src: string;
  alt: string;
  placeholder?: string;
  threshold?: number;
  className?: string;
  onLoad?: () => void;
}

/**
 * LazyImage component for performance optimization
 * Loads images only when they enter the viewport
 */
export const LazyImage: React.FC<LazyImageProps> = ({
  src,
  alt,
  placeholder,
  threshold = 0.1,
  className,
  onLoad,
  ...props
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(false);
  const [hasError, setHasError] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsInView(true);
            observer.disconnect();
          }
        });
      },
      { threshold }
    );

    if (containerRef.current) {
      observer.observe(containerRef.current);
    }

    return () => observer.disconnect();
  }, [threshold]);

  useEffect(() => {
    if (isInView && imgRef.current) {
      const img = new Image();
      img.src = src;
      
      img.onload = () => {
        setIsLoaded(true);
        onLoad?.();
      };

      img.onerror = () => {
        setHasError(true);
      };

      // Preload the image
      if (imgRef.current) {
        imgRef.current.src = src;
      }
    }
  }, [isInView, src, onLoad]);

  return (
    <div
      ref={containerRef}
      className={cn('relative overflow-hidden', className)}
      style={{ minHeight: props.height ? `${props.height}px` : '200px' }}
    >
      {!isLoaded && !hasError && (
        <div className="absolute inset-0 flex items-center justify-center bg-muted animate-pulse">
          {placeholder ? (
            <img
              src={placeholder}
              alt=""
              className="w-full h-full object-cover opacity-50"
              aria-hidden="true"
            />
          ) : (
            <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin" />
          )}
        </div>
      )}

      {hasError && (
        <div className="absolute inset-0 flex items-center justify-center bg-muted">
          <span className="text-muted-foreground">Failed to load image</span>
        </div>
      )}

      <img
        ref={imgRef}
        src={isInView ? src : undefined}
        alt={alt}
        className={cn(
          'transition-opacity duration-300',
          isLoaded ? 'opacity-100' : 'opacity-0',
          className
        )}
        loading="lazy"
        {...props}
      />
    </div>
  );
};

