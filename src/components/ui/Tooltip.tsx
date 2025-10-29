import React, { useState, useRef, useEffect } from 'react';
import { HelpCircle, Info } from 'lucide-react';

interface TooltipProps {
  children: React.ReactNode;
  content: string;
  position?: 'top' | 'bottom' | 'left' | 'right';
  icon?: 'help' | 'info';
  ariaLabel?: string;
}

export const Tooltip: React.FC<TooltipProps> = ({
  children,
  content,
  position = 'top',
  icon,
  ariaLabel,
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [tooltipPosition, setTooltipPosition] = useState({ top: 0, left: 0 });
  const triggerRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isVisible && triggerRef.current && tooltipRef.current) {
      const triggerRect = triggerRef.current.getBoundingClientRect();
      const tooltipRect = tooltipRef.current.getBoundingClientRect();
      const scrollY = window.scrollY;
      const scrollX = window.scrollX;

      let top = 0;
      let left = 0;

      switch (position) {
        case 'top':
          top = triggerRect.top + scrollY - tooltipRect.height - 8;
          left = triggerRect.left + scrollX + (triggerRect.width - tooltipRect.width) / 2;
          break;
        case 'bottom':
          top = triggerRect.bottom + scrollY + 8;
          left = triggerRect.left + scrollX + (triggerRect.width - tooltipRect.width) / 2;
          break;
        case 'left':
          top = triggerRect.top + scrollY + (triggerRect.height - tooltipRect.height) / 2;
          left = triggerRect.left + scrollX - tooltipRect.width - 8;
          break;
        case 'right':
          top = triggerRect.top + scrollY + (triggerRect.height - tooltipRect.height) / 2;
          left = triggerRect.right + scrollX + 8;
          break;
      }

      // Ensure tooltip stays within viewport
      const padding = 8;
      if (top < scrollY + padding) top = scrollY + padding;
      if (top + tooltipRect.height > scrollY + window.innerHeight - padding) {
        top = scrollY + window.innerHeight - tooltipRect.height - padding;
      }
      if (left < scrollX + padding) left = scrollX + padding;
      if (left + tooltipRect.width > scrollX + window.innerWidth - padding) {
        left = scrollX + window.innerWidth - tooltipRect.width - padding;
      }

      setTooltipPosition({ top, left });
    }
  }, [isVisible, position]);

  const handleMouseEnter = () => setIsVisible(true);
  const handleMouseLeave = () => setIsVisible(false);
  const handleFocus = () => setIsVisible(true);
  const handleBlur = () => setIsVisible(false);

  const positionClasses = {
    top: 'bottom-full left-1/2 transform -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 transform -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 transform -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 transform -translate-y-1/2 ml-2',
  };

  const arrowClasses = {
    top: 'top-full left-1/2 transform -translate-x-1/2 border-t-gray-900',
    bottom: 'bottom-full left-1/2 transform -translate-x-1/2 border-b-gray-900',
    left: 'left-full top-1/2 transform -translate-y-1/2 border-l-gray-900',
    right: 'right-full top-1/2 transform -translate-y-1/2 border-r-gray-900',
  };

  if (icon) {
    const IconComponent = icon === 'help' ? HelpCircle : Info;
    return (
      <div className="inline-flex items-center gap-1">
        {children}
        <div
          ref={triggerRef}
          className="relative inline-flex items-center"
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
          onFocus={handleFocus}
          onBlur={handleBlur}
        >
          <IconComponent
            className="w-4 h-4 text-muted-foreground hover:text-foreground cursor-help"
            aria-label={ariaLabel || content}
            tabIndex={0}
          />
          {isVisible && (
            <div
              ref={tooltipRef}
              className={`absolute z-50 px-3 py-2 text-sm text-white bg-gray-900 rounded-md shadow-lg whitespace-nowrap pointer-events-none ${positionClasses[position]}`}
              role="tooltip"
              aria-hidden={!isVisible}
            >
              {content}
              <div
                className={`absolute w-0 h-0 border-4 border-transparent ${arrowClasses[position]}`}
              />
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div
      ref={triggerRef}
      className="relative inline-block"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onFocus={handleFocus}
      onBlur={handleBlur}
    >
      {children}
      {isVisible && (
        <div
          ref={tooltipRef}
          className={`absolute z-50 px-3 py-2 text-sm text-white bg-gray-900 rounded-md shadow-lg whitespace-nowrap pointer-events-none ${positionClasses[position]}`}
          role="tooltip"
          aria-hidden={!isVisible}
          style={{
            top: `${tooltipPosition.top}px`,
            left: `${tooltipPosition.left}px`,
          }}
        >
          {content}
          <div
            className={`absolute w-0 h-0 border-4 border-transparent ${arrowClasses[position]}`}
          />
        </div>
      )}
    </div>
  );
};

