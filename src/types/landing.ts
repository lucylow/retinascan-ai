export interface Feature {
  id: string;
  title: string;
  description: string;
  icon: string;
  color: string;
}

export interface PricingPlan {
  id: string;
  name: string;
  price: number;
  period: string;
  features: string[];
  popular?: boolean;
  cta: string;
}

export interface Testimonial {
  id: string;
  name: string;
  role: string;
  company: string;
  content: string;
  avatar: string;
  rating: number;
}

export interface ContactForm {
  name: string;
  email: string;
  company: string;
  message: string;
  interest: string[];
}

