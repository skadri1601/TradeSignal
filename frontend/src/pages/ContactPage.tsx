import { useState, useEffect } from 'react';
import { Mail, MessageSquare, MapPin } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import ContactForm, { ContactFormData } from '../components/contact/ContactForm';
import apiClient from '../api/client';

export default function ContactPage() {
  const { user } = useAuth();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [initialData, setInitialData] = useState<Partial<ContactFormData>>({});

  useEffect(() => {
    if (user) {
      setInitialData({
        name: user.full_name || user.username || '',
        email: user.email || '',
        phone: user.phone_number || '',
      });
    }
  }, [user]);

  const handleSubmit = async (data: ContactFormData) => {
    setIsSubmitting(true);
    setSubmitStatus('idle');

    try {
      const response = await apiClient.post('/api/v1/contact/', {
        name: data.name,
        company_name: data.company_name || undefined,
        email: data.email,
        phone: data.phone || undefined,
        message: data.message,
      });
      
      if (response.data.success) {
        setSubmitStatus('success');
        // Reset form after successful submission
        setTimeout(() => {
          setSubmitStatus('idle');
        }, 5000);
      } else {
        setSubmitStatus('error');
      }
    } catch (error: any) {
      console.error('Contact form error:', error);
      setSubmitStatus('error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Contact Us</h1>
        <p className="mt-2 text-gray-600">
          Have a question or need help? We're here for you.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Contact Form */}
        <div className="lg:col-span-2">
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Send us a message</h2>
            <ContactForm
              onSubmit={handleSubmit}
              initialData={initialData}
              isSubmitting={isSubmitting}
              submitStatus={submitStatus}
            />
          </div>
        </div>

        {/* Contact Info */}
        <div className="space-y-4">
          <div className="card">
            <h3 className="font-semibold text-gray-900 mb-4">Get in touch</h3>
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <Mail className="h-5 w-5 text-blue-600 mt-0.5" />
                <div>
                  <p className="font-medium text-gray-900">Email</p>
                  <a href="mailto:support@tradesignal.com" className="text-blue-600 hover:underline">
                    support@tradesignal.com
                  </a>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <MessageSquare className="h-5 w-5 text-blue-600 mt-0.5" />
                <div>
                  <p className="font-medium text-gray-900">Response Time</p>
                  <p className="text-gray-600">Within 24 hours</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <MapPin className="h-5 w-5 text-blue-600 mt-0.5" />
                <div>
                  <p className="font-medium text-gray-900">Office</p>
                  <p className="text-gray-600">Dallas, TX, USA</p>
                </div>
              </div>
            </div>
          </div>

          <div className="card bg-blue-50 border-blue-200">
            <h3 className="font-semibold text-gray-900 mb-2">Need immediate help?</h3>
            <p className="text-sm text-gray-700 mb-4">
              For urgent billing or account issues, email us directly at support@tradesignal.com
            </p>
            <a
              href="mailto:support@tradesignal.com"
              className="inline-flex items-center space-x-2 text-blue-600 hover:text-blue-700 font-medium"
            >
              <Mail className="h-4 w-4" />
              <span>Email Support</span>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}

