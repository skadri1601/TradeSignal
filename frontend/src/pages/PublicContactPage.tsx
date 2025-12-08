import { useState } from 'react';
import ContactForm, { ContactFormData } from '../components/contact/ContactForm';
import FAQSection from '../components/contact/FAQSection';
import { submitPublicContact } from '../api/publicContact';

export default function PublicContactPage() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');

  const handleSubmit = async (data: ContactFormData) => {
    setIsSubmitting(true);
    setSubmitStatus('idle');

    try {
      await submitPublicContact({
        name: data.name,
        company_name: data.company_name || undefined,
        email: data.email,
        phone: data.phone || undefined,
        message: data.message,
      });

      setSubmitStatus('success');
      // Reset form after successful submission
      setTimeout(() => {
        setSubmitStatus('idle');
      }, 5000);
    } catch (error: any) {
      console.error('Contact form error:', error);
      setSubmitStatus('error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Have Questions? We're Here to Help
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Get in touch with our team and we'll respond to you as soon as possible.
          </p>
        </div>

        {/* Main Content - Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8 max-w-6xl mx-auto">
          {/* Contact Form - Left Side (60%) */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-200">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Send us a message</h2>
              <ContactForm
                onSubmit={handleSubmit}
                isSubmitting={isSubmitting}
                submitStatus={submitStatus}
              />
            </div>
          </div>

          {/* FAQ Section - Right Side (40%) */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-200">
              <FAQSection />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
