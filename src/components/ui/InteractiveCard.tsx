import React, { useState } from 'react';

interface InteractiveCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  className?: string;
  hoverEffect?: boolean;
}

export const InteractiveCard: React.FC<InteractiveCardProps> = ({
  children,
  className = '',
  hoverEffect = true,
  ...divProps
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    setMousePosition({ x, y });
  };

  return (
    <div
      className={`
        relative overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm
        transition-all duration-300
        ${hoverEffect ? 'hover:shadow-2xl hover:-translate-y-2' : ''}
        ${className}
      `}
      onMouseEnter={(e) => { setIsHovered(true); divProps.onMouseEnter?.(e); }}
      onMouseLeave={(e) => { setIsHovered(false); divProps.onMouseLeave?.(e); }}
      onMouseMove={(e) => { handleMouseMove(e); divProps.onMouseMove?.(e); }}
      {...divProps}
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

export default InteractiveCard;


