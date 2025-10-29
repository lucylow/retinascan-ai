import React, { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import { cn } from '@/lib/utils';

interface DataMaskProps {
  value: string;
  maskChar?: string;
  revealOn?: 'hover' | 'click' | 'focus';
  className?: string;
  sensitive?: boolean;
  ariaLabel?: string;
}

/**
 * DataMask component for protecting sensitive information
 * Implements privacy by design principles
 */
export const DataMask: React.FC<DataMaskProps> = ({
  value,
  maskChar = '•',
  revealOn = 'hover',
  className,
  sensitive = true,
  ariaLabel,
}) => {
  const [isRevealed, setIsRevealed] = useState(false);
  const [isFocused, setIsFocused] = useState(false);

  if (!sensitive) {
    return <span className={className}>{value}</span>;
  }

  const maskedValue = maskChar.repeat(Math.min(value.length, 8));

  const handleClick = () => {
    if (revealOn === 'click') {
      setIsRevealed(!isRevealed);
    }
  };

  const handleMouseEnter = () => {
    if (revealOn === 'hover') {
      setIsRevealed(true);
    }
  };

  const handleMouseLeave = () => {
    if (revealOn === 'hover') {
      setIsRevealed(false);
    }
  };

  const handleFocus = () => {
    if (revealOn === 'focus') {
      setIsRevealed(true);
      setIsFocused(true);
    }
  };

  const handleBlur = () => {
    if (revealOn === 'focus') {
      setIsRevealed(false);
      setIsFocused(false);
    }
  };

  const showValue = isRevealed || isFocused;

  return (
    <span
      className={cn(
        'inline-flex items-center gap-2 font-mono',
        revealOn === 'click' && 'cursor-pointer',
        className
      )}
      onClick={handleClick}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onFocus={handleFocus}
      onBlur={handleBlur}
      tabIndex={revealOn !== 'hover' ? 0 : undefined}
      role={revealOn === 'click' ? 'button' : undefined}
      aria-label={ariaLabel || (showValue ? `Revealed: ${value}` : 'Masked sensitive data')}
    >
      <span aria-live="polite">
        {showValue ? value : maskedValue}
      </span>
      {revealOn === 'click' && (
        <span className="inline-flex items-center text-muted-foreground">
          {isRevealed ? (
            <EyeOff className="w-4 h-4" />
          ) : (
            <Eye className="w-4 h-4" />
          )}
        </span>
      )}
    </span>
  );
};

/**
 * PatientInfoMask - Specialized component for patient information
 */
interface PatientInfoMaskProps {
  patientId: string;
  patientName?: string;
  revealOn?: 'hover' | 'click' | 'focus';
}

export const PatientInfoMask: React.FC<PatientInfoMaskProps> = ({
  patientId,
  patientName,
  revealOn = 'hover',
}) => {
  return (
    <div className="space-y-2">
      {patientName && (
        <div>
          <span className="text-sm font-medium">Name: </span>
          <DataMask
            value={patientName}
            revealOn={revealOn}
            sensitive
            ariaLabel="Patient name"
          />
        </div>
      )}
      <div>
        <span className="text-sm font-medium">ID: </span>
        <DataMask
          value={patientId}
          revealOn={revealOn}
          sensitive
          ariaLabel="Patient ID"
        />
      </div>
    </div>
  );
};

