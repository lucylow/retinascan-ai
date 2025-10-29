import React, { useState } from 'react';

interface InteractiveCardProps {
  children: React.ReactNode;
  className?: string;
  hoverEffect?: boolean;
  onMouseEnter?: () => void;
  onMouseLeave?: () => void;
}

export const InteractiveCard: React.FC<InteractiveCardProps> = ({
  children,
  className = '',
  hoverEffect = true,
  onMouseEnter,
  onMouseLeave,
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    setMousePosition({ x, y });
  };

  const handleMouseEnter = () => {
    setIsHovered(true);
    onMouseEnter?.();
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
    onMouseLeave?.();
  };

  return (
    <div
      className={`
        relative overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm
        transition-all duration-300
        ${hoverEffect ? 'hover:shadow-2xl hover:-translate-y-2' : ''}
        ${className}
      `}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onMouseMove={handleMouseMove}
    >
      {hoverEffect && (
        <div
          className="absolute inset-0 opacity-0 transition-opacity duration-300 pointer-events-none"
          style={{
            background: `
              radial-gradient(
                600px circle at ${mousePosition.x}% ${mousePosition.y}%,
                rgba(59, 130, 246, 0.1),
                transparent 40%
              )
            `,
            opacity: isHovered ? 1 : 0,
          }}
        />
      )}
      <div className="relative z-10">{children}</div>
    </div>
  );
};

