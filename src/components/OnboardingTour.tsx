import React, { useState, useEffect, useRef } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { X, ChevronRight, ChevronLeft } from 'lucide-react';
import { cn } from '@/lib/utils';

interface TourStep {
  id: string;
  target: string; // CSS selector or element ref
  title: string;
  content: string;
  position?: 'top' | 'bottom' | 'left' | 'right' | 'center';
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface OnboardingTourProps {
  steps: TourStep[];
  onComplete?: () => void;
  onSkip?: () => void;
  storageKey?: string;
}

/**
 * OnboardingTour component for first-time user guidance
 * Guides users through key features with interactive tooltips
 */
export const OnboardingTour: React.FC<OnboardingTourProps> = ({
  steps,
  onComplete,
  onSkip,
  storageKey = 'onboarding_completed',
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isVisible, setIsVisible] = useState(false);
  const [overlayStyles, setOverlayStyles] = useState<React.CSSProperties>({});
  const stepRefs = useRef<(HTMLElement | null)[]>([]);

  useEffect(() => {
    // Check if onboarding was already completed
    const completed = localStorage.getItem(storageKey);
    if (completed === 'true') {
      return;
    }

    // Start tour after a short delay
    const timer = setTimeout(() => {
      setIsVisible(true);
      highlightStep(0);
    }, 500);

    return () => clearTimeout(timer);
  }, [storageKey]);

  const highlightStep = (stepIndex: number) => {
    if (stepIndex < 0 || stepIndex >= steps.length) return;

    const step = steps[stepIndex];
    const element = document.querySelector(step.target) as HTMLElement;

    if (!element) {
      console.warn(`Tour step target not found: ${step.target}`);
      return;
    }

    // Scroll element into view
    element.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'nearest' });

    // Calculate overlay position
    const rect = element.getBoundingClientRect();
    const padding = 8;

    setOverlayStyles({
      top: `${rect.top - padding}px`,
      left: `${rect.left - padding}px`,
      width: `${rect.width + padding * 2}px`,
      height: `${rect.height + padding * 2}px`,
    });

    // Highlight the element
    element.style.zIndex = '1000';
    element.style.transition = 'all 0.3s ease';
    element.style.transform = 'scale(1.02)';
    element.style.boxShadow = '0 0 0 4px rgba(59, 130, 246, 0.5)';
    element.classList.add('ring-4', 'ring-blue-500');

    stepRefs.current[stepIndex] = element;
  };

  const clearHighlight = () => {
    stepRefs.current.forEach((el) => {
      if (el) {
        el.style.zIndex = '';
        el.style.transform = '';
        el.style.boxShadow = '';
        el.classList.remove('ring-4', 'ring-blue-500');
      }
    });
  };

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      clearHighlight();
      const next = currentStep + 1;
      setCurrentStep(next);
      setTimeout(() => highlightStep(next), 100);
    } else {
      completeTour();
    }
  };

  const previousStep = () => {
    if (currentStep > 0) {
      clearHighlight();
      const prev = currentStep - 1;
      setCurrentStep(prev);
      setTimeout(() => highlightStep(prev), 100);
    }
  };

  const skipTour = () => {
    clearHighlight();
    setIsVisible(false);
    localStorage.setItem(storageKey, 'true');
    onSkip?.();
  };

  const completeTour = () => {
    clearHighlight();
    setIsVisible(false);
    localStorage.setItem(storageKey, 'true');
    onComplete?.();
  };

  if (!isVisible || currentStep >= steps.length) return null;

  const step = steps[currentStep];
  const element = document.querySelector(step.target) as HTMLElement;

  if (!element) return null;

  const rect = element.getBoundingClientRect();
  const position = step.position || 'bottom';

  const getTooltipPosition = () => {
    const padding = 16;
    const tooltipWidth = 320;
    const tooltipHeight = 200;

    switch (position) {
      case 'top':
        return {
          top: `${rect.top - tooltipHeight - padding}px`,
          left: `${rect.left + rect.width / 2 - tooltipWidth / 2}px`,
        };
      case 'bottom':
        return {
          top: `${rect.bottom + padding}px`,
          left: `${rect.left + rect.width / 2 - tooltipWidth / 2}px`,
        };
      case 'left':
        return {
          top: `${rect.top + rect.height / 2 - tooltipHeight / 2}px`,
          left: `${rect.left - tooltipWidth - padding}px`,
        };
      case 'right':
        return {
          top: `${rect.top + rect.height / 2 - tooltipHeight / 2}px`,
          left: `${rect.right + padding}px`,
        };
      case 'center':
      default:
        return {
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
        };
    }
  };

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black/50 z-[9998] transition-opacity"
        onClick={skipTour}
        aria-hidden="true"
      />

      {/* Highlight */}
      <div
        className="fixed z-[9999] pointer-events-none border-4 border-blue-500 rounded-lg transition-all"
        style={overlayStyles}
        aria-hidden="true"
      />

      {/* Tooltip */}
      <Card
        className="fixed z-[10000] w-80 p-6 shadow-2xl"
        style={getTooltipPosition()}
        role="dialog"
        aria-labelledby="tour-title"
        aria-describedby="tour-content"
      >
        <div className="flex items-start justify-between mb-4">
          <div>
            <h3 id="tour-title" className="font-semibold text-lg">
              {step.title}
            </h3>
            <p className="text-xs text-muted-foreground mt-1">
              Step {currentStep + 1} of {steps.length}
            </p>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={skipTour}
            className="h-6 w-6"
            aria-label="Skip tour"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        <p id="tour-content" className="text-sm text-muted-foreground mb-4">
          {step.content}
        </p>

        {step.action && (
          <Button
            onClick={() => {
              step.action?.onClick();
              nextStep();
            }}
            className="w-full mb-4"
            size="sm"
          >
            {step.action.label}
          </Button>
        )}

        <div className="flex items-center justify-between">
          <Button
            variant="outline"
            size="sm"
            onClick={previousStep}
            disabled={currentStep === 0}
          >
            <ChevronLeft className="h-4 w-4 mr-1" />
            Previous
          </Button>

          <div className="flex gap-1">
            {steps.map((_, index) => (
              <div
                key={index}
                className={cn(
                  'h-2 w-2 rounded-full transition-all',
                  index === currentStep
                    ? 'bg-primary w-6'
                    : 'bg-muted'
                )}
                aria-label={`Step ${index + 1}`}
              />
            ))}
          </div>

          <Button
            size="sm"
            onClick={nextStep}
          >
            {currentStep === steps.length - 1 ? 'Finish' : 'Next'}
            <ChevronRight className="h-4 w-4 ml-1" />
          </Button>
        </div>
      </Card>
    </>
  );
};

// Hook for creating tour steps easily
export const useOnboardingTour = () => {
  const createTourSteps = (config: {
    uploadStep?: boolean;
    resultsStep?: boolean;
    chatStep?: boolean;
    featuresStep?: boolean;
  }): TourStep[] => {
    const steps: TourStep[] = [];

    if (config.uploadStep) {
      steps.push({
        id: 'upload',
        target: '#image-input',
        title: 'Upload Your Retinal Image',
        content: 'Click here to upload a retinal fundus image. Supported formats: PNG, JPG, JPEG (max 16MB).',
        position: 'right',
      });
    }

    if (config.resultsStep) {
      steps.push({
        id: 'results',
        target: '[data-tour="results"]',
        title: 'View Diagnosis Results',
        content: 'Here you\'ll see the AI analysis results including severity level, confidence scores, and clinical recommendations.',
        position: 'left',
      });
    }

    if (config.chatStep) {
      steps.push({
        id: 'chat',
        target: '[data-tour="chat"]',
        title: 'Ask the AI Assistant',
        content: 'Need help understanding your results? Click here to chat with our AI assistant.',
        position: 'top',
      });
    }

    if (config.featuresStep) {
      steps.push({
        id: 'features',
        target: '[data-tour="features"]',
        title: 'Explore Features',
        content: 'Learn more about RetinaScan AI\'s powerful features and capabilities.',
        position: 'bottom',
      });
    }

    return steps;
  };

  return { createTourSteps };
};

