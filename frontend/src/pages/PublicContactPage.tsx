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
    <div className="min-h-screen bg-black text-white selection:bg-purple-500/30 overflow-x-hidden">
      
      {/* Background Ambience */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-0 w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[120px]" />
      </div>

      <div className="relative pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          {/* Hero Section */}
          <div className="text-center mb-16 relative z-10">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              Have Questions? <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400">
                We're Here to Help
              </span>
            </h1>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              TradeSignal helps retail investors, day traders, and financial analysts track insider trading
              intelligence in real-time. We're here to answer your questions about our platform, pricing,
              or data sources. Get in touch and we'll respond as soon as possible.
            </p>
          </div>

          {/* Mission Statement Section */}
          <div className="max-w-3xl mx-auto mb-12 bg-gradient-to-br from-purple-900/20 to-blue-900/20 border border-white/10 rounded-3xl p-8 text-center relative z-10">
            <h2 className="text-2xl font-bold text-white mb-3">Our Mission</h2>
            <p className="text-gray-400 leading-relaxed">
              We believe financial transparency shouldn't be a luxury—it should be a standard.
              TradeSignal democratizes access to insider trading data by tracking SEC Form 4 filings,
              congressional trades, and institutional flows with LUNA, our advanced AI engine.
            </p>
          </div>

          {/* Main Content - Two Column Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-8 max-w-6xl mx-auto relative z-10">
            {/* Contact Form - Left Side (60%) */}
            <div className="lg:col-span-3">
              <div className="bg-gray-900/50 backdrop-blur-sm border border-white/10 rounded-3xl p-8 shadow-xl">
                <h2 className="text-2xl font-bold text-white mb-6">Send us a message</h2>
                <ContactForm
                  onSubmit={handleSubmit}
                  isSubmitting={isSubmitting}
                  submitStatus={submitStatus}
                />
              </div>
            </div>

            {/* FAQ Section - Right Side (40%) */}
            <div className="lg:col-span-2">
              <div className="bg-gray-900/50 backdrop-blur-sm border border-white/10 rounded-3xl p-8 shadow-xl h-full">
                <FAQSection />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}