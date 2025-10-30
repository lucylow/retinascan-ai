import React from 'react';
import { useForm } from '@/hooks/useForm';
import { InteractiveCard } from '@/components/ui/InteractiveCard';
import { AnimatedSection } from '@/components/ui/AnimatedSection';
import { Button } from '@/components/ui/button';

const interests = ['Web Development','Mobile Apps','E-commerce','SEO','UI/UX Design','Other'];

export const Contact: React.FC = () => {
  const { values, errors, touched, isSubmitting, handleChange, handleBlur, handleSubmit } = useForm({
    name: '',
    email: '',
    company: '',
    message: '',
    interest: [],
  });

  const onSubmit = async (formValues: any) => {
    // Simulate API call
    // eslint-disable-next-line no-console
    console.log('Form submitted:', formValues);
    await new Promise(resolve => setTimeout(resolve, 2000));
    // eslint-disable-next-line no-alert
    alert('Thank you for your message! We\'ll get back to you soon.');
  };

  return (
    <section id="contact" className="py-20 bg-gray-900 text-white">
      <div className="container mx-auto px-4">
        <AnimatedSection>
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">Ready to Get Started?</h2>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">Let's discuss your project and see how we can help bring your ideas to life.</p>
          </div>
        </AnimatedSection>

        <div className="max-w-4xl mx-auto">
          <AnimatedSection delay={200}>
            <InteractiveCard className="bg-gray-800 border-gray-700">
              <div className="p-8">
                <form onSubmit={(e) => { e.preventDefault(); handleSubmit(onSubmit); }}>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                    <div>
                      <label htmlFor="name" className="block text-sm font-medium text-gray-300 mb-2">Full Name *</label>
                      <input
                        type="text"
                        id="name"
                        name="name"
                        value={values.name}
                        onChange={handleChange}
                        onBlur={handleBlur}
                        className={`w-full px-4 py-3 rounded-lg bg-gray-700 border text-white placeholder-gray-400 focus:outline-none focus:ring-2 transition-all ${errors.name && touched.name ? 'border-red-500 focus:ring-red-500' : 'border-gray-600 focus:ring-blue-500 focus:border-blue-500'}`}
                        placeholder="Enter your full name"
                      />
                      {errors.name && touched.name && (
                        <p className="mt-1 text-sm text-red-400">{errors.name}</p>
                      )}
                    </div>

                    <div>
                      <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2">Email Address *</label>
                      <input
                        type="email"
                        id="email"
                        name="email"
                        value={values.email}
                        onChange={handleChange}
                        onBlur={handleBlur}
                        className={`w-full px-4 py-3 rounded-lg bg-gray-700 border text-white placeholder-gray-400 focus:outline-none focus:ring-2 transition-all ${errors.email && touched.email ? 'border-red-500 focus:ring-red-500' : 'border-gray-600 focus:ring-blue-500 focus:border-blue-500'}`}
                        placeholder="Enter your email"
                      />
                      {errors.email && touched.email && (
                        <p className="mt-1 text-sm text-red-400">{errors.email}</p>
                      )}
                    </div>
                  </div>

                  <div className="mb-6">
                    <label htmlFor="company" className="block text-sm font-medium text-gray-300 mb-2">Company</label>
                    <input
                      type="text"
                      id="company"
                      name="company"
                      value={values.company}
                      onChange={handleChange}
                      className="w-full px-4 py-3 rounded-lg bg-gray-700 border border-gray-600 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                      placeholder="Enter your company name"
                    />
                  </div>

                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-300 mb-3">Areas of Interest</label>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                      {interests.map((interest) => (
                        <label key={interest} className="flex items-center space-x-3 cursor-pointer group">
                          <input
                            type="checkbox"
                            name="interest"
                            value={interest}
                            checked={values.interest?.includes(interest)}
                            onChange={handleChange}
                            className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500 focus:ring-2"
                          />
                          <span className="text-gray-300 group-hover:text-white transition-colors">{interest}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  <div className="mb-6">
                    <label htmlFor="message" className="block text-sm font-medium text-gray-300 mb-2">Message *</label>
                    <textarea
                      id="message"
                      name="message"
                      value={values.message}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      rows={5}
                      className={`w-full px-4 py-3 rounded-lg bg-gray-700 border text-white placeholder-gray-400 focus:outline-none focus:ring-2 transition-all resize-none ${errors.message && touched.message ? 'border-red-500 focus:ring-red-500' : 'border-gray-600 focus:ring-blue-500 focus:border-blue-500'}`}
                      placeholder="Tell us about your project..."
                    />
                    {errors.message && touched.message && (
                      <p className="mt-1 text-sm text-red-400">{errors.message}</p>
                    )}
                  </div>

                  <Button type="submit" size="lg" className="w-full" disabled={isSubmitting}>
                    {isSubmitting ? (
                      <div className="flex items-center justify-center">
                        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                        Sending...
                      </div>
                    ) : (
                      'Send Message'
                    )}
                  </Button>
                </form>
              </div>
            </InteractiveCard>
          </AnimatedSection>
        </div>
      </div>
    </section>
  );
};

export default Contact;


